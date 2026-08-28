# Large Model Artifact Transfer Protocol

1. Identify canonical final-model files and record every relative path, byte count and SHA256 in an immutable source manifest.
2. Upload canonical files and small metadata to the approved private ModelScope repository.
3. Verify remote filenames, file count, individual sizes and ModelScope blob/content consistency when available.
4. Record `uploaded_to_modelscope_awaiting_destination_hash_verification` at this point. Do not normally re-download the full model to the same source host solely for verification.
5. When the artifact reaches its real destination, recompute every SHA256 there and compare it with the immutable source manifest.
6. Only after that comparison passes may the destination be marked `destination_verified`.

PN-FP A2 followed the source/upload checks and remained awaiting destination verification. PN-FP Ba additionally performed a valid full authenticated same-host remote re-read, but that stronger check added approximately 37.6 minutes and is not the default future requirement.
