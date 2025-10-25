# Fleur de Pain ReAct Agent - C4 Assignment

**Author:** Ali Assaad
**Course:** EECE 503P - Fall 2026
**Framework:** LangGraph
**Assignment:** C4 - Build & Evaluate a Custom ReAct Agent

## Overview

This project implements a **manual ReAct-style agent** for Fleur de Pain bakery using the **Thought → Action → Observation → Answer** reasoning pattern. The agent does NOT use prebuilt agent executors; instead, it implements custom reasoning logic.

### Key Features

- **Manual ReAct Loop:** Custom controller implementing T→A→O→A cycle
- **Framework:** LangGraph for state management (without prebuilt executors)
- **Multiple Personas:** Friendly Advisor vs. Strict Expert
- **Tools:** Lead capture and feedback logging to JSONL files
- **Business Grounding:** All responses based on PDF and text documents
- **Experiments:** Testing multiple LLM configurations (temperature, top-p, model)
- **Comprehensive Reflection:** Analysis in Jupyter notebook + PDF export

## Use Case Definition

**Scenario:** Fleur de Pain bakery customer assistant

**Goal:**
- Answer bakery FAQs
- Explain bake-time policies
- Collect custom cake leads
- Log unknown questions

**Audience:** Customers planning purchases or asking about availability

**Tools:**
1. `record_customer_interest(email, name, message)` - Append lead to `logs/leads.jsonl`
2. `record_feedback(question)` - Append feedback to `logs/feedback.jsonl`

**Constraints:**
- Do NOT invent prices or availability
- Fresh batches every 3 hours
- Custom cakes require 24-hour notice
- Pre-orders via WhatsApp only
- 2-hour delivery windows (when available)

**Grounding:** All responses must reference `me/about_business.pdf` and `me/business_summary.txt`

## Project Structure

```
react_agent/
├── agent/
│   ├── __init__.py          # Package initialization
│   ├── tools.py             # Tool functions (record_customer_interest, record_feedback)
│   ├── personas.py          # System prompts for Friendly Advisor & Strict Expert
│   ├── react_loop.py        # Manual ReAct controller (NO prebuilt executors)
│   └── framework_impl.py    # LangGraph integration
├── experiments/
│   ├── runs.csv             # Experiment results (persona, config, success, notes)
│   └── notes.md             # Detailed observations during testing
├── app.ipynb                # Main demo notebook with reflection
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd react_agent
pip install -r requirements.txt
```

**Key Dependencies:**
- `openai>=1.12.0` - LLM API
- `langgraph>=0.0.20` - State machine framework
- `PyPDF2>=3.0.0` - PDF reading
- `jupyter>=1.0.0` - Notebook environment
- `pandas>=2.0.0` - Experiment tracking

### 2. Set Up Environment

Create a `.env` file in the parent directory with your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run the Notebook

```bash
jupyter notebook app.ipynb
```

Run all cells to:
- Load business context
- Test both personas
- Run 4 required test scenarios
- Execute experiments with different configurations
- View the reflection and results

### 4. Export Reflection to PDF

**Option A - Jupyter Menu:**
```
File → Save and Export Notebook As → PDF
```

**Option B - Command Line:**
```bash
jupyter nbconvert --to pdf app.ipynb --output C4_Reflection.pdf
```

## Architecture

### Manual ReAct Loop (`react_loop.py`)

The core of this project is the custom ReAct controller:

```python
class ReActController:
    def run(self, messages):
        for turn in range(max_turns):
            # 1. Call LLM
            response = self.llm_call(messages)

            # 2. Check for final Answer
            if self._has_final_answer(response):
                return extract_answer(response)

            # 3. Detect Action
            action = self._detect_action(response)
            if action:
                tool_name, tool_args = action

                # 4. Execute Tool
                result = self._execute_tool(tool_name, tool_args)

                # 5. Add Observation
                messages.append({"role": "user", "content": f"Observation: {result}"})

        return final_answer
```

**Key Methods:**
- `_has_final_answer()`: Detects "Answer:" marker
- `_detect_action()`: Parses `Action: tool_name({...})` using regex
- `_execute_tool()`: Calls Python function, handles errors gracefully
- Stops when Answer found or max_turns reached

### LangGraph Integration (`framework_impl.py`)

LangGraph provides state management while our custom loop handles reasoning:

```python
class LangGraphReActAgent:
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("process_message", self._process_with_react_loop)
        workflow.set_entry_point("process_message")
        workflow.add_edge("process_message", END)
        return workflow.compile()
```

**Why LangGraph?**
- Lightweight and flexible
- Doesn't force prebuilt agent patterns
- Provides useful state typing
- Easy to debug

We use a **single node** that runs our custom ReActController internally.

