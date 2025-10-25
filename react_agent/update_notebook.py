"""
Update app.ipynb to include all 4 tools
"""
import json

# Read the notebook
with open('app.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Update the overview cell
overview_cell = """# Fleur de Pain ReAct Agent - C4 Assignment

**Author:** Ali Assaad
**Course:** EECE 503P - Fall 2026
**Framework:** LangGraph

## Overview

This notebook implements a custom ReAct-style agent for Fleur de Pain bakery using:
- **Manual ReAct Loop:** Thought → Action → Observation → Answer (no prebuilt executors)
- **Framework:** LangGraph for state management
- **Multiple Personas:** Friendly Advisor vs. Strict Expert
- **4 Tools:** Complete bakery operations
- **Experiments:** Testing different LLM configurations and prompting strategies

### Use Case
- **Scenario:** Fleur de Pain bakery assistant
- **Goal:** Answer FAQs, enforce policies, collect leads, schedule pickups, process cake orders
- **Audience:** Customers planning purchases
- **Grounding:** PDF and text business documents
- **Constraints:** No invented prices, fresh every 3h, custom cakes need 24h notice

### Tools (All 4)
1. **record_customer_interest** - General lead capture → logs/leads.jsonl
2. **record_feedback** - Unknown questions → logs/feedback.jsonl
3. **schedule_pickup** - Pickup appointments → logs/scheduled_pickups.jsonl
4. **create_cake_order** - Custom cake orders → logs/cake_orders.jsonl
"""

# Find and update the first markdown cell
for cell in notebook['cells']:
    if cell['cell_type'] == 'markdown' and 'Fleur de Pain ReAct Agent' in ''.join(cell['source']):
        cell['source'] = overview_cell.split('\n')
        break

# Add a new test cell for additional tools
additional_tests_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 5.3 Test Additional Tools (schedule_pickup, create_cake_order)\n",
        "\n",
        "Testing the 2 additional tools that were added to match C3 functionality."
    ]
}

additional_tests_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "print(\"Testing Additional Tools:\\n\" + \"=\"*60)\n",
        "\n",
        "# Test schedule_pickup\n",
        "print(\"\\n### Test: schedule_pickup\")\n",
        "result_pickup = run_test(\n",
        "    \"friendly_advisor\",\n",
        "    \"test_1_freshness\",  # Use any test key\n",
        "    config_friendly_07\n",
        ")\n",
        "# Manually test with pickup message\n",
        "llm_call = create_llm_call(model=\"gpt-4o\", temperature=0.7)\n",
        "agent = create_langgraph_agent(llm_call, persona=\"friendly_advisor\", max_turns=10)\n",
        "result = agent.run(\"I want to pick up 2 sourdough loaves tomorrow at 3 PM. My name is David.\", BUSINESS_CONTEXT)\n",
        "print(f\"User: I want to pick up 2 sourdough loaves tomorrow at 3 PM. My name is David.\")\n",
        "print(f\"\\nAgent Response:\\n{result['final_answer']}\")\n",
        "print(f\"\\nTool Calls: {len(result['metadata']['actions_taken'])}\")\n",
        "if result['metadata']['actions_taken']:\n",
        "    for action in result['metadata']['actions_taken']:\n",
        "        print(f\"  - {action['tool']}({action['args']})\")\n",
        "\n",
        "# Test create_cake_order\n",
        "print(\"\\n\" + \"-\"*60)\n",
        "print(\"\\n### Test: create_cake_order\")\n",
        "result2 = agent.run(\"I need a chocolate birthday cake for 20 people next Saturday. I'm Maria, maria@test.com. Write 'Happy Birthday!' on it.\", BUSINESS_CONTEXT)\n",
        "print(f\"User: I need a chocolate birthday cake for 20 people next Saturday...\")\n",
        "print(f\"\\nAgent Response:\\n{result2['final_answer']}\")\n",
        "print(f\"\\nTool Calls: {len(result2['metadata']['actions_taken'])}\")\n",
        "if result2['metadata']['actions_taken']:\n",
        "    for action in result2['metadata']['actions_taken']:\n",
        "        print(f\"  - {action['tool']}({action['args']})\")\n",
        "\n",
        "print(\"\\n\" + \"=\"*60)\n",
        "print(\"✅ Additional tools tested!\")"
    ]
}

# Insert after cell 14 (after the strict expert tests)
insert_index = None
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown' and 'Verify Tool Logs' in ''.join(cell.get('source', [])):
        insert_index = i
        break

if insert_index:
    notebook['cells'].insert(insert_index, additional_tests_code)
    notebook['cells'].insert(insert_index, additional_tests_cell)

# Save the updated notebook
with open('app.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1)

print("[SUCCESS] Notebook updated with all 4 tools!")
print("Restart Jupyter kernel to see changes")
