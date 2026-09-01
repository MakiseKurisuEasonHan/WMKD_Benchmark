# SCW materialized-stream runtime adaptation

> Historical strict-A engineering record. This path was superseded by the explicitly approved A2 domestic-data adaptation; SCW A2/Ba are now FULLY CLOSED. Statements below that prohibit Ba describe the strict-A decision boundary at that historical time and are not current project status.

## Status and classification

Local research and synthetic validation support **`RUNTIME_DATA_ACCESS_ADAPTATION`**, not SCW A2. Formal A and Ba remain NOT RUN. The classification is conditional on the future AutoDL materialization/audit/gate preserving the exact post-interleave finite stream described below.

## Pinned implementation findings

Official source is `eth-sri/robust-llm-fingerprints@15bc1929569357130f2dbc0b09f91bbf4f4bd947`, tracked clean. Relevant implementation locations are:

- `src/robust_fp/finetuning/dataset.py`: dataset loading, raw transforms, tokenization/chat templating, 512-token packing, and column selection.
- `src/robust_fp/finetuning/finetune.py:44-112`: per-source labeling/shuffle and final `interleave_datasets` call.
- `src/robust_fp/finetuning/data_utils.py`: Alpaca conversion, response-length filter, chat-template tokenization, and padding.
- `src/robust_fp/finetuning/losses.py`: label ID to lambda/loss mapping.
- `src/robust_fp/finetuning/dmwm_trainer.py`: label-driven watermark versus anti-watermark-TV loss dispatch.
- `src/robust_fp/finetuning/finetune.py:179-190`: `DomainWatermarkTrainer` construction and stopping through Transformers `max_steps`.

Streaming is an implementation/storage convenience for very large sources and incremental preprocessing, not an expressed scientific requirement. It does, however, participate in the realized sample sequence: IterableDataset shuffle is buffered/shard-aware, and probabilistic interleave consumes the iterable outputs. Consequently, switching to `streaming=False` and re-interleaving is not accepted as exact.

Each source is preprocessed before interleave. LucieFr and OpenWebText tokenize raw `text`, concatenate batched token lists, drop the remainder below 512 within each map batch, and emit 512-token chunks. AlpacaGPT4 maps instruction/output to messages, rejects assistant responses shorter than 200 characters, applies the model chat template with `max_length=512` and `padding=max_length`, then retains `input_ids` and `attention_mask`. The official code then assigns label IDs and shuffles each resulting source.

With `PYTHONHASHSEED=42`, per-source shuffle seeds are `hash(DatasetType) % 2**sys.hash_info.width`; the final interleave seed is `hash(finetuning_config.short_str()) % 2**sys.hash_info.width`. For WMKD's runtime config, `short_str()` is the fixed custom name `French_WMKD_SCW_A`. Python hash therefore directly affects source order and probabilistic source selection. No Python `random`, Torch RNG, or independent NumPy seed is selected by this data code beyond the integer seeds passed to Hugging Face Datasets.

The final combination is probabilistic weighted interleave with probabilities 0.6/0.2/0.2, not round-robin and not a fixed-count rebalance. `stopping_strategy="all_exhausted"` oversamples/restarts an exhausted source until every source has been exhausted at least once. The finite 160,000-record training prefix ends far before full exhaustion is expected; observed source proportions are stochastic and must be recorded rather than forced to exact 60/20/20.

Map-style and iterable interleave are not treated as interchangeable. Although both use the requested probabilities/seed and `all_exhausted` concept, iterable execution adds streaming shuffle buffers, shards, worker/process sharding, restart state, and iterator-specific exhaustion behavior. The adaptation therefore enumerates the actual official streaming result rather than reconstructing it with a map-style dataset.

## Exact finite-stream contract

Single-GPU formal training uses 2,500 optimizer steps × 16 gradient-accumulation microbatches × per-device batch 4 = **40,000 microbatches and exactly 160,000 consumed tokenized examples**. `max_steps` overrides epoch completion. With the fixed single process, default zero DataLoader workers, full batches available, and a source stream much longer than this prefix, no extra safety records are required. A future runtime preflight must fail if those assumptions change.

Materialization occurs after official preprocessing, per-source shuffle, source label assignment, and probabilistic interleave, but before Trainer/DataLoader batching. Each JSONL record freezes global index, `input_ids`, `attention_mask`, official label ID, source dataset, role, loss type, lambda, and a content hash. This is the earliest layer that preserves the exact realized training sequence without re-running random/shard/packing behavior during Formal A. Raw source row IDs are no longer available at this point because official preprocessing removes them; the manifest states this limitation. Source/loss identity remains exact because the fixed official label IDs are one-to-one with LucieFr/watermark, AlpacaGPT4/anti-watermark-TV, and OpenWebText/anti-watermark-TV.

Duplicates are preserved occurrence-for-occurrence. There is no deduplication, source rebalance, manual round-robin, or record replacement. The immutable manifest records repository/model/dataset revisions, `PYTHONHASHSEED`, computed shuffle/interleave seeds, probabilities, stopping strategy, training-length contract, record/source counts, observed proportions, file size/SHA256, ordered content digest, code version, timestamp, schema, and limitations.

Formal training uses a PyTorch-only sequential `IterableDataset` over the frozen local JSONL. It verifies file SHA256, every record hash/index/source/loss mapping, count, and training arguments before exposing only official model inputs (`input_ids`, `attention_mask`, scalar `labels`). It deliberately avoids a map-style dataset because Transformers would otherwise install a random sampler and change order. The wrapper replaces only the official in-memory data-loading function; official model, trainer, losses, optimizer, scheduler, tokenizer/model setup, and source checkout remain unchanged.

## Equivalence statement and remaining gate

The proposal can provide exact equivalence **between the enumerated official streaming prefix and the frozen local prefix**: byte-identical token/mask/label values in identical global order. It cannot claim identity with an earlier historical run unless that historical prefix was recorded; the future materialization creates the canonical Formal A stream using the already fixed revisions, runtime, hashes, and official implementation.

Scientific safety remains conditional on future AutoDL Stage A/B audit and a four-step local-materialized clean-exit gate. If real materialization cannot reproduce itself under identical seeds, yields other than 160,000 records, changes Trainer consumption, or fails any hash/label/order audit, Formal A must remain blocked and the classification becomes `MATERIALIZATION_NOT_SCIENTIFICALLY_SAFE`.

## Prepared future sequence (not executed)

1. Generate exactly 160,000 post-interleave official records with pinned revisions and `PYTHONHASHSEED=42`.
2. Freeze JSONL and manifest; independently audit file/content hashes, indices, source/loss mapping, counts, and observed proportions.
3. Run one four-step gate through the local sequential loader and require 4/4, `train_end`, subprocess/outer exit 0, and clean interpreter shutdown.
4. Only if the gate passes, launch Formal A 2,500 steps with the same frozen stream.
5. Fresh reload, detector, utility, report, and shutdown follow the existing protocol. Ba remains prohibited.