### Personas (`personas.py`)

**Friendly Advisor:**
- Warm, encouraging, conversational
- Patient with lead collection
- Offers to check with team for exceptions
- Temperature 0.7 works best

**Strict Expert:**
- Precise, policy-first, minimal words
- Demands details upfront
- No exceptions offered
- Temperature 0.2 works best

Both follow the same ReAct format with few-shot examples in the prompt.

## Test Scenarios

### Test 1: Freshness and Bake Times
**Input:** "What breads are fresh now? When is the next batch?"
**Expected:** Mentions 3-hour policy, grounded in docs, no invented prices

### Test 2: Custom Cake for Tomorrow
**Input:** "I need a custom cake for tomorrow at 3 pm."
**Expected:** Confirms 24h notice, collects details, calls `record_customer_interest`

### Test 3: Unknown Question
**Input:** "Do you have gluten-free sourdough daily?"
**Expected:** Explains uncertainty, calls `record_feedback`

### Test 4: Pre-order Channel
**Input:** "How do I pre-order and get delivery?"
**Expected:** WhatsApp channel, 2-hour windows, grounded in docs

## Experiments

Configurations tested:

| Persona          | Temp | Top-P | Model  | Style   |
|------------------|------|-------|--------|---------|
| Friendly Advisor | 0.2  | 1.0   | gpt-4o | default |
| Friendly Advisor | 0.7  | 1.0   | gpt-4o | default |
| Strict Expert    | 0.2  | 1.0   | gpt-4o | default |
| Strict Expert    | 0.7  | 1.0   | gpt-4o | default |
| Friendly Advisor | 0.7  | 0.9   | gpt-4o | default |

**Results logged in:** `experiments/runs.csv`
**Observations in:** `experiments/notes.md`

## Reflection Highlights

### Best Configuration
**Winner:** Friendly Advisor, temp=0.7, top_p=1.0, GPT-4o

**Why:**
- Natural conversation flow
- Reliable policy adherence
- Appropriate tool calling
- Customer-friendly tone

### Biggest Challenges
1. **Parsing Action calls** - LLMs don't always format JSON perfectly
2. **Stopping criteria** - Knowing when reasoning is complete
3. **Observation injection** - Making tool results usable by LLM
4. **Prompt engineering** - Consistent ReAct format adherence

### Key Learnings
- Few-shot examples are critical for format adherence
- Temperature tuning is use-case specific
- Error handling must be robust
- Manual loops provide fine-grained control

**Full reflection available in:** `app.ipynb` (Section 8) and `C4_Reflection.pdf`

## Tool Logs

After running tests, check:

```bash
cat ../logs/leads.jsonl       # Customer leads
cat ../logs/feedback.jsonl    # Unknown questions
```

Example lead:
```json
{"ts": "2025-10-20T14:30:00Z", "email": "ana@example.com", "name": "Ana Darwish", "message": "Cake for 12 people, 1pm pickup Friday"}
```

## Assignment Rubric Compliance

- ✅ **Use case defined** - Bakery assistant scenario clearly documented
- ✅ **Manual ReAct loop** - Custom controller in `react_loop.py`, NO prebuilt executors
- ✅ **Framework integration** - LangGraph in `framework_impl.py`
- ✅ **Multiple personas** - Friendly Advisor vs. Strict Expert
- ✅ **Tools implemented** - `record_customer_interest` and `record_feedback` with JSONL logging
- ✅ **Experiments logged** - `runs.csv` with persona/config/results
- ✅ **4 test scenarios** - All tested in notebook
- ✅ **Business grounding** - PDF and TXT documents loaded and used
- ✅ **Reflection PDF** - Comprehensive analysis in notebook, exportable to PDF
- ✅ **Runnable from clone** - Clear setup instructions

## Files to Submit

1. ✅ `react_agent/` - Complete directory
2. ✅ `me/about_business.pdf` - Business documents
3. ✅ `me/business_summary.txt` - Business summary
4. ✅ `app.ipynb` - Demo notebook with reflection
5. ✅ `C4_Reflection.pdf` - Exported from notebook
6. ✅ `experiments/runs.csv` - Experiment results
7. ✅ `logs/leads.jsonl` - Example lead logs
8. ✅ `logs/feedback.jsonl` - Example feedback logs

## Next Steps

Potential enhancements:
- Add more personas (Sales Expert, Technical Advisor)
- Implement conversation memory for multi-turn dialogs
- Add more tools (check_inventory, calculate_price, schedule_delivery)
- Deploy with Gradio for live customer demo
- Implement RAG for larger business document sets
- Add evaluation metrics (tool call accuracy, policy compliance rate)

## License

Educational project for EECE 503P - Fall 2026

## Author

Ali Assaad - AUB Student

---

