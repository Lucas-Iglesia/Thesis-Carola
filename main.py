"""
Main entry point for ATS discrimination testing system.
Run experiments to test if the ATS system shows bias based on CV demographics.
"""

import asyncio
from experiment_runner import ATSExperiment, quick_test
from analyzer import ATSAnalyzer
from cv_variations import NAME_VARIATIONS


def run_full_experiment(iterations_per_profile: int = 10, save_results: bool = True, max_concurrent: int = 5):
    """
    Run a full experiment testing all CV profiles using async execution.

    Args:
        iterations_per_profile: Number of times to evaluate each CV
        save_results: Whether to save results to file
        max_concurrent: Maximum number of concurrent requests (default: 5)

    Returns:
        Tuple of (experiment_data, analyzer, results_filename)
    """
    print(f"\n🔬 Starting ATS Discrimination Testing System (ASYNC MODE)")
    print(f"📊 Configuration:")
    print(f"   - Profiles to test: {len(NAME_VARIATIONS)}")
    print(f"   - Iterations per profile: {iterations_per_profile}")
    print(f"   - Total evaluations: {len(NAME_VARIATIONS) * iterations_per_profile}")
    print(f"   - Max concurrent requests: {max_concurrent}")
    print()

    # Create and run experiment asynchronously
    experiment = ATSExperiment(iterations_per_config=iterations_per_profile, max_concurrent=max_concurrent)
    experiment_data = asyncio.run(experiment.run_all_experiments_async())

    # Save results
    results_filename = None
    if save_results:
        results_filename = experiment.save_results(experiment_data)

    # Analyze results
    print("\n📈 Analyzing results...")
    analyzer = ATSAnalyzer(results_data=experiment_data)

    # Generate report
    report = analyzer.generate_report()
    print("\n" + report)

    if save_results:
        report_filename = results_filename.replace(".json", "_report.txt")
        analyzer.generate_report(output_file=report_filename)

        csv_filename = results_filename.replace(".json", "_summary.csv")
        analyzer.export_summary_csv(output_file=csv_filename)

    return experiment_data, analyzer, results_filename


def run_quick_test(iterations: int = 3, num_profiles: int = 2):
    """
    Run a quick test with limited profiles and iterations.

    Args:
        iterations: Number of iterations per profile
        num_profiles: Number of profiles to test
    """
    print(f"\n🧪 Running Quick Test")
    print(f"   - Testing {num_profiles} profiles")
    print(f"   - {iterations} iterations each")
    print()

    results, filename = quick_test(iterations=iterations, num_profiles=num_profiles)

    # Analyze
    print("\n📈 Analyzing results...")
    analyzer = ATSAnalyzer(results_data=results)
    report = analyzer.generate_report()
    print("\n" + report)

    return results, analyzer, filename


def run_custom_experiment(profile_ids: list, iterations: int = 10, max_concurrent: int = 5):
    """
    Run experiment with specific profiles only using async execution.

    Args:
        profile_ids: List of profile IDs to test (e.g., ["profile_1", "profile_2"])
        iterations: Number of iterations per profile
        max_concurrent: Maximum number of concurrent requests (default: 5)
    """
    # Filter profiles
    selected_profiles = [p for p in NAME_VARIATIONS if p["id"] in profile_ids]

    if not selected_profiles:
        print(f"❌ No profiles found matching IDs: {profile_ids}")
        return None

    print(f"\n🔬 Running Custom Experiment (ASYNC MODE)")
    print(f"   - Selected profiles: {[p['id'] for p in selected_profiles]}")
    print(f"   - Iterations per profile: {iterations}")
    print(f"   - Max concurrent requests: {max_concurrent}")
    print()

    experiment = ATSExperiment(iterations_per_config=iterations, max_concurrent=max_concurrent)
    experiment_data = asyncio.run(experiment.run_all_experiments_async(profiles=selected_profiles))

    results_filename = experiment.save_results(experiment_data)

    # Analyze
    analyzer = ATSAnalyzer(results_data=experiment_data)
    report = analyzer.generate_report()
    print("\n" + report)

    report_filename = results_filename.replace(".json", "_report.txt")
    analyzer.generate_report(output_file=report_filename)

    return experiment_data, analyzer, results_filename


if __name__ == "__main__":
    import sys

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "quick":
            # Quick test
            run_quick_test(iterations=3, num_profiles=2)

        elif command == "full":
            # Full experiment
            iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            run_full_experiment(iterations_per_profile=iterations)

        elif command == "custom":
            # Custom profiles
            if len(sys.argv) < 3:
                print("Usage: python main.py custom <profile_ids...> [iterations]")
                print("Example: python main.py custom profile_1 profile_2 profile_3 5")
                sys.exit(1)

            # Get profile IDs and iterations
            profile_ids = []
            iterations = 10
            for arg in sys.argv[2:]:
                if arg.startswith("profile_"):
                    profile_ids.append(arg)
                else:
                    try:
                        iterations = int(arg)
                    except ValueError:
                        pass

            run_custom_experiment(profile_ids=profile_ids, iterations=iterations)

        elif command == "analyze":
            # Analyze existing results
            if len(sys.argv) < 3:
                print("Usage: python main.py analyze <results_file.json>")
                sys.exit(1)

            from analyzer import analyze_results
            analyze_results(sys.argv[2])

        else:
            print("Unknown command. Available commands:")
            print("  python main.py quick              - Quick test (3 iterations, 2 profiles)")
            print("  python main.py full [iterations]  - Full experiment (default: 10 iterations)")
            print("  python main.py custom <profile_ids...> [iterations]")
            print("  python main.py analyze <file.json> - Analyze existing results")
    else:
        # Default: show menu
        print("\n" + "="*70)
        print("ATS DISCRIMINATION TESTING SYSTEM")
        print("="*70)
        print("\nAvailable commands:")
        print("  1. Quick test:    python main.py quick")
        print("  2. Full test:     python main.py full [iterations]")
        print("  3. Custom test:   python main.py custom profile_1 profile_2 [iterations]")
        print("  4. Analyze:       python main.py analyze results_file.json")
        print("\nOr run interactively:")
        print()

        choice = input("Choose an option (1-4) or press Enter to run quick test: ").strip()

        if choice == "1" or choice == "":
            run_quick_test()
        elif choice == "2":
            iterations = input("Enter iterations per profile (default: 10): ").strip()
            iterations = int(iterations) if iterations else 10
            run_full_experiment(iterations_per_profile=iterations)
        elif choice == "3":
            print("\nAvailable profiles:")
            for p in NAME_VARIATIONS:
                print(f"  - {p['id']}: {p['description']}")
            profile_input = input("\nEnter profile IDs (space-separated): ").strip()
            profile_ids = profile_input.split()
            iterations = input("Enter iterations per profile (default: 10): ").strip()
            iterations = int(iterations) if iterations else 10
            run_custom_experiment(profile_ids=profile_ids, iterations=iterations)
        elif choice == "4":
            filename = input("Enter results filename: ").strip()
            from analyzer import analyze_results
            analyze_results(filename)
        else:
            print("Invalid choice. Running quick test...")
            run_quick_test()