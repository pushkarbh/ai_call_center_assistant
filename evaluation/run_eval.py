#!/usr/bin/env python3
"""
Evaluation Runner for Call Center Assistant

Runs the full evaluation pipeline against the test dataset and reports results.
Can optionally push results to LangSmith for tracking.

Usage:
    python -m evaluation.run_eval [--langsmith] [--verbose]
"""

import json
import time
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

from graph.workflow import run_analysis
from evaluation.evaluators import (
    FaithfulnessEvaluator,
    CompletenessEvaluator,
    QAScoreValidator
)


def load_test_cases(path: str = "evaluation/datasets/test_cases.json") -> list:
    """Load test cases from JSON file"""
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("test_cases", [])


def run_single_evaluation(test_case: dict, verbose: bool = False) -> dict:
    """Run evaluation for a single test case

    Args:
        test_case: Test case dictionary with transcript and expected values
        verbose: Whether to print detailed output

    Returns:
        Dictionary with evaluation results
    """
    test_id = test_case.get("id", "unknown")
    transcript = test_case.get("transcript", "")
    expected = test_case.get("expected", {})

    if verbose:
        print(f"\n{'='*60}")
        print(f"Running: {test_id} - {test_case.get('name', '')}")
        print(f"{'='*60}")

    results = {
        "test_id": test_id,
        "name": test_case.get("name", ""),
        "category": test_case.get("category", ""),
        "success": False,
        "scores": {},
        "errors": [],
        "latency_ms": 0
    }

    try:
        # Run the pipeline
        start_time = time.time()
        final_state = run_analysis(
            raw_input=transcript,
            input_type="transcript"
        )
        latency_ms = (time.time() - start_time) * 1000
        results["latency_ms"] = latency_ms

        if verbose:
            print(f"Pipeline completed in {latency_ms:.0f}ms")

        # Extract outputs
        summary = final_state.get("summary")
        qa_scores = final_state.get("qa_scores")

        if not summary:
            results["errors"].append("No summary generated")
            return results

        # Convert summary to dict if it's a Pydantic model
        if hasattr(summary, "model_dump"):
            summary_dict = summary.model_dump()
        elif hasattr(summary, "dict"):
            summary_dict = summary.dict()
        else:
            summary_dict = summary

        # Convert qa_scores to dict
        if qa_scores:
            if hasattr(qa_scores, "model_dump"):
                qa_dict = qa_scores.model_dump()
            elif hasattr(qa_scores, "dict"):
                qa_dict = qa_scores.dict()
            else:
                qa_dict = qa_scores
        else:
            qa_dict = {}

        # Run evaluators
        if verbose:
            print("Running faithfulness evaluation...")
        faithfulness_eval = FaithfulnessEvaluator()
        faithfulness_result = faithfulness_eval.evaluate(transcript, summary_dict)
        results["scores"]["faithfulness"] = faithfulness_result.score
        results["faithfulness_details"] = {
            "reasoning": faithfulness_result.reasoning,
            "hallucinations": faithfulness_result.hallucinations,
            "misrepresentations": faithfulness_result.misrepresentations
        }

        if verbose:
            print(f"  Faithfulness: {faithfulness_result.score}/10")

        if verbose:
            print("Running completeness evaluation...")
        completeness_eval = CompletenessEvaluator()
        completeness_result = completeness_eval.evaluate(transcript, summary_dict)
        results["scores"]["completeness"] = completeness_result.score
        results["completeness_details"] = {
            "reasoning": completeness_result.reasoning,
            "missing_information": completeness_result.missing_information
        }

        if verbose:
            print(f"  Completeness: {completeness_result.score}/10")

        if verbose:
            print("Running QA score validation...")
        qa_validator = QAScoreValidator()
        qa_result = qa_validator.validate(qa_dict, transcript)
        results["scores"]["qa_validity"] = qa_result.score
        results["qa_details"] = {
            "is_valid": qa_result.is_valid,
            "issues": qa_result.issues,
            "warnings": qa_result.warnings
        }

        if verbose:
            print(f"  QA Validity: {qa_result.score:.2f}")

        # Check expected values
        if expected:
            # Sentiment check
            if "sentiment" in expected and summary_dict.get("sentiment"):
                actual_sentiment = summary_dict["sentiment"]
                if hasattr(actual_sentiment, "value"):
                    actual_sentiment = actual_sentiment.value
                expected_sentiment = expected["sentiment"]
                sentiment_match = actual_sentiment.lower() == expected_sentiment.lower()
                results["scores"]["sentiment_accuracy"] = 1.0 if sentiment_match else 0.0

                if verbose:
                    match_str = "✓" if sentiment_match else "✗"
                    print(f"  Sentiment: {match_str} (expected: {expected_sentiment}, got: {actual_sentiment})")

            # Resolution check
            if "resolution_status" in expected and summary_dict.get("resolution_status"):
                actual_resolution = summary_dict["resolution_status"]
                if hasattr(actual_resolution, "value"):
                    actual_resolution = actual_resolution.value
                expected_resolution = expected["resolution_status"]
                resolution_match = actual_resolution.lower() == expected_resolution.lower()
                results["scores"]["resolution_accuracy"] = 1.0 if resolution_match else 0.0

                if verbose:
                    match_str = "✓" if resolution_match else "✗"
                    print(f"  Resolution: {match_str} (expected: {expected_resolution}, got: {actual_resolution})")

            # Abuse detection check
            if "abuse_detected" in expected:
                actual_abuse = len(final_state.get("abuse_flags", [])) > 0
                expected_abuse = expected["abuse_detected"]
                abuse_match = actual_abuse == expected_abuse
                results["scores"]["abuse_detection_accuracy"] = 1.0 if abuse_match else 0.0

                if verbose:
                    match_str = "✓" if abuse_match else "✗"
                    print(f"  Abuse Detection: {match_str} (expected: {expected_abuse}, got: {actual_abuse})")

        # Calculate overall success
        min_threshold = 6  # Minimum acceptable score out of 10
        results["success"] = (
            results["scores"].get("faithfulness", 0) >= min_threshold and
            results["scores"].get("completeness", 0) >= min_threshold and
            results["scores"].get("qa_validity", 0) >= 0.8
        )

    except Exception as e:
        results["errors"].append(str(e))
        if verbose:
            print(f"Error: {e}")

    return results


