"""
Run experiments and save DETAILED results including actual responses
This allows comparison of agent outputs across different configurations
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import agent modules
from react_agent.agent import create_langgraph_agent

# Load environment
load_dotenv(Path(__file__).parent.parent / '.env')

def load_business_context():
    """Load business documents."""
    context = ""
    pdf_path = Path(__file__).parent.parent / "me" / "about_business.pdf"
    if pdf_path.exists():
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            context += page.extract_text() + "\n"
        context = "=== Business Profile ===\n" + context + "\n\n"

    txt_path = Path(__file__).parent.parent / "me" / "business_summary.txt"
    if txt_path.exists():
        with open(txt_path, 'r', encoding='utf-8') as f:
            context += "=== Business Summary ===\n" + f.read()

    return context

def create_llm_call(model="gpt-4o", temperature=0.7, top_p=1.0):
    """Create LLM call function."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def llm_call(messages):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=1500
        )
        return response.choices[0].message.content

    return llm_call

# Test scenarios
TEST_SCENARIOS = {
    "freshness": "What breads are fresh now? When is the next batch?",
    "custom_cake": "I need a custom cake for tomorrow at 3 pm.",
    "unknown_question": "Do you have gluten-free sourdough daily?",
    "preorder": "How do I pre-order and get delivery?"
}

# Experiment configurations
EXPERIMENTS = [
    {"persona": "friendly_advisor", "temp": 0.2, "top_p": 1.0, "model": "gpt-4o"},
    {"persona": "friendly_advisor", "temp": 0.7, "top_p": 1.0, "model": "gpt-4o"},
    {"persona": "friendly_advisor", "temp": 1.0, "top_p": 1.0, "model": "gpt-4o"},
    {"persona": "strict_expert", "temp": 0.2, "top_p": 1.0, "model": "gpt-4o"},
    {"persona": "strict_expert", "temp": 0.7, "top_p": 1.0, "model": "gpt-4o"},
    {"persona": "friendly_advisor", "temp": 0.7, "top_p": 0.9, "model": "gpt-4o"},
]

if __name__ == "__main__":
    print("="*70)
    print("DETAILED EXPERIMENT RUNNER")
    print("Saves both metadata AND actual responses for comparison")
    print("="*70)

    business_context = load_business_context()

    # Files to save results
    summary_csv = Path("experiments/runs.csv")
    detailed_jsonl = Path("experiments/detailed_results.jsonl")

    # Load existing data
    summary_data = []

    print(f"\nRunning {len(EXPERIMENTS)} experiments on {len(TEST_SCENARIOS)} scenarios...")
    print(f"Total tests: {len(EXPERIMENTS) * len(TEST_SCENARIOS)}\n")

    experiment_num = 0

    for exp in EXPERIMENTS:
        for scenario_key, user_message in TEST_SCENARIOS.items():
            experiment_num += 1

            print(f"[{experiment_num}/{len(EXPERIMENTS)*len(TEST_SCENARIOS)}] "
                  f"{exp['persona']}, temp={exp['temp']}, scenario={scenario_key}")

            # Create agent
            llm_call = create_llm_call(
                model=exp["model"],
                temperature=exp["temp"],
                top_p=exp["top_p"]
            )
            agent = create_langgraph_agent(llm_call, persona=exp["persona"], max_turns=10)

            # Run agent
            result = agent.run(user_message, business_context)

            # Save to summary CSV
            summary_data.append({
                "timestamp": datetime.now().isoformat(),
                "persona": exp["persona"],
                "temperature": exp["temp"],
                "top_p": exp["top_p"],
                "model": exp["model"],
                "scenario": scenario_key,
                "success": result["metadata"].get("stopped_reason") == "answer_found",
                "turns": result["metadata"].get("turns", 0),
                "tool_calls": len(result["metadata"].get("actions_taken", []))
            })

            # Save DETAILED results to JSONL
            detailed_result = {
                "timestamp": datetime.now().isoformat(),
                "experiment": {
                    "persona": exp["persona"],
                    "temperature": exp["temp"],
                    "top_p": exp["top_p"],
                    "model": exp["model"]
                },
                "scenario": {
                    "key": scenario_key,
                    "user_message": user_message
                },
                "response": {
                    "final_answer": result["final_answer"],
                    "turns": result["metadata"].get("turns", 0),
                    "stopped_reason": result["metadata"].get("stopped_reason"),
                    "actions_taken": result["metadata"].get("actions_taken", [])
                }
            }

            # Append to JSONL
            with open(detailed_jsonl, 'a', encoding='utf-8') as f:
                f.write(json.dumps(detailed_result) + "\n")

            print(f"  -> Response length: {len(result['final_answer'])} chars, "
                  f"Tools: {len(result['metadata'].get('actions_taken', []))}")

    # Save summary CSV
    df = pd.DataFrame(summary_data)
    df.to_csv(summary_csv, index=False)

    print("\n" + "="*70)
    print("RESULTS SAVED:")
    print("="*70)
    print(f"1. Summary: experiments/runs.csv")
    print(f"2. Detailed: experiments/detailed_results.jsonl (with full responses)")
    print("\nTo view detailed results:")
    print("  python view_detailed_results.py")
