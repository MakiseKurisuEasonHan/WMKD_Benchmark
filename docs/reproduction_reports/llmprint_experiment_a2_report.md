# LLMPrint Experiment A2 formal closure report

## Outcome

**Terminal status: BLOCKED. Scientific reproduction was not judged.**

- Immutable fingerprint package: 200/200 PASS; no regeneration or overwrite.
- Canonical Reference fresh reload: PASS.
- Frozen validation negatives evaluated: 6/13, each with an atomic 200-record sequence.
- Primary paper detector: not calibrated because the frozen panel is incomplete.
- Supplementary release detector: not calibrated because the frozen panel is incomplete.
- Preferred fingerprint: no scientific preference decision; no Teacher checkpoint exists.
- Ba: NOT STARTED.

## Blocker

Slot 7 requires `microsoft/phi-2@1650c3d781609187dc5133d1baf8fdf2921b874b`. That revision is absent from the ModelScope blob-revision set. A direct `resolve/<hash>` request silently returns current master content, demonstrated by the identical ETag. Using it would violate the frozen-panel rule. No replacement, master fallback, panel change, or tuning was performed.
