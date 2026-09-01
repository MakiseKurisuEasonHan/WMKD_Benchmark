"""Frozen dual gray-box detectors for LLMPrint Experiment A and Ba."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import fmean, pstdev, stdev


Z_SCORE = 1.64
RELEASE_PROB_THRESHOLD = 1e-3


def bits(sequence, *, inclusive: bool) -> list[int]:
    return [int(pos >= neg if inclusive else pos > neg) for pos, neg in sequence]


def paper_model(reference, compare) -> dict:
    if len(reference) != len(compare) or not reference:
        raise ValueError("paper detector requires equal non-empty sequences")
    reference_bits = bits(reference, inclusive=True)
    compare_bits = bits(compare, inclusive=True)
    matches = [int(left == right) for left, right in zip(reference_bits, compare_bits)]
    return {
        "reference_bits": reference_bits,
        "compare_bits": compare_bits,
        "matches": matches,
        "match_count": sum(matches),
        "total": len(matches),
        "accuracy": sum(matches) / len(matches),
    }


def calibrate_paper(reference, negatives: dict[str, list]) -> dict:
    if not negatives:
        raise ValueError("paper calibration requires validation negatives")
    models = {name: paper_model(reference, seq) for name, seq in negatives.items()}
    accuracies = [row["accuracy"] for row in models.values()]
    mu = fmean(accuracies)
    sample_sigma = stdev(accuracies) if len(accuracies) > 1 else 0.0
    population_sigma = pstdev(accuracies)
    raw_tau = mu + Z_SCORE * sample_sigma
    return {
        "detector": "PRIMARY_PAPER_GRAYBOX",
        "comparison": ">=",
        "ddof": 1,
        "z": Z_SCORE,
        "mu": mu,
        "population_sigma_ddof0": population_sigma,
        "sample_sigma_ddof1": sample_sigma,
        "population_sigma_ddof0_supplementary": population_sigma,
        "raw_tau": raw_tau,
        "tau_clipped": False,
        "final_tau": raw_tau,
        "positive_condition": "accuracy >= final_tau",
        "models": models,
    }


def exact_binomial_greater(successes: int, trials: int) -> float:
    if trials <= 0:
        return 1.0
    return sum(math.comb(trials, k) for k in range(successes, trials + 1)) / (2**trials)


def release_model(reference, compare, *, min_n: int = 0) -> dict:
    if len(reference) != len(compare):
        raise ValueError("release detector requires equal-length sequences")
    filtered_indices = [
        index
        for index, ((ref_pos, ref_neg), (cmp_pos, cmp_neg)) in enumerate(zip(reference, compare))
        if min(ref_pos, ref_neg) > RELEASE_PROB_THRESHOLD
        and min(cmp_pos, cmp_neg) > RELEASE_PROB_THRESHOLD
    ]
    reference_bits = [int(reference[index][0] > reference[index][1]) for index in filtered_indices]
    compare_bits = [int(compare[index][0] > compare[index][1]) for index in filtered_indices]
    correct_bits = sum(left == right for left, right in zip(reference_bits, compare_bits))
    valid_n = len(filtered_indices)
    pvalue = exact_binomial_greater(correct_bits, valid_n)
    return {
        "filtered_indices": filtered_indices,
        "reference_bits": reference_bits,
        "compare_bits": compare_bits,
        "valid_n": valid_n,
        "correct_bits": correct_bits,
        "filtered_accuracy": correct_bits / valid_n if valid_n else None,
        "exact_binomial_pvalue_greater": pvalue,
        "calibrated_min_n": min_n,
        "positive": pvalue < 0.05 and valid_n >= min_n,
    }


def calibrate_release(reference, negatives: dict[str, list]) -> dict:
    preliminary = {name: release_model(reference, seq) for name, seq in negatives.items()}
    usable = [row["valid_n"] for row in preliminary.values() if row["valid_n"] > 0]
    min_n = max(usable) if len(usable) >= 3 else 0
    return {
        "detector": "SUPPLEMENTARY_RELEASE_GRAYBOX",
        "probability_threshold": RELEASE_PROB_THRESHOLD,
        "probability_condition": "strictly greater than threshold for all four probabilities",
        "bit_comparison": ">",
        "pvalue_condition": "one-sided exact binomial p < 0.05",
        "min_n_rule": "maximum positive valid_n among usable validation negatives; 0 if fewer than 3",
        "calibrated_min_n": min_n,
        "models": {name: release_model(reference, seq, min_n=min_n) for name, seq in negatives.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    reference = payload["reference_sequence"]
    negatives = payload["validation_negative_sequences"]
    result = {
        "schema_version": "wmkd.llmprint-dual-detector.v1",
        "primary": calibrate_paper(reference, negatives),
        "supplementary": calibrate_release(reference, negatives),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
