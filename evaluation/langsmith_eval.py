#!/usr/bin/env python3
"""
LangSmith Evaluation Integration

This script:
1. Creates/updates a dataset in LangSmith with test cases
2. Runs evaluations using LangSmith's evaluate() API
3. Results appear in LangSmith dashboard for tracking

Usage:
    python -m evaluation.langsmith_eval --create-dataset    # Upload test cases
    python -m evaluation.langsmith_eval --run               # Run evaluation
    python -m evaluation.langsmith_eval --create-dataset --run  # Both

Requirements:
    LANGCHAIN_API_KEY environment variable must be set
"""

import json
import os
import argparse
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from langsmith import Client
from langsmith.evaluation import evaluate


# Dataset name in LangSmith
DATASET_NAME = "call-center-assistant-eval"


def load_test_cases() -> list:
    """Load test cases from JSON file"""
    path = Path(__file__).parent / "datasets" / "test_cases.json"
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("test_cases", [])


def create_dataset(client: Client) -> str:
    """Create or update the evaluation dataset in LangSmith

    Returns:
        Dataset ID
    """
    print(f"Creating/updating dataset: {DATASET_NAME}")

    # Check if dataset exists
    datasets = list(client.list_datasets(dataset_name=DATASET_NAME))

    if datasets:
        dataset = datasets[0]
        print(f"Dataset already exists (ID: {dataset.id})")
        # Delete existing examples to refresh
        examples = list(client.list_examples(dataset_id=dataset.id))
        for ex in examples:
            client.delete_example(ex.id)
        print(f"Cleared {len(examples)} existing examples")
    else:
        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description="Evaluation dataset for AI Call Center Assistant"
        )
        print(f"Created new dataset (ID: {dataset.id})")

    # Load and upload test cases
    test_cases = load_test_cases()

    for tc in test_cases:
        client.create_example(
            dataset_id=dataset.id,
            inputs={
                "transcript": tc["transcript"],
                "test_id": tc["id"],
                "category": tc.get("category", "")
            },
            outputs={
                "expected_sentiment": tc["expected"].get("sentiment"),
                "expected_resolution": tc["expected"].get("resolution_status"),
                "expected_abuse": tc["expected"].get("abuse_detected", False),
                "expected_topics": tc["expected"].get("key_topics", [])
            },
            metadata={
                "name": tc.get("name", ""),
                "category": tc.get("category", "")
            }
        )

    print(f"Uploaded {len(test_cases)} test cases")
    return str(dataset.id)


def target_function(inputs: dict) -> dict:
    """The function being evaluated - runs the full pipeline

    Args:
        inputs: Dictionary with 'transcript' key

    Returns:
        Dictionary with pipeline outputs
    """
    from graph.workflow import run_analysis

    transcript = inputs.get("transcript", "")

    # Run the pipeline
    result = run_analysis(
        raw_input=transcript,
        input_type="transcript"
    )

    # Extract relevant outputs
    summary = result.get("summary")
    qa_scores = result.get("qa_scores")
    abuse_flags = result.get("abuse_flags", [])

    # Convert to serializable format
    output = {
        "summary": {},
        "qa_scores": {},
        "abuse_detected": len(abuse_flags) > 0,
        "execution_path": result.get("execution_path", [])
    }

    if summary:
        if hasattr(summary, "model_dump"):
            output["summary"] = summary.model_dump()
        else:
            output["summary"] = summary

        # Extract key fields for easy evaluation
        output["sentiment"] = output["summary"].get("sentiment")
        if hasattr(output["sentiment"], "value"):
            output["sentiment"] = output["sentiment"].value

        output["resolution_status"] = output["summary"].get("resolution_status")
        if hasattr(output["resolution_status"], "value"):
            output["resolution_status"] = output["resolution_status"].value

    if qa_scores:
        if hasattr(qa_scores, "model_dump"):
            output["qa_scores"] = qa_scores.model_dump()
        else:
            output["qa_scores"] = qa_scores

    return output


# Custom evaluators for LangSmith

def faithfulness_evaluator(run, example) -> dict:
    """Evaluate summary faithfulness using LLM"""
    from evaluation.evaluators import FaithfulnessEvaluator

    transcript = example.inputs.get("transcript", "")
    summary = run.outputs.get("summary", {})

    if not transcript or not summary:
        return {"key": "faithfulness", "score": 0, "comment": "Missing data"}

    evaluator = FaithfulnessEvaluator()
    result = evaluator.evaluate(transcript, summary)

    return {
        "key": "faithfulness",
        "score": result.score / 10,  # Normalize to 0-1
        "comment": result.reasoning
    }


