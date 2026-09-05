# CTCC Experiment Bb — formal blocked closure

Run `ctcc_bb_20260904_055000` has status **BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE**. Under the frozen standardized Bb preprocessing protocol, CTCC exceeded the predefined identity-fallback acceptance limit (202 > 200), so the experiment was blocked before Student training.

Parent provenance and frozen Qwen/protocol identity are preserved in the full experiment log. At the gate there were `17269` resolved records and `18264` journal rows. The threshold was neither modified nor tuned. This is not a watermark failure, detector failure, Student-training failure, or Qwen scientific failure.

Student training, detector, and utility were not run. All attempts, journal, progress artifacts, and failure evidence remain in place; no canonical artifact was deleted.

Reason: Frozen standardized Bb preprocessing identity-fallback acceptance gate exceeded: 202 > 200; threshold unchanged and no downstream execution.

## Protocol, provenance, and bounded closure

Objective was frozen proactive Bb preprocessing on CTCC Ba parent `ctcc_ba_generation_20260829_195943_cont1` before fresh-Student distillation and frozen evaluation. The parent has 20,000 records with dataset/file SHA `621c9aed...12484` / `4cc5943d...f4c6`.

The run resolved 17,269 records and preserved 18,264 journal rows. At fallback 202 versus limit 200 it failed closed. Student training, telemetry, detector, utility, processed20k archive, and Student archive are `NOT_RUN`/unavailable. Environment, frozen prompt/config hashes, journal/failure-log SHA, artifacts, and limitation remain in the canonical full log. No Bb2 result is borrowed.

Bounded conclusion: this is a preprocessing acceptance-gate block, not a watermark, Student, detector, utility, or Qwen scientific failure.
