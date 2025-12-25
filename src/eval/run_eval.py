import asyncio
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

from src.agents.classifier_agent import ClassifierAgent
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


async def run_eval(csv_path: Path, out_path: Path, max_samples: int = None):
    df = pd.read_csv(csv_path).fillna("")

    # Allow testing with a subset of samples for quick evaluation
    if max_samples and len(df) > max_samples:
        original_len = len(df)
        df = df.head(max_samples)
        print(f"Testing with first {max_samples} samples (out of {original_len} total)")

    # Check if we have a real API key
    import os

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your-groq-api-key-here":
        print("WARNING: GROQ_API_KEY not set or using placeholder value.")
        print("Evaluation will fail. Please set a valid GROQ_API_KEY in .env file.")
        print("Get your API key from: https://console.groq.com/")
        return

    pipeline = AnalysisPipeline()

    tasks = [_run_one(pipeline, row) for _, row in df.iterrows()]
    results = []
    for i, task in enumerate(tasks):
        print(f"Processing sample {i+1}/{len(tasks)}: {df.iloc[i]['id']}")
        result = await task
        results.append(result)

        # Add delay between requests to respect rate limits (Groq free tier: 6000 TPM)
        # Optimized prompts: ~400 tokens per call × 3 calls = ~1200 tokens per sample
        # 6000 TPM / 1200 = 5 samples per minute → 12 seconds between samples
        if i < len(tasks) - 1:  # Don't delay after the last request
            await asyncio.sleep(12)  # 12 second delay for optimized token usage

    out_df = pd.DataFrame(results)

    # --- Basic metrics ---
    out_df["correct"] = (out_df["expected_label"] == out_df["pred_label"]) & (
        out_df["expected_label"] != ""
    )

    accuracy = out_df["correct"].mean() if out_df["expected_label"].ne("").any() else np.nan

    label_counts = out_df.groupby("pred_label").size().reset_index(name="count")
    conf_by_label = (
        out_df.groupby("pred_label")["confidence"]
        .mean(numeric_only=True)
        .reset_index()
        .rename(columns={"confidence": "avg_confidence"})
    )

    # Confusion matrix (only for rows with expected_label)
    has_expected = out_df["expected_label"].ne("")
    confusion = None
    if has_expected.any():
        confusion = pd.crosstab(
            out_df.loc[has_expected, "expected_label"], out_df.loc[has_expected, "pred_label"]
        )

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


async def run_classifier_eval(csv_path: Path, out_path: Path, max_samples: int = None):
    """Run evaluation using only the classifier (1 API call per sample instead of 3)"""
    df = pd.read_csv(csv_path).fillna("")

    # Check for GROQ API key
    import os

    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your-groq-api-key-here":
        print("WARNING: GROQ_API_KEY not set or using placeholder value.")
        print("Evaluation will fail. Please set a valid GROQ_API_KEY in .env file.")
        print("Get your API key from: https://console.groq.com/")
        return

    if max_samples and len(df) > max_samples:
        original_len = len(df)
        df = df.head(max_samples)
        print(f"Testing with first {max_samples} samples (out of {original_len} total)")

    classifier = ClassifierAgent()

    results = []
    for i, (_, row) in enumerate(df.iterrows()):
        sample_id = row["id"]
        text = row["text"]

        print(f"Processing sample {i+1}/{len(df)}: {sample_id}")

        try:
            # Only use classifier (1 API call instead of 3)
            cls_result = await classifier.run(text=text)
            category = cls_result.get("category", "")
            needs_review = cls_result.get("needs_review", False)

            # Map to our expected labels for evaluation
            if needs_review:
                pred_label = (
                    "flag"
                    if category in ["harassment", "misinformation", "politics", "privacy", "spam"]
                    else "block"
                )
            else:
                pred_label = "allowed"

            results.append(
                {
                    "id": sample_id,
                    "text": text,
                    "expected_label": row["expected_label"],
                    "pred_label": pred_label,
                    "confidence": 0.8,  # Default confidence for classifier-only
                    "category": category,
                    "needs_review": needs_review,
                    "reasons": f"Classifier: {category}, needs_review: {needs_review}",
                }
            )

        except Exception as e:
            print(f"Error processing sample {sample_id}: {e}")
            results.append(
                {
                    "id": sample_id,
                    "text": text,
                    "expected_label": row["expected_label"],
                    "pred_label": "error",
                    "confidence": 0.0,
                    "category": "error",
                    "needs_review": False,
                    "reasons": f"Error: {e}",
                }
            )

        # Optimized classifier-only: ~200 tokens per call
        # 6000 TPM / 200 = 30 samples per minute → 2 seconds between samples
        if i < len(df) - 1:
            await asyncio.sleep(3)  # 3 second delay for classifier-only

    out_df = pd.DataFrame(results)

    # Basic metrics
    out_df["correct"] = (out_df["expected_label"] == out_df["pred_label"]) & (
        out_df["expected_label"] != ""
    )
    accuracy = out_df["correct"].mean() if len(out_df) > 0 else 0

    # Label distribution
    label_counts = (
        out_df["pred_label"]
        .value_counts(dropna=False)
        .rename_axis("pred_label")
        .reset_index(name="count")
    )

    # Confusion matrix
    allowed_mask = out_df["expected_label"] == "allowed"
    flag_mask = out_df["expected_label"] == "flag"
    block_mask = out_df["expected_label"] == "block"

    allowed_correct = (
        (out_df[allowed_mask]["pred_label"] == "allowed").mean() if allowed_mask.any() else 0
    )
    flag_correct = (out_df[flag_mask]["pred_label"] == "flag").mean() if flag_mask.any() else 0
    block_correct = (out_df[block_mask]["pred_label"] == "block").mean() if block_mask.any() else 0

    print("\n=== CLASSIFIER-ONLY EVAL SUMMARY ===")
    print(f"Samples: {len(out_df)}")
    print(f"Overall Accuracy: {accuracy:.3f}")
    print(f"Allowed Accuracy: {allowed_correct:.3f}")
    print(f"Flag Accuracy: {flag_correct:.3f}")
    print(f"Block Accuracy: {block_correct:.3f}")
    print("\nPredicted label distribution:")
    print(label_counts.to_string(index=False))

    out_df.to_csv(out_path, index=False)
    print(f"\nSaved detailed results to: {out_path}")


def main():
    import sys

    max_samples = None
    classifier_only = False

    args = sys.argv[1:]
    for arg in args:
        if arg == "--classifier-only":
            classifier_only = True
        elif arg.isdigit():
            max_samples = int(arg)

    if max_samples:
        print(f"Limiting evaluation to first {max_samples} samples")

    csv_path = Path("src/eval/eval_samples.csv")
    out_path = Path("src/eval/eval_results.csv")

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing eval samples file: {csv_path}")

    if classifier_only:
        print("Running CLASSIFIER-ONLY evaluation (1 API call per sample)")
        asyncio.run(run_classifier_eval(csv_path, out_path, max_samples))
    else:
        print("Running FULL PIPELINE evaluation (3 API calls per sample)")
        asyncio.run(run_eval(csv_path, out_path, max_samples))


if __name__ == "__main__":
    main()
