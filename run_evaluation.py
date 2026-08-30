import json
import csv
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.resume_parser import extract_resume_information
from app.job_parser import extract_job_requirements
from app.scoring import compute_overall_match

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "evaluation_dataset",
    "evaluation_dataset.json"
)

RESULTS_CSV = os.path.join(
    PROJECT_ROOT,
    "data",
    "evaluation_dataset",
    "evaluation_results.csv"
)


def run_evaluation():
    if not os.path.exists(DATASET_PATH):
        print("ERROR: Evaluation dataset not found.")
        print(DATASET_PATH)
        return

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    results = []

    print("=" * 110)
    print(
        f"{'Case ID':<10} | "
        f"{'Scenario':<38} | "
        f"{'Score':<10} | "
        f"{'Recommendation':<20} | "
        f"{'Pass?':<6}"
    )
    print("-" * 110)

    for item in dataset:
        case_id = item.get("id", "")
        scenario = item.get("scenario", "")
        resume_text = item.get("resume_text", "")
        job_text = item.get("job_text", "")
        expected = item.get("expected_result", {})

        expected_recommendation = expected.get(
            "recommendation",
            ""
        )

        expected_min = float(
            expected.get("min_score", 0)
        )

        expected_max = float(
            expected.get("max_score", 100)
        )

        print(f"\nCASE: {case_id}")

        try:
            resume_data = extract_resume_information(
                resume_text
            )

            job_data = extract_job_requirements(
                job_text
            )

            print(
                "RESUME NAME:",
                getattr(resume_data, "name", "")
            )

            print(
                "RESUME SKILLS:",
                getattr(resume_data, "skills", [])
            )

            print(
                "RESUME YEARS:",
                getattr(
                    resume_data,
                    "years_experience",
                    0.0
                )
            )

            print(
                "RESUME EDUCATION:",
                getattr(
                    resume_data,
                    "education",
                    []
                )
            )

            print(
                "JOB REQUIRED:",
                getattr(
                    job_data,
                    "required_skills",
                    []
                )
            )

            print(
                "JOB PREFERRED:",
                getattr(
                    job_data,
                    "preferred_skills",
                    []
                )
            )

            print(
                "JOB YEARS:",
                getattr(
                    job_data,
                    "required_experience_years",
                    0.0
                )
            )

            print(
                "JOB EDUCATION:",
                getattr(
                    job_data,
                    "education_required",
                    []
                )
            )

            score_details = compute_overall_match(
                resume_data,
                job_data,
                resume_text,
                job_text
            )

            print("DEBUG:", score_details)
            print("-" * 80)

            final_score = score_details["final_score"]
            recommendation = score_details["recommendation"]

            score_pass = (
                expected_min
                <= final_score
                <= expected_max
            )

            recommendation_pass = (
                recommendation
                == expected_recommendation
            )

            final_pass = (
                score_pass
                and recommendation_pass
            )

            print(
                f"{case_id:<10} | "
                f"{scenario[:38]:<38} | "
                f"{final_score:<10.2f} | "
                f"{recommendation:<20} | "
                f"{'PASS' if final_pass else 'FAIL'}"
            )

            results.append({
                "CaseID": case_id,
                "Scenario": scenario,
                "ExpectedRecommendation":
                    expected_recommendation,
                "ExpectedMinScore":
                    expected_min,
                "ExpectedMaxScore":
                    expected_max,
                "CalculatedScore":
                    final_score,
                "ActualRecommendation":
                    recommendation,
                "ScoreRangePass":
                    score_pass,
                "RecommendationPass":
                    recommendation_pass,
                "FinalResult":
                    "PASS" if final_pass else "FAIL",
                "Error": ""
            })

        except Exception as e:
            error_message = str(e)

            print(
                f"{case_id:<10} | "
                f"{scenario[:38]:<38} | "
                f"{'ERROR':<10} | "
                f"{error_message[:20]:<20} | "
                f"FAIL"
            )

            results.append({
                "CaseID": case_id,
                "Scenario": scenario,
                "ExpectedRecommendation":
                    expected_recommendation,
                "ExpectedMinScore":
                    expected_min,
                "ExpectedMaxScore":
                    expected_max,
                "CalculatedScore": "",
                "ActualRecommendation": "",
                "ScoreRangePass": False,
                "RecommendationPass": False,
                "FinalResult": "ERROR",
                "Error": error_message
            })

    if results:
        os.makedirs(
            os.path.dirname(RESULTS_CSV),
            exist_ok=True
        )

        fieldnames = [
            "CaseID",
            "Scenario",
            "ExpectedRecommendation",
            "ExpectedMinScore",
            "ExpectedMaxScore",
            "CalculatedScore",
            "ActualRecommendation",
            "ScoreRangePass",
            "RecommendationPass",
            "FinalResult",
            "Error"
        ]

        with open(
            RESULTS_CSV,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )
            writer.writeheader()
            writer.writerows(results)

    passed = sum(
        1
        for result in results
        if result["FinalResult"] == "PASS"
    )

    failed = sum(
        1
        for result in results
        if result["FinalResult"] == "FAIL"
    )

    errors = sum(
        1
        for result in results
        if result["FinalResult"] == "ERROR"
    )

    total = len(results)

    accuracy = (
        (passed / total) * 100
        if total
        else 0.0
    )

    print("=" * 110)
    print(f"Total Cases : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Errors      : {errors}")
    print(f"Accuracy    : {accuracy:.2f}%")
    print(f"Results saved to: {RESULTS_CSV}")
    print("=" * 110)


if __name__ == "__main__":
    run_evaluation()