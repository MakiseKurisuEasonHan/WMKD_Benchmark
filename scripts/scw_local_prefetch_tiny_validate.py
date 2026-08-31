"""Non-scientific tiny validation of official SCW preprocessing on local Parquet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official-source", required=True)
    parser.add_argument("--official-runtime-config", required=True)
    parser.add_argument("--parquet", required=True)
    parser.add_argument("--source", required=True, choices=("LucieFr", "AlpacaGPT4", "OpenWebText"))
    args = parser.parse_args()
    source = Path(args.official_source).resolve()
    sys.path.insert(0, str(source / "src"))

    import pyarrow.parquet as pq
    from robust_fp.config import MainConfiguration
    from datasets import Dataset
    from robust_fp.finetuning.data_utils import add_chat_template, convert_sft_dataset, tokenize_dataset_with_chat
    from robust_fp.finetuning.dataset import group_texts, tokenize_function
    from scw_materialized_stream import normalize_official_record
    from transformers import AutoTokenizer

    runtime = MainConfiguration.parse_yaml(args.official_runtime_config)
    ft = runtime.finetuning_config
    tokenizer = AutoTokenizer.from_pretrained(ft.base_model, padding_side="left")
    if tokenizer.chat_template is None:
        tokenizer = add_chat_template(tokenizer)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    parquet = pq.ParquetFile(args.parquet)
    source_contract = {
        "LucieFr": (0, "watermark"), "AlpacaGPT4": (1, "anti-watermark-tv"),
        "OpenWebText": (2, "anti-watermark-tv"),
    }
    label_id, expected_loss = source_contract[args.source]
    if args.source == "AlpacaGPT4":
        batch = next(parquet.iter_batches(batch_size=128, columns=["instruction", "output"]))
        values = batch.to_pydict()
        dataset = Dataset.from_dict(values)
        dataset = convert_sft_dataset(
            dataset,
            convert_fn=lambda example: {"messages": [
                {"role": "user", "content": example["instruction"]},
                {"role": "assistant", "content": example["output"]},
            ]},
            min_response_length=200,
        )
        tokenized_dataset = tokenize_dataset_with_chat(dataset, tokenizer, max_length=ft.sequence_length)
        examples = [tokenized_dataset[index] for index in range(min(8, len(tokenized_dataset)))]
        input_rows = len(values["instruction"])
        official_functions = ["convert_sft_dataset", "tokenize_dataset_with_chat"]
    else:
        batch = next(parquet.iter_batches(batch_size=32, columns=["text"]))
        texts = batch.column(0).to_pylist()
        tokenized = tokenize_function({"text": texts}, tokenizer)
        grouped = group_texts(tokenized, ft.sequence_length)
        examples = [
            {"input_ids": input_ids, "attention_mask": attention_mask}
            for input_ids, attention_mask in zip(grouped["input_ids"][:8], grouped["attention_mask"][:8])
        ]
        input_rows = len(texts)
        official_functions = ["tokenize_function", "group_texts"]
    if not examples:
        raise RuntimeError("official preprocessing produced no tokenized records")
    records = [
        normalize_official_record({**example, "labels": label_id}, index)
        for index, example in enumerate(examples)
    ]
    if any(row["source_dataset"] != args.source or row["loss_type"] != expected_loss for row in records):
        raise RuntimeError(f"{args.source} source/loss mapping validation failed")
    print(json.dumps({
        "status": "PASS",
        "classification": "NON_SCIENTIFIC_LOCAL_PREFETCH_VALIDATION",
        "input_rows": input_rows,
        "tokenized_records": len(records),
        "sequence_length": ft.sequence_length,
        "source_dataset": args.source,
        "label_id": label_id,
        "loss_type": expected_loss,
        "official_functions": official_functions,
    }, indent=2))


if __name__ == "__main__":
    main()
