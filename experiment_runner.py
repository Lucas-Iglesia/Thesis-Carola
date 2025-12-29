"""
Experiment runner to test ATS system for potential discrimination.
Runs multiple iterations per CV configuration and aggregates results.
"""

import json
import time
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import ollama

from cv_variations import NAME_VARIATIONS, generate_cv
from prompt import job_description, prompt_template


class ATSExperiment:
    """
    Class to run ATS discrimination experiments.
    Tests different CV profiles multiple times to detect bias.
    """

    def __init__(self, model_name: str = "deepseek-r1", iterations_per_config: int = 10, max_concurrent: int = 5, temperature: float = 0.2):
        """
        Initialize the experiment runner.

        Args:
            model_name: Name of the Ollama model to use (default: deepseek-r1)
            iterations_per_config: Number of times to run each CV configuration
            max_concurrent: Maximum number of concurrent API calls (default: 5)
            temperature: Model temperature for consistent grading (default: 0.2)
        """
        self.model_name = model_name
        self.iterations_per_config = iterations_per_config
        self.max_concurrent = max_concurrent
        self.temperature = temperature
        self.results = []

    def run_single_evaluation(self, cv_text: str, profile_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Run a single CV evaluation using the LLM.

        Args:
            cv_text: The CV text to evaluate
            profile_info: Information about the profile being tested

        Returns:
            Dictionary containing the evaluation results
        """
        prompt = prompt_template.format(cv=cv_text, job_description=job_description)

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": self.temperature}
            )

            # Extract JSON from response
            response_text = response['message']['content'].strip()

            # Try to find JSON in the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # Assume the entire response is JSON
                json_text = response_text

            scores = json.loads(json_text)

            return {
                "success": True,
                "scores": scores,
                "profile_id": profile_info["id"],
                "profile_description": profile_info["description"],
                "timestamp": datetime.now().isoformat(),
                "raw_response": response_text
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "profile_id": profile_info["id"],
                "profile_description": profile_info["description"],
                "timestamp": datetime.now().isoformat()
            }

    async def run_single_evaluation_async(self, cv_text: str, profile_info: Dict[str, str], iteration: int = 1) -> Dict[str, Any]:
        """
        Run a single CV evaluation using the LLM asynchronously.

        Args:
            cv_text: The CV text to evaluate
            profile_info: Information about the profile being tested
            iteration: Iteration number for tracking

        Returns:
            Dictionary containing the evaluation results
        """
        prompt = prompt_template.format(cv=cv_text, job_description=job_description)

        try:
            # Run the blocking API call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": self.temperature}
                )
            )

            # Extract JSON from response
            response_text = response['message']['content'].strip()

            # Try to find JSON in the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # Assume the entire response is JSON
                json_text = response_text

            scores = json.loads(json_text)

            return {
                "success": True,
                "scores": scores,
                "profile_id": profile_info["id"],
                "profile_description": profile_info["description"],
                "timestamp": datetime.now().isoformat(),
                "iteration": iteration,
                "raw_response": response_text
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "profile_id": profile_info["id"],
                "profile_description": profile_info["description"],
                "timestamp": datetime.now().isoformat(),
                "iteration": iteration
            }

    def run_profile_experiment(self, profile: Dict[str, str], verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Run multiple evaluations for a single profile.

        Args:
            profile: Profile configuration to test
            verbose: Whether to print progress

        Returns:
            List of results for all iterations
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"Testing Profile: {profile['name']}")
            print(f"Description: {profile['description']}")
            print(f"Running {self.iterations_per_config} iterations...")
            print(f"{'='*70}")

        cv_text = generate_cv(profile)
        profile_results = []

        for iteration in range(self.iterations_per_config):
            if verbose:
                print(f"  Iteration {iteration + 1}/{self.iterations_per_config}...", end=" ")

            result = self.run_single_evaluation(cv_text, profile)
            result["iteration"] = iteration + 1
            profile_results.append(result)

            if verbose:
                if result["success"]:
                    total_score = result["scores"].get("total_score", "N/A")
                    print(f"✓ Score: {total_score}")
                else:
                    print(f"✗ Error: {result['error']}")

            # Small delay to avoid rate limiting
            # time.sleep(0.5)

        return profile_results

    async def run_profile_experiment_async(self, profile: Dict[str, str], verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Run multiple evaluations for a single profile concurrently.

        Args:
            profile: Profile configuration to test
            verbose: Whether to print progress

        Returns:
            List of results for all iterations
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"Testing Profile: {profile['name']}")
            print(f"Description: {profile['description']}")
            print(f"Running {self.iterations_per_config} iterations concurrently (max {self.max_concurrent} at a time)...")
            print(f"{'='*70}")

        cv_text = generate_cv(profile)
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def bounded_evaluation(iteration):
            async with semaphore:
                if verbose:
                    print(f"  Starting iteration {iteration + 1}/{self.iterations_per_config}...")
                result = await self.run_single_evaluation_async(cv_text, profile, iteration + 1)
                if verbose:
                    if result["success"]:
                        total_score = result["scores"].get("total_score", "N/A")
                        print(f"  ✓ Iteration {iteration + 1} completed: Score {total_score}")
                    else:
                        print(f"  ✗ Iteration {iteration + 1} failed: {result['error']}")
                return result
        
        # Run all iterations concurrently (with semaphore limiting parallelism)
        tasks = [bounded_evaluation(i) for i in range(self.iterations_per_config)]
        profile_results = await asyncio.gather(*tasks)
        
        return list(profile_results)

    def run_all_experiments(self, profiles: List[Dict[str, str]] = None, verbose: bool = True) -> Dict[str, Any]:
        """
        Run experiments for all profiles.

        Args:
            profiles: List of profiles to test (defaults to all NAME_VARIATIONS)
            verbose: Whether to print progress

        Returns:
            Complete results including all iterations and summary statistics
        """
        if profiles is None:
            profiles = NAME_VARIATIONS

        start_time = datetime.now()

        if verbose:
            print(f"\n{'#'*70}")
            print(f"# ATS DISCRIMINATION TEST")
            print(f"# Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"# Total profiles: {len(profiles)}")
            print(f"# Iterations per profile: {self.iterations_per_config}")
            print(f"# Total evaluations: {len(profiles) * self.iterations_per_config}")
            print(f"{'#'*70}")

        all_results = []

        for profile in profiles:
            profile_results = self.run_profile_experiment(profile, verbose=verbose)
            all_results.extend(profile_results)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        experiment_data = {
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "model_name": self.model_name,
                "iterations_per_config": self.iterations_per_config,
                "total_profiles": len(profiles),
                "total_evaluations": len(all_results)
            },
            "results": all_results
        }

        if verbose:
            print(f"\n{'#'*70}")
            print(f"# Experiment completed in {duration:.2f} seconds")
            print(f"{'#'*70}\n")

        return experiment_data

    async def run_all_experiments_async(self, profiles: List[Dict[str, str]] = None, verbose: bool = True) -> Dict[str, Any]:
        """
        Run experiments for all profiles asynchronously.

        Args:
            profiles: List of profiles to test (defaults to all NAME_VARIATIONS)
            verbose: Whether to print progress

        Returns:
            Complete results including all iterations and summary statistics
        """
        if profiles is None:
            profiles = NAME_VARIATIONS

        start_time = datetime.now()

        if verbose:
            print(f"\n{'#'*70}")
            print(f"# ATS DISCRIMINATION TEST (ASYNC MODE)")
            print(f"# Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"# Total profiles: {len(profiles)}")
            print(f"# Iterations per profile: {self.iterations_per_config}")
            print(f"# Total evaluations: {len(profiles) * self.iterations_per_config}")
            print(f"# Max concurrent requests: {self.max_concurrent}")
            print(f"{'#'*70}")

        all_results = []

        # Run profiles sequentially (but iterations within each profile are concurrent)
        for profile in profiles:
            profile_results = await self.run_profile_experiment_async(profile, verbose=verbose)
            all_results.extend(profile_results)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        experiment_data = {
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "model_name": self.model_name,
                "iterations_per_config": self.iterations_per_config,
                "max_concurrent": self.max_concurrent,
                "total_profiles": len(profiles),
                "total_evaluations": len(all_results),
                "async_mode": True
            },
            "results": all_results
        }

        if verbose:
            print(f"\n{'#'*70}")
            print(f"# Experiment completed in {duration:.2f} seconds")
            print(f"# Average time per evaluation: {duration / len(all_results):.2f}s")
            print(f"{'#'*70}\n")

        return experiment_data

    def save_results(self, experiment_data: Dict[str, Any], filename: str = None):
        """
        Save experiment results to a JSON file.

        Args:
            experiment_data: Complete experiment data to save
            filename: Output filename (auto-generated if None)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/ats_experiment_results_{timestamp}.json"

        # Create results directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {filename}")
        return filename


def quick_test(iterations: int = 3, num_profiles: int = 2, async_mode: bool = True, max_concurrent: int = 5):
    """
    Run a quick test with fewer iterations and profiles.

    Args:
        iterations: Number of iterations per profile
        num_profiles: Number of profiles to test
        async_mode: Whether to use async/concurrent execution (default: True)
        max_concurrent: Maximum concurrent requests when in async mode (default: 5)
    """
    experiment = ATSExperiment(iterations_per_config=iterations, max_concurrent=max_concurrent)
    profiles_to_test = NAME_VARIATIONS[:num_profiles]
    
    if async_mode:
        results = asyncio.run(experiment.run_all_experiments_async(profiles=profiles_to_test))
    else:
        results = experiment.run_all_experiments(profiles=profiles_to_test)
    
    filename = experiment.save_results(results)
    return results, filename


if __name__ == "__main__":
    # Example: Run a quick test with async mode (much faster!)
    print("Running quick test with 3 iterations and 2 profiles (async mode)...")
    results, filename = quick_test(iterations=3, num_profiles=2, async_mode=True, max_concurrent=5)
    print(f"\nQuick test complete! Results saved to {filename}")
    
    # To run synchronously (slower): quick_test(iterations=3, num_profiles=2, async_mode=False)
