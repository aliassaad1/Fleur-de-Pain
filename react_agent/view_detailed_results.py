"""
View detailed experiment results with actual responses
Allows easy comparison between configurations
"""

import json
from pathlib import Path
from collections import defaultdict

def view_results():
    """Display detailed results grouped by scenario."""

    detailed_file = Path("experiments/detailed_results.jsonl")

    if not detailed_file.exists():
        print("No detailed results found. Run: python run_detailed_experiments.py")
        return

    # Load all results
    results = []
    with open(detailed_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    print("="*80)
    print(f"DETAILED EXPERIMENT RESULTS ({len(results)} total)")
    print("="*80)

    # Group by scenario
    by_scenario = defaultdict(list)
    for r in results:
        scenario_key = r['scenario']['key']
        by_scenario[scenario_key].append(r)

    # Display by scenario
    for scenario_key, scenario_results in by_scenario.items():
        print(f"\n\n{'='*80}")
        print(f"SCENARIO: {scenario_key}")
        print(f"User Message: {scenario_results[0]['scenario']['user_message']}")
        print(f"{'='*80}\n")

        for i, result in enumerate(scenario_results, 1):
            exp = result['experiment']
            resp = result['response']

            print(f"\n--- Configuration {i} ---")
            print(f"Persona: {exp['persona']}")
            print(f"Temperature: {exp['temperature']}, Top-p: {exp['top_p']}")
            print(f"Turns: {resp['turns']}, Tool Calls: {len(resp['actions_taken'])}")

            if resp['actions_taken']:
                print("Tools Used:")
                for action in resp['actions_taken']:
                    print(f"  - {action['tool']}()")

            print(f"\nAgent Response:")
            print("-" * 80)
            print(resp['final_answer'])
            print("-" * 80)

    print("\n\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)

    # Show average response lengths by persona
    persona_stats = defaultdict(list)
    for r in results:
        persona = r['experiment']['persona']
        response_len = len(r['response']['final_answer'])
        persona_stats[persona].append(response_len)

    print("\nAverage Response Length by Persona:")
    for persona, lengths in persona_stats.items():
        avg_len = sum(lengths) / len(lengths)
        print(f"  {persona}: {avg_len:.0f} characters")

    # Show tool usage by persona
    print("\nTool Usage by Persona:")
    persona_tools = defaultdict(int)
    for r in results:
        persona = r['experiment']['persona']
        tools = len(r['response']['actions_taken'])
        persona_tools[persona] += tools

    for persona, total_tools in persona_tools.items():
        print(f"  {persona}: {total_tools} total tool calls")

if __name__ == "__main__":
    view_results()
