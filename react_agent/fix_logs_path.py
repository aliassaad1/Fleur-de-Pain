"""
Fix notebook to read from react_agent/logs instead of parent ../logs
"""
import json

# Read the notebook
with open('app.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find the cell with read_jsonl function
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        # Check if this is the "Verify Tool Logs" cell
        if 'read_jsonl' in source and ('logs/leads' in source or '../logs/leads' in source):
            print(f"Found the cell at index {i}")

            # Create properly formatted source as list of lines
            new_source = [
                "def read_jsonl(file_path):\n",
                "    \"\"\"Read JSONL file and return list of dictionaries.\"\"\"\n",
                "    if not Path(file_path).exists():\n",
                "        return []\n",
                "    \n",
                "    with open(file_path, 'r') as f:\n",
                "        return [json.loads(line) for line in f if line.strip()]\n",
                "\n",
                "# Check ALL 4 log files from react_agent/logs directory\n",
                "print(\"=\"*60)\n",
                "print(\"Checking react_agent/logs directory (C4 project)\")\n",
                "print(\"=\"*60)\n",
                "\n",
                "# Check leads.jsonl\n",
                "leads = read_jsonl(\"logs/leads.jsonl\")\n",
                "print(f\"\\n1. Leads captured: {len(leads)}\")\n",
                "if leads:\n",
                "    print(\"\\nLatest lead:\")\n",
                "    print(json.dumps(leads[-1], indent=2))\n",
                "\n",
                "# Check feedback.jsonl\n",
                "feedback = read_jsonl(\"logs/feedback.jsonl\")\n",
                "print(f\"\\n2. Feedback logged: {len(feedback)}\")\n",
                "if feedback:\n",
                "    print(\"\\nLatest feedback:\")\n",
                "    print(json.dumps(feedback[-1], indent=2))\n",
                "\n",
                "# Check scheduled_pickups.jsonl\n",
                "pickups = read_jsonl(\"logs/scheduled_pickups.jsonl\")\n",
                "print(f\"\\n3. Scheduled pickups: {len(pickups)}\")\n",
                "if pickups:\n",
                "    print(\"\\nLatest pickup:\")\n",
                "    print(json.dumps(pickups[-1], indent=2))\n",
                "\n",
                "# Check cake_orders.jsonl\n",
                "cakes = read_jsonl(\"logs/cake_orders.jsonl\")\n",
                "print(f\"\\n4. Cake orders: {len(cakes)}\")\n",
                "if cakes:\n",
                "    print(\"\\nLatest cake order:\")\n",
                "    print(json.dumps(cakes[-1], indent=2))\n",
                "\n",
                "print(\"\\n\" + \"=\"*60)\n",
                "print(f\"Total entries: {len(leads) + len(feedback) + len(pickups) + len(cakes)}\")\n",
                "print(\"=\"*60)"
            ]

            cell['source'] = new_source
            print("Updated cell with properly formatted source!")
            break

# Save the updated notebook
with open('app.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1)

print("\n[SUCCESS] Notebook fixed!")
print("Refresh Jupyter and restart kernel to see changes")
