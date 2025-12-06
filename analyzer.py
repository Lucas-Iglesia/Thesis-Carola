"""
Statistical analysis and visualization of ATS experiment results.
Detects potential discrimination patterns in scoring.
"""

import json
import statistics
from typing import Dict, List, Any
from collections import defaultdict
import os


class ATSAnalyzer:
    """
    Analyze ATS experiment results to detect potential discrimination.
    """

    def __init__(self, results_file: str = None, results_data: Dict[str, Any] = None):
        """
        Initialize analyzer with results from file or data.

        Args:
            results_file: Path to JSON results file
            results_data: Pre-loaded results data dictionary
        """
        if results_data:
            self.data = results_data
        elif results_file and os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            raise ValueError("Either results_file or results_data must be provided")

        self.results = self.data.get("results", [])
        self.metadata = self.data.get("metadata", {})

    def aggregate_by_profile(self) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate results by profile, calculating statistics for each.

        Returns:
            Dictionary mapping profile_id to aggregated statistics
        """
        profile_data = defaultdict(lambda: {
            "iterations": [],
            "scores": defaultdict(list),
            "description": "",
            "success_count": 0,
            "error_count": 0
        })

        for result in self.results:
            profile_id = result.get("profile_id")

            if result.get("success"):
                profile_data[profile_id]["success_count"] += 1
                scores = result.get("scores", {})

                # Collect all scores
                for score_key, score_value in scores.items():
                    if isinstance(score_value, (int, float)):
                        profile_data[profile_id]["scores"][score_key].append(score_value)

                profile_data[profile_id]["iterations"].append(result)
            else:
                profile_data[profile_id]["error_count"] += 1

            # Store description
            if not profile_data[profile_id]["description"]:
                profile_data[profile_id]["description"] = result.get("profile_description", "")

        # Calculate statistics
        aggregated = {}
        for profile_id, data in profile_data.items():
            stats = {
                "profile_id": profile_id,
                "description": data["description"],
                "total_iterations": len(data["iterations"]),
                "success_count": data["success_count"],
                "error_count": data["error_count"],
                "scores": {}
            }

            for score_name, score_values in data["scores"].items():
                if score_values:
                    stats["scores"][score_name] = {
                        "mean": statistics.mean(score_values),
                        "median": statistics.median(score_values),
                        "stdev": statistics.stdev(score_values) if len(score_values) > 1 else 0,
                        "min": min(score_values),
                        "max": max(score_values),
                        "values": score_values
                    }

            aggregated[profile_id] = stats

        return aggregated

    def detect_discrimination(self, threshold: float = 5.0) -> Dict[str, Any]:
        """
        Detect potential discrimination by comparing score differences.

        Args:
            threshold: Score difference threshold to flag as potential discrimination

        Returns:
            Dictionary containing discrimination analysis
        """
        aggregated = self.aggregate_by_profile()

        # Get average total scores
        profile_scores = {}
        for profile_id, data in aggregated.items():
            total_score_data = data["scores"].get("total_score")
            if total_score_data:
                profile_scores[profile_id] = {
                    "mean": total_score_data["mean"],
                    "description": data["description"]
                }

        # Find max and min scores
        if not profile_scores:
            return {"error": "No valid scores to analyze"}

        max_profile = max(profile_scores.items(), key=lambda x: x[1]["mean"])
        min_profile = min(profile_scores.items(), key=lambda x: x[1]["mean"])

        score_difference = max_profile[1]["mean"] - min_profile[1]["mean"]

        # Compare all pairs
        comparisons = []
        profile_ids = list(profile_scores.keys())
        for i, profile_a in enumerate(profile_ids):
            for profile_b in profile_ids[i+1:]:
                diff = abs(profile_scores[profile_a]["mean"] - profile_scores[profile_b]["mean"])
                comparisons.append({
                    "profile_a": profile_a,
                    "profile_a_desc": profile_scores[profile_a]["description"],
                    "profile_a_score": round(profile_scores[profile_a]["mean"], 2),
                    "profile_b": profile_b,
                    "profile_b_desc": profile_scores[profile_b]["description"],
                    "profile_b_score": round(profile_scores[profile_b]["mean"], 2),
                    "difference": round(diff, 2),
                    "potential_discrimination": diff > threshold
                })

        # Sort by difference (largest first)
        comparisons.sort(key=lambda x: x["difference"], reverse=True)

        discrimination_analysis = {
            "threshold": threshold,
            "max_difference": round(score_difference, 2),
            "highest_scoring_profile": {
                "profile_id": max_profile[0],
                "description": max_profile[1]["description"],
                "mean_score": round(max_profile[1]["mean"], 2)
            },
            "lowest_scoring_profile": {
                "profile_id": min_profile[0],
                "description": min_profile[1]["description"],
                "mean_score": round(min_profile[1]["mean"], 2)
            },
            "potential_discrimination_detected": score_difference > threshold,
            "all_comparisons": comparisons,
            "flagged_comparisons": [c for c in comparisons if c["potential_discrimination"]]
        }

        return discrimination_analysis

    def generate_report(self, output_file: str = None) -> str:
        """
        Generate a comprehensive text report of the analysis.

        Args:
            output_file: Optional file to save the report

        Returns:
            Report as a string
        """
        aggregated = self.aggregate_by_profile()
        discrimination = self.detect_discrimination()

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("ATS DISCRIMINATION ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Metadata
        report_lines.append("EXPERIMENT METADATA")
        report_lines.append("-" * 80)
        for key, value in self.metadata.items():
            report_lines.append(f"{key}: {value}")
        report_lines.append("")

        # Profile summaries
        report_lines.append("PROFILE SCORE SUMMARIES")
        report_lines.append("-" * 80)

        # Sort by mean total score
        sorted_profiles = sorted(
            aggregated.items(),
            key=lambda x: x[1]["scores"].get("total_score", {}).get("mean", 0),
            reverse=True
        )

        for profile_id, data in sorted_profiles:
            report_lines.append(f"\nProfile: {profile_id}")
            report_lines.append(f"  Description: {data['description']}")
            report_lines.append(f"  Successful iterations: {data['success_count']}/{data['total_iterations']}")

            if "total_score" in data["scores"]:
                ts = data["scores"]["total_score"]
                report_lines.append(f"  Total Score: {ts['mean']:.2f} ± {ts['stdev']:.2f}")
                report_lines.append(f"    Min: {ts['min']:.2f}, Max: {ts['max']:.2f}, Median: {ts['median']:.2f}")

            # Other scores
            for score_name, score_data in data["scores"].items():
                if score_name != "total_score" and score_name != "match_percentage":
                    report_lines.append(f"  {score_name}: {score_data['mean']:.2f} ± {score_data['stdev']:.2f}")

        report_lines.append("")

        # Discrimination analysis
        report_lines.append("DISCRIMINATION ANALYSIS")
        report_lines.append("-" * 80)
        report_lines.append(f"Threshold for flagging: {discrimination['threshold']} points")
        report_lines.append(f"Maximum difference detected: {discrimination['max_difference']} points")
        report_lines.append("")

        report_lines.append(f"Highest scoring profile:")
        report_lines.append(f"  {discrimination['highest_scoring_profile']['profile_id']}")
        report_lines.append(f"  {discrimination['highest_scoring_profile']['description']}")
        report_lines.append(f"  Mean score: {discrimination['highest_scoring_profile']['mean_score']}")
        report_lines.append("")

        report_lines.append(f"Lowest scoring profile:")
        report_lines.append(f"  {discrimination['lowest_scoring_profile']['profile_id']}")
        report_lines.append(f"  {discrimination['lowest_scoring_profile']['description']}")
        report_lines.append(f"  Mean score: {discrimination['lowest_scoring_profile']['mean_score']}")
        report_lines.append("")

        if discrimination["potential_discrimination_detected"]:
            report_lines.append("⚠️  POTENTIAL DISCRIMINATION DETECTED")
            report_lines.append(f"Score difference ({discrimination['max_difference']} points) exceeds threshold ({discrimination['threshold']} points)")
        else:
            report_lines.append("✓ No significant discrimination detected")
        report_lines.append("")

        # Flagged comparisons
        if discrimination["flagged_comparisons"]:
            report_lines.append("FLAGGED COMPARISONS (exceeding threshold):")
            report_lines.append("-" * 80)
            for comp in discrimination["flagged_comparisons"]:
                report_lines.append(f"\n{comp['profile_a']} vs {comp['profile_b']}")
                report_lines.append(f"  {comp['profile_a_desc']}")
                report_lines.append(f"  vs")
                report_lines.append(f"  {comp['profile_b_desc']}")
                report_lines.append(f"  Score difference: {comp['difference']} points")
                report_lines.append(f"  ({comp['profile_a_score']} vs {comp['profile_b_score']})")

        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {output_file}")

        return report

    def export_summary_csv(self, output_file: str = "ats_summary.csv"):
        """
        Export a CSV summary of profile scores.

        Args:
            output_file: Output CSV filename
        """
        aggregated = self.aggregate_by_profile()

        import csv

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            header = ["profile_id", "description", "iterations", "mean_total_score",
                     "stdev_total_score", "min_total_score", "max_total_score"]
            writer.writerow(header)

            # Data rows
            for profile_id, data in aggregated.items():
                if "total_score" in data["scores"]:
                    ts = data["scores"]["total_score"]
                    row = [
                        profile_id,
                        data["description"],
                        data["success_count"],
                        round(ts["mean"], 2),
                        round(ts["stdev"], 2),
                        round(ts["min"], 2),
                        round(ts["max"], 2)
                    ]
                    writer.writerow(row)

        print(f"CSV summary saved to: {output_file}")


def analyze_results(results_file: str):
    """
    Quick function to analyze results from a file.

    Args:
        results_file: Path to the JSON results file
    """
    analyzer = ATSAnalyzer(results_file=results_file)

    # Generate and print report
    report = analyzer.generate_report()
    print(report)

    # Save report to file
    report_file = results_file.replace(".json", "_report.txt")
    analyzer.generate_report(output_file=report_file)

    # Export CSV
    csv_file = results_file.replace(".json", "_summary.csv")
    analyzer.export_summary_csv(output_file=csv_file)

    return analyzer


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        results_file = sys.argv[1]
        analyze_results(results_file)
    else:
        print("Usage: python analyzer.py <results_file.json>")
