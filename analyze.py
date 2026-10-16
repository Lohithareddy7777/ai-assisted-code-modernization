
# Historical breakdown analysis for KM-Waechter.
# Compare actual breakdown groups before ranking vehicles.
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


def analyze_history(path=HISTORY_FILE):
    """Compare breakdown groups and calculate relative vehicle risk."""
    df = pd.read_csv(path)

    required = ["car_id", "broke_down", *FEATURES]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in fleet_history.csv: {missing}")

    if df.empty:
        raise ValueError("fleet_history.csv contains no records.")

    # Validate breakdown outcomes.
    outcome_series = pd.to_numeric(df["broke_down"], errors="coerce")
    outcome_array = np.asarray(outcome_series, dtype=np.float64)

    if not np.isfinite(outcome_array).all():
        raise ValueError("broke_down contains missing or invalid values.")

    if not np.isin(outcome_array, [0.0, 1.0]).all():
        raise ValueError("broke_down must contain only 0 or 1.")

    # Compare feature averages and correlations.
    rows = []

    for column in FEATURES:
        feature_series = pd.to_numeric(df[column], errors="coerce")
        feature_array = np.asarray(feature_series, dtype=np.float64)

        no_breakdown_mask = (
            (outcome_array == 0) & np.isfinite(feature_array)
        )
        breakdown_mask = (
            (outcome_array == 1) & np.isfinite(feature_array)
        )

        no_breakdown_values = feature_array[no_breakdown_mask]
        breakdown_values = feature_array[breakdown_mask]

        no_breakdown_mean = (
            float(np.mean(no_breakdown_values))
            if no_breakdown_values.size > 0
            else float("nan")
        )

        breakdown_mean = (
            float(np.mean(breakdown_values))
            if breakdown_values.size > 0
            else float("nan")
        )

        valid_mask = (
            np.isfinite(feature_array) & np.isfinite(outcome_array)
        )
        x = feature_array[valid_mask]
        y = outcome_array[valid_mask]

        correlation = 0.0

        if x.size > 1 and np.std(x) > 0 and np.std(y) > 0:
            value = float(np.corrcoef(x, y)[0, 1])
            if np.isfinite(value):
                correlation = value

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

    # Calculate a relative risk score from 0 to 100.
    ranked = df.copy()
    score = np.zeros(len(ranked), dtype=np.float64)

    for column, weight in RISK_WEIGHTS.items():
        feature_series = pd.to_numeric(ranked[column], errors="coerce")
        feature_values = np.asarray(feature_series, dtype=np.float64)

        valid_values = np.isfinite(feature_values)
        percentile_scores = np.zeros(len(ranked), dtype=np.float64)

        if valid_values.any():
            valid_series = pd.Series(feature_values[valid_values])
            percentile_scores[valid_values] = np.asarray(
                valid_series.rank(method="average", pct=True),
                dtype=np.float64,
            )

        score += percentile_scores * weight * 100

    ranked["risk_score"] = np.round(score, 1)
    ranked["risk_band"] = pd.cut(
        ranked["risk_score"],
        bins=[-0.1, 40, 70, 100],
        labels=["LOW", "MEDIUM", "HIGH"],
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

    print("\nTOP 20 CARS BY RELATIVE BREAKDOWN RISK")

    columns = [
        "car_id",
        "km_since_service",
        "avg_daily_km",
        "load_factor",
        "risk_score",
        "risk_band",
        "broke_down",
    ]

    print(ranked[columns].head(20).to_string(index=False))

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
