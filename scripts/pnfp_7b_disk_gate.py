"""Read-only, fail-closed disk admission check; never generates logits or deletes files.

Run on the data-disk host immediately before each stage. Components describe
ADDITIONAL simultaneously resident bytes (including final save, temporary copies,
datasets, caches, and metadata), not artifacts already included in disk.used.
Full-vocabulary BF16 targets are the only supported Bc representation.
"""
import argparse
import datetime
import json
import shutil
from pathlib import Path


def budget(total, used, free, components, *, samples=0, sequence_length=1024,
           vocabulary_size=32000, supervised_tokens=None):
    if min(total, used, free, samples) < 0 or min(sequence_length, vocabulary_size) <= 0:
        raise ValueError('Invalid disk or tensor dimensions')
    if not components or any(type(v) is not int or v < 0 for v in components.values()):
        raise ValueError('Explicit nonnegative integer component byte estimates required')
    if supervised_tokens is not None and not 0 <= supervised_tokens <= samples * sequence_length:
        raise ValueError('Invalid exact supervised token count')
    tokens = samples * sequence_length if supervised_tokens is None else supervised_tokens
    logit_bytes = tokens * vocabulary_size * 2
    extra = sum(components.values()) + logit_bytes
    limit = free * 85 // 100
    return dict(total_bytes=total, current_used_bytes=used, current_free_bytes=free,
                additional_components_bytes=components,
                logits=dict(sample_count=samples, sequence_length=sequence_length,
                            vocabulary_size=vocabulary_size, dtype='bfloat16', bytes_per_value=2,
                            representation='full_vocab', stored_positions=tokens,
                            estimate_kind='upper_bound' if supervised_tokens is None else 'exact_masked_positions',
                            payload_bytes=logit_bytes),
                additional_peak_bytes=extra, projected_used_peak_bytes=used + extra,
                maximum_additional_bytes=limit, reserved_free_fraction=0.15,
                passed=extra <= limit and used + extra <= total)


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--disk-path', required=True)
    p.add_argument('--stage', required=True)
    p.add_argument('--components-json', required=True,
                   help='Reviewed mapping of additional peak allocations to bytes; include overhead')
    p.add_argument('--samples', type=int, default=0)
    p.add_argument('--sequence-length', type=int, default=1024)
    p.add_argument('--vocabulary-size', type=int, default=32000)
    p.add_argument('--supervised-tokens', type=int)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    disk = shutil.disk_usage(a.disk_path)
    result = budget(*disk, json.loads(Path(a.components_json).read_text(encoding='utf-8')),
                    samples=a.samples, sequence_length=a.sequence_length,
                    vocabulary_size=a.vocabulary_size, supervised_tokens=a.supervised_tokens)
    result.update(stage=a.stage, disk_path=str(Path(a.disk_path).resolve()),
                  timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat())
    Path(a.output).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    raise SystemExit(0 if result['passed'] else 2)


if __name__ == '__main__':
    main()