def completeness_evaluator(run, example) -> dict:
    """Evaluate summary completeness using LLM"""
    from evaluation.evaluators import CompletenessEvaluator

    transcript = example.inputs.get("transcript", "")
    summary = run.outputs.get("summary", {})

    if not transcript or not summary:
        return {"key": "completeness", "score": 0, "comment": "Missing data"}

    evaluator = CompletenessEvaluator()
    result = evaluator.evaluate(transcript, summary)

    return {
        "key": "completeness",
        "score": result.score / 10,
        "comment": result.reasoning
    }


def sentiment_accuracy_evaluator(run, example) -> dict:
    """Check if sentiment matches expected"""
    actual = run.outputs.get("sentiment", "").lower() if run.outputs.get("sentiment") else ""
    expected = (example.outputs.get("expected_sentiment") or "").lower()

    if not expected:
        return {"key": "sentiment_accuracy", "score": 1, "comment": "No expected value"}

    match = actual == expected
    return {
        "key": "sentiment_accuracy",
        "score": 1 if match else 0,
        "comment": f"Expected: {expected}, Got: {actual}"
    }


def resolution_accuracy_evaluator(run, example) -> dict:
    """Check if resolution status matches expected"""
    actual = run.outputs.get("resolution_status", "").lower() if run.outputs.get("resolution_status") else ""
    expected = (example.outputs.get("expected_resolution") or "").lower()

    if not expected:
        return {"key": "resolution_accuracy", "score": 1, "comment": "No expected value"}

    match = actual == expected
    return {
        "key": "resolution_accuracy",
        "score": 1 if match else 0,
        "comment": f"Expected: {expected}, Got: {actual}"
    }


def abuse_detection_evaluator(run, example) -> dict:
    """Check if abuse detection matches expected"""
    actual = run.outputs.get("abuse_detected", False)
    expected = example.outputs.get("expected_abuse", False)

    match = actual == expected
    return {
        "key": "abuse_detection",
        "score": 1 if match else 0,
        "comment": f"Expected abuse: {expected}, Detected: {actual}"
    }


def qa_validity_evaluator(run, example) -> dict:
    """Validate QA scores structure and ranges"""
    from evaluation.evaluators import QAScoreValidator

    qa_scores = run.outputs.get("qa_scores", {})
    transcript = example.inputs.get("transcript", "")

    validator = QAScoreValidator()
    result = validator.validate(qa_scores, transcript)

    return {
        "key": "qa_validity",
        "score": result.score,
        "comment": f"Valid: {result.is_valid}" + (f", Issues: {result.issues}" if result.issues else "")
    }


def run_evaluation(experiment_prefix: str = "eval") -> dict:
    """Run evaluation experiment in LangSmith

    Args:
        experiment_prefix: Prefix for experiment name

    Returns:
        Evaluation results
    """
    print(f"\nRunning evaluation experiment: {experiment_prefix}")
    print("=" * 60)

    # Run evaluation
    results = evaluate(
        target_function,
        data=DATASET_NAME,
        evaluators=[
            faithfulness_evaluator,
            completeness_evaluator,
            sentiment_accuracy_evaluator,
            resolution_accuracy_evaluator,
            abuse_detection_evaluator,
            qa_validity_evaluator
        ],
        experiment_prefix=experiment_prefix,
        max_concurrency=2,  # Limit parallel runs to avoid rate limits
    )

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"\nView results in LangSmith:")
    print(f"  https://smith.langchain.com")
    print(f"  Project: {os.getenv('LANGCHAIN_PROJECT', 'default')}")
    print(f"  Dataset: {DATASET_NAME}")

    return results


def main():
    parser = argparse.ArgumentParser(description="LangSmith Evaluation")
    parser.add_argument("--create-dataset", action="store_true", help="Create/update dataset in LangSmith")
    parser.add_argument("--run", action="store_true", help="Run evaluation experiment")
    parser.add_argument("--prefix", default="eval", help="Experiment prefix (default: eval)")
    args = parser.parse_args()

    # Check for API key
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("Error: LANGCHAIN_API_KEY not set")
        print("Get your key from: https://smith.langchain.com/settings")
        return

    client = Client()

    if args.create_dataset:
        create_dataset(client)

    if args.run:
        run_evaluation(experiment_prefix=args.prefix)

    if not args.create_dataset and not args.run:
        parser.print_help()


if __name__ == "__main__":
    main()