def run_full_evaluation(verbose: bool = False, langsmith: bool = False) -> dict:
    """Run evaluation on all test cases

    Args:
        verbose: Whether to print detailed output
        langsmith: Whether to push results to LangSmith

    Returns:
        Dictionary with aggregate results
    """
    print("\n" + "="*60)
    print("AI Call Center Assistant - Evaluation Suite")
    print("="*60)

    test_cases = load_test_cases()
    print(f"Loaded {len(test_cases)} test cases")

    all_results = []
    start_time = time.time()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {test_case.get('id', '')}...", end="" if not verbose else "\n")
        result = run_single_evaluation(test_case, verbose)
        all_results.append(result)

        if not verbose:
            status = "✓" if result["success"] else "✗"
            print(f" {status}")

    total_time = time.time() - start_time

    # Calculate aggregate metrics
    num_passed = sum(1 for r in all_results if r["success"])
    num_failed = len(all_results) - num_passed

    avg_faithfulness = sum(r["scores"].get("faithfulness", 0) for r in all_results) / len(all_results)
    avg_completeness = sum(r["scores"].get("completeness", 0) for r in all_results) / len(all_results)
    avg_latency = sum(r["latency_ms"] for r in all_results) / len(all_results)

    # Accuracy metrics
    sentiment_scores = [r["scores"].get("sentiment_accuracy") for r in all_results if "sentiment_accuracy" in r["scores"]]
    resolution_scores = [r["scores"].get("resolution_accuracy") for r in all_results if "resolution_accuracy" in r["scores"]]
    abuse_scores = [r["scores"].get("abuse_detection_accuracy") for r in all_results if "abuse_detection_accuracy" in r["scores"]]

    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)

    print(f"\nTest Cases: {len(all_results)}")
    print(f"  Passed: {num_passed} ({num_passed/len(all_results)*100:.1f}%)")
    print(f"  Failed: {num_failed} ({num_failed/len(all_results)*100:.1f}%)")

    print(f"\nQuality Scores (avg):")
    print(f"  Faithfulness: {avg_faithfulness:.1f}/10")
    print(f"  Completeness: {avg_completeness:.1f}/10")

    if sentiment_scores:
        print(f"\nClassification Accuracy:")
        print(f"  Sentiment: {sum(sentiment_scores)/len(sentiment_scores)*100:.1f}%")
    if resolution_scores:
        print(f"  Resolution: {sum(resolution_scores)/len(resolution_scores)*100:.1f}%")
    if abuse_scores:
        print(f"  Abuse Detection: {sum(abuse_scores)/len(abuse_scores)*100:.1f}%")

    print(f"\nPerformance:")
    print(f"  Avg Latency: {avg_latency:.0f}ms")
    print(f"  Total Time: {total_time:.1f}s")

    # Failed cases
    failed_cases = [r for r in all_results if not r["success"]]
    if failed_cases:
        print(f"\nFailed Cases:")
        for r in failed_cases:
            print(f"  - {r['test_id']}: {r['name']}")
            if r["errors"]:
                for err in r["errors"]:
                    print(f"      Error: {err}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = Path("evaluation/results")
    results_path.mkdir(exist_ok=True)

    output_file = results_path / f"eval_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "summary": {
                "total": len(all_results),
                "passed": num_passed,
                "failed": num_failed,
                "avg_faithfulness": avg_faithfulness,
                "avg_completeness": avg_completeness,
                "avg_latency_ms": avg_latency,
                "total_time_s": total_time
            },
            "results": all_results
        }, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    return {
        "total": len(all_results),
        "passed": num_passed,
        "failed": num_failed,
        "results": all_results
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run evaluation suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--langsmith", action="store_true", help="Push results to LangSmith")
    args = parser.parse_args()

    run_full_evaluation(verbose=args.verbose, langsmith=args.langsmith)
