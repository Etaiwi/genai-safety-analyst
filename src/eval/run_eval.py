import asyncio
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
load_dotenv()  # Load environment variables

from src.pipelines.analysis_pipeline import AnalysisPipeline


def _safe_float(x, default=np.nan):
    try:
        return float(x)
    except Exception:
        return default


async def _run_one(pipeline: AnalysisPipeline, row) -> dict:
    res = await pipeline.analyze(content_id=row["id"], text=row["text"])
    decision = res.get("decision", {})
    return {
        "id": row["id"],
        "text": row["text"],
        "expected_label": row.get("expected_label", ""),
        "pred_label": decision.get("label"),
        "confidence": _safe_float(decision.get("confidence")),
        "reasons": " | ".join(decision.get("reasons", [])[:5]),
    }


async def run_eval(csv_path: Path, out_path: Path):
    df = pd.read_csv(csv_path).fillna("")

    # Check if we have a real API key
    import os
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your-groq-api-key-here":
        print("WARNING: GROQ_API_KEY not set or using placeholder value.")
        print("Evaluation will fail. Please set a valid GROQ_API_KEY in .env file.")
        print("Get your API key from: https://console.groq.com/")
        return

    pipeline = AnalysisPipeline()

    tasks = [ _run_one(pipeline, row) for _, row in df.iterrows() ]
    results = []
    for i, task in enumerate(tasks):
        print(f"Processing sample {i+1}/{len(tasks)}: {df.iloc[i]['id']}")
        result = await task
        results.append(result)

    out_df = pd.DataFrame(results)

    # --- Basic metrics ---
    out_df["correct"] = (out_df["expected_label"] == out_df["pred_label"]) & (out_df["expected_label"] != "")

    accuracy = out_df["correct"].mean() if out_df["expected_label"].ne("").any() else np.nan

    label_counts = out_df.groupby("pred_label").size().reset_index(name="count")
    conf_by_label = out_df.groupby("pred_label")["confidence"].mean(numeric_only=True).reset_index().rename(columns={"confidence": "avg_confidence"})

    # Confusion matrix (only for rows with expected_label)
    has_expected = out_df["expected_label"].ne("")
    confusion = None
    if has_expected.any():
        confusion = pd.crosstab(out_df.loc[has_expected, "expected_label"], out_df.loc[has_expected, "pred_label"])

    # Save detailed results
    out_df.to_csv(out_path, index=False)

    # Print summary (nice for README)
    print("\n=== EVAL SUMMARY ===")
    print(f"Samples: {len(out_df)}")
    if not np.isnan(accuracy):
        print(f"Accuracy (vs expected_label): {accuracy:.3f}")

    print("\nPredicted label distribution:")
    print(label_counts.to_string(index=False))

    print("\nAverage confidence by predicted label:")
    print(conf_by_label.to_string(index=False))

    if confusion is not None:
        print("\nConfusion matrix (expected x predicted):")
        print(confusion.to_string())

    print(f"\nSaved detailed results to: {out_path}")


def main():
    csv_path = Path("src/eval/eval_samples.csv")
    out_path = Path("src/eval/eval_results.csv")

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing eval samples file: {csv_path}")

    asyncio.run(run_eval(csv_path, out_path))


if __name__ == "__main__":
    main()
