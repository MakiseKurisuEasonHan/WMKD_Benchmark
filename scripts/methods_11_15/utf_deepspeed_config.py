"""Materialize HF 4.44 hidden-size resource buckets for DeepSpeed integer schema.

Only the fractional prefetch expression needs truncation. Other two expressions
are already integers. No optimizer, offload, batch, or scientific fields change.
"""
import copy


def materialize(config, hidden_size):
    assert type(hidden_size) is int and hidden_size > 0
    result = copy.deepcopy(config)
    zero = result['zero_optimization']
    values = {
        'reduce_bucket_size': hidden_size * hidden_size,
        'stage3_prefetch_bucket_size': int(0.9 * hidden_size * hidden_size),
        'stage3_param_persistence_threshold': 10 * hidden_size,
    }
    for key, value in values.items():
        if zero.get(key) == 'auto':
            zero[key] = value
        assert type(zero[key]) is int, (key, zero[key])
    return result


def regression_check():
    original = {'zero_optimization': {'stage': 3,
        'reduce_bucket_size': 'auto', 'stage3_prefetch_bucket_size': 'auto',
        'stage3_param_persistence_threshold': 'auto',
        'offload_optimizer': {'device': 'cpu'}}, 'optimizer': {'type': 'Adam'}}
    fixed = materialize(original, 4096)
    assert fixed['zero_optimization']['stage3_prefetch_bucket_size'] == 15099494
    assert fixed['zero_optimization']['reduce_bucket_size'] == 16777216
    assert fixed['zero_optimization']['stage3_param_persistence_threshold'] == 40960
    assert materialize(fixed, 4096) == fixed
    assert original['zero_optimization']['stage3_prefetch_bucket_size'] == 'auto'
    assert fixed['optimizer'] == original['optimizer']
    assert fixed['zero_optimization']['offload_optimizer'] == original['zero_optimization']['offload_optimizer']
    assert fixed['zero_optimization']['stage'] == 3


if __name__ == '__main__':
    regression_check()
    print('UTF DeepSpeed bucket regression PASS')
