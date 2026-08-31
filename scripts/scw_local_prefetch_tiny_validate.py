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
    args = parser.parse_args()
    source = Path(args.official_source).resolve()
    sys.path.insert(0, str(source / "src"))

    import pyarrow.parquet as pq
    from robust_fp.config import MainConfiguration
    from robust_fp.finetuning.data_utils import add_chat_template
    from robust_fp.finetuning.dataset import group_texts, tokenize_function
    from scw_materialized_stream import normalize_official_record
    from transformers import AutoTokenizer

    runtime = MainConfiguration.parse_yaml(args.official_runtime_config)
    ft = runtime.finetuning_config
    tokenizer = AutoTokenizer.from_pretrained(ft.base_model, padding_side="left")
    if tokenizer.chat_template is None:
        tokenizer = add_chat_template(tokenizer)
    parquet = pq.ParquetFile(args.parquet)
    batch = next(parquet.iter_batches(batch_size=32, columns=["text"]))
    texts = batch.column(0).to_pylist()
    tokenized = tokenize_function({"text": texts}, tokenizer)
    grouped = group_texts(tokenized, ft.sequence_length)
    if not grouped["input_ids"]:
        raise RuntimeError("official preprocessing produced no packed records")
    records = []
    for index, (input_ids, attention_mask) in enumerate(zip(grouped["input_ids"][:8], grouped["attention_mask"][:8])):
        records.append(normalize_official_record({"input_ids": input_ids, "attention_mask": attention_mask, "labels": 0}, index))
    if not records or any(row["source_dataset"] != "LucieFr" or row["loss_type"] != "watermark" for row in records):
        raise RuntimeError("LucieFr source/loss mapping validation failed")
    print(json.dumps({
        "status": "PASS",
        "classification": "NON_SCIENTIFIC_LOCAL_PREFETCH_VALIDATION",
        "input_rows": len(texts),
        "tokenized_records": len(records),
        "sequence_length": ft.sequence_length,
        "source_dataset": "LucieFr",
        "label_id": 0,
        "loss_type": "watermark",
        "official_functions": ["tokenize_function", "group_texts"],
    }, indent=2))


if __name__ == "__main__":
    main()
