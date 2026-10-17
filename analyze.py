
# Historical breakdown analysis for KM-Waechter.
# Compare breakdown groups before ranking vehicles.
# Risk scores prioritize inspections; they are not breakdown probabilities.

from pathlib import Path

import numpy as np
import pandas as pd

HISTORY_FILE = Path(__file__).with_name("fleet_history.csv")

RISK_WEIGHTS = {
    "km_since_service": 0.50,
    "avg_daily_km": 0.30,
    "load_factor": 0.20,
}

FEATURES = [
    "odometer_km",
    "km_since_service",
    "avg_daily_km",
    "load_factor",
    "age_years",
]


def numeric_array(values) -> np.ndarray:
    """Convert values to a float array, replacing invalid values with NaN."""
    converted = pd.to_numeric(values, errors="coerce")
    return np.asarray(converted, dtype=np.float64)


def analyze_history(path=HISTORY_FILE):
    """Compare breakdown groups and calculate relative vehicle risk."""
    df = pd.read_csv(path)

    required = ["car_id", "broke_down", *FEATURES]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in fleet_history.csv: {missing}")

    if df.empty:
        raise ValueError("fleet_history.csv contains no records.")

    outcomes = numeric_array(df["broke_down"])

    if not np.isfinite(outcomes).all():
        raise ValueError("broke_down contains missing or invalid values.")

    if not np.isin(outcomes, [0.0, 1.0]).all():
        raise ValueError("broke_down must contain only 0 or 1.")

    rows = []

    for column in FEATURES:
        values = numeric_array(df[column])

        no_breakdown = values[(outcomes == 0) & np.isfinite(values)]
        breakdown = values[(outcomes == 1) & np.isfinite(values)]

        no_breakdown_mean = (
            float(np.mean(no_breakdown))
            if no_breakdown.size
            else float("nan")
        )
        breakdown_mean = (
            float(np.mean(breakdown))
            if breakdown.size
            else float("nan")
        )

        valid = np.isfinite(values)
        x = values[valid]
        y = outcomes[valid]

        correlation = 0.0
        if x.size > 1 and np.std(x) > 0 and np.std(y) > 0:
            result = float(np.corrcoef(x, y)[0, 1])
            if np.isfinite(result):
                correlation = result

        difference = (
            breakdown_mean - no_breakdown_mean
            if np.isfinite(breakdown_mean)
            and np.isfinite(no_breakdown_mean)
            else float("nan")
        )

        rows.append({
            "factor": column,
            "no_breakdown_mean": no_breakdown_mean,
            "breakdown_mean": breakdown_mean,
            "difference": difference,
            "correlation": correlation,
            "absolute_correlation": abs(correlation),
        })

    comparison = pd.DataFrame(rows).sort_values(
        "absolute_correlation",
        ascending=False,
    )

    ranked = df.copy()
    score = np.zeros(len(ranked), dtype=np.float64)

    for column, weight in RISK_WEIGHTS.items():
        values = numeric_array(ranked[column])
        valid = np.isfinite(values)
        percentiles = np.zeros(len(ranked), dtype=np.float64)

        if valid.any():
            valid_values = values[valid]
            order = np.argsort(valid_values, kind="stable")
            sorted_values = valid_values[order]
            ranks = np.empty(len(sorted_values), dtype=np.float64)

            start = 0
            while start < len(sorted_values):
                end = start + 1
                while (
                    end < len(sorted_values)
                    and sorted_values[end] == sorted_values[start]
                ):
                    end += 1

                # Average rank for tied values, scaled to 0..1.
                average_rank = ((start + 1) + end) / 2
                ranks[start:end] = average_rank / len(sorted_values)
                start = end

            original_ranks = np.empty_like(ranks)
            original_ranks[order] = ranks
            percentiles[np.flatnonzero(valid)] = original_ranks

        score += percentiles * weight * 100

    ranked["risk_score"] = np.round(score, 1)
    ranked["risk_band"] = pd.cut(
        ranked["risk_score"],
        bins=[-0.1, 40, 70, 100],
        labels=["LOW", "MEDIUM", "HIGH"],
        include_lowest=True,
    )

    ranked = ranked.sort_values("risk_score", ascending=False)

    return comparison, ranked


def main():
    comparison, ranked = analyze_history()

    print("FEATURE COMPARISON")
    print(
        comparison.to_string(
            index=False,
            float_format=lambda value: f"{value:.3f}",
        )
    )

    print("\nALL CARS RANKED BY RELATIVE BREAKDOWN RISK")

    columns = [
        "car_id",
        "km_since_service",
        "avg_daily_km",
        "load_factor",
        "risk_score",
        "risk_band",
        "broke_down",
    ]

    print(ranked[columns].to_string(index=False))

    print("\nInterpretation:")
    print(
        "Feature correlations show historical associations, "
        "not proof of causation."
    )
    print(
        "Risk scores prioritize inspections; "
        "they are not probabilities of breakdown."
    )


if __name__ == "__main__":
    main()
