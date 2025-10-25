instruction_c4.md — Build & Evaluate a Custom ReAct Agent (using your “Fleur de Pain” project)

This **SINGLE** file is your master plan for C4. It tells you exactly what to build, how to structure the repo, what experiments to run, how to test, how to write the **PDF** report, and what to submit so you fully meet the rubric.

0. What C4 is asking for

You will extend your previous business chatbot into a ReAct-style agent (Thought → Action → Observation → Answer) in one chosen framework: LangGraph, CrewAI, or Autogen. You must implement the loop yourself (do not use prebuilt agent executors). Create multiple personas, vary **LLM** configurations (temperature, model, top-p, etc.), and evaluate which combination works best. Include a reflection.

You may reuse your previous bakery scenario “Fleur de Pain.”

You must:

Define your use case (goal, audience, tools, constraints).

Write your own ReAct logic (system prompt + tool descriptions, detect actions, execute tool, feed observation, parse/stopping).

Implement using exactly one framework (LangGraph, CrewAI, or Autogen).

Test multiple personas and multiple configurations, then reflect on results.

1. Repo layout

You can keep working inside your existing repo or create a new one. Suggested structure:

react_agent/

me/

about_business.pdf (from C3)

business_summary.txt (from C3)

agent/

personas.py (system prompts for multiple personas)

tools.py (Python tool functions)

react_loop.py (manual ReAct controller: Thought → Action → Observation → Answer)

framework_impl.py (your chosen framework wiring)

experiments/

runs.csv (logged results of persona/config experiments)

notes.md (observations during testing)

app.ipynb (main notebook: demos + reflection + final **PDF** export)

app.py (optional: **CLI**/Gradio wrapper to demo agent)

requirements.txt

**README**.md

2. Use case definition (reuse bakery)

Fill this explicitly in your notebook or **README**:

Scenario: Fleur de Pain bakery assistant (based on your C3 files).

Goal: Answer bakery FAQs, explain the bake-time policy, collect custom-cake leads, and log unknown questions.

Audience: Customers planning purchases or asking about availability.

Tools:

record_customer_interest(email, name, message) → append **JSON** to logs/leads.jsonl (one **JSON** per line).

record_feedback(question) → append **JSON** to logs/feedback.jsonl.

Constraints: Do not invent prices; fresh every 3 hours; custom cakes require 24-hour notice; pre-order via WhatsApp; 2-hour delivery windows.

Grounding: The agent must use /me/about_business.pdf and /me/business_summary.txt as its source of truth.

3. Tools to implement

Create agent/tools.py with two functions:

record_customer_interest(email, name, message)

Purpose: store potential customer leads (orders/inquiries).

Behavior: append a **JSON** line with fields ts (**UTC** **ISO**), email, name, message to logs/leads.jsonl.

Ensure a logs/ directory exists; create it at runtime if missing.

record_feedback(question)

Purpose: log unknown questions or general feedback.

Behavior: append a **JSON** line with fields ts (**UTC** **ISO**) and question to logs/feedback.jsonl.

**JSONL** examples (one line per entry):

{*ts*: ***2025**-10-**18T12**:34:**56Z***, *email*: *[ana@example.com](mailto:ana@example.com) *, *name*: *Ana Darwish*, *message*: *Cake for 12 people, 1pm pickup Friday*}

{*ts*: ***2025**-10-**18T12**:40:**21Z***, *question*: *Do you have gluten-free sourdough daily?*}

4. Personas (at least two)

Create agent/personas.py with clearly different voices:

### Friendly Advisor

Voice: warm, encouraging, plain language, concise.

Policies to enforce: fresh every 3 hours; custom cakes need 24h; WhatsApp pre-orders; 2-hour delivery windows.

Lead collection: when appropriate, collect name, email/WhatsApp, what they want, desired date/time, then propose calling record_customer_interest.

Unknowns: propose calling record_feedback(question=…).

ReAct format to follow in the model’s output:

Thought: …

Action: tool_name({*field*:*value*})

Observation: …

Answer: …

Stop after Answer.

### Strict Expert

Voice: precise, policy-first, minimal wording.

Enforce the same policies.

Collect contact info before promising anything.

Use the same tools and ReAct format. Stop after Answer.

5. Manual ReAct controller

Create agent/react_loop.py with a framework-agnostic control loop that:

Calls the **LLM** to produce text.

Appends the model’s text to the conversation.

Checks if the model has produced a final Answer; if yes, stop and return the messages.

If not final, detect an Action line of the form: Action: tool_name({...}).

If an action is present, execute the corresponding Python function (from tools.py) with parsed **JSON** arguments.

Capture the tool result and add it back to the conversation as an Observation line.

Loop up to a safety max_turns; if the model doesn’t produce an action, ask it to provide the final Answer.

Implementation tips:

Define a parser that extracts the tool name and **JSON** arguments from the Action line.

Define stopping criteria (detect “Answer:” or similar).

Treat tool errors gracefully by returning an Observation that includes the error message and letting the model continue.

6. Framework integration (pick exactly one)

Create agent/framework_impl.py and wire your loop into one of the following:

LangGraph: map Thought, Action, Observation, Answer states as nodes with conditional edges; keep your custom loop controlling transitions.

CrewAI: define crew roles for your personas; coordinate tool usage through your loop handler.

Autogen: set up dialog agents for personas; parse messages for actions and execute tools between turns.

Important: do not use a prebuilt agent executor; the ReAct logic must be yours.

7. **LLM** wrapper and grounding

In app.ipynb:

Load /me/about_business.pdf and /me/business_summary.txt, and inject their content into a system or context message each turn.

Provide a simple llm_call(messages) → text function for your chosen model/provider (OpenAI, Anthropic, etc.).

Optionally add a Gradio interface for demonstrations. Keep it aligned with your custom loop (not a generic agent runner).

8. Experiments (personas and configurations)

Create experiments/runs.csv and systematically test:

Personas: Friendly Advisor vs. Strict Expert (add more if desired).

Prompting variants: with vs. without chain-of-thought style cues, zero-shot vs. few-shot exemplars, system vs. in-message instructions.

Configurations: temperature (e.g., 0.2 and 0.7), top-p (e.g., 1.0 and 0.9), model choice, max tokens.

Suggested **CSV** columns:

timestamp, persona, temperature, top_p, model, prompt_style, task, success, notes, tool_calls

Take short notes in experiments/notes.md about surprising outcomes, errors, or behavior changes.

9. Test protocol (scripted conversations)

Use these four end-to-end tests to verify the loop, tools, and policies:

Freshness and bake times

User: “What breads are fresh now? When is the next batch?”

Expected: mentions the every-3-hours policy; grounded in business docs; no invented prices.

Persona differences: Friendly gives more guidance; Expert is concise and policy-focused.

Custom cake for tomorrow

User: “I need a custom cake for tomorrow at 3 pm.”

Expected: confirms 24-hour notice rule; collects name, email/WhatsApp, size, flavor, filling, pickup time.

Action: record_customer_interest({...}).

Verification: new line appears in logs/leads.jsonl with the data.

Unknown question

User: “Do you have gluten-free sourdough daily?” (not guaranteed in docs)

Expected: explains uncertainty; Action: record_feedback({*question*: …}).

Verification: new line appears in logs/feedback.jsonl.

Pre-order channel

User: “How do I pre-order and get delivery?”

Expected: WhatsApp channel; same-day pickup while stocks last; 2-hour delivery windows; grounded in docs.

10. Reflection (in the notebook and export to **PDF**)

Write your reflection at the end of app.ipynb and export to C4_Reflection.pdf. Answer these questions clearly:

Which persona was most helpful or natural, and why?

Which prompt and configuration worked best for this use case, and why?

How well did the agent reason and use tools (successes and failures)?

What were the biggest challenges building the loop?

How to make the **PDF** quickly:

In Jupyter, use File → Save and Export As → **PDF** (if available), or export to **HTML** and print to **PDF**.

Or use nbconvert: jupyter nbconvert --to pdf app.ipynb

Alternatively, write your reflection in a markdown file and convert with Pandoc: pandoc reflection.md -o C4_Reflection.pdf

Ensure the **PDF** includes: use-case summary, framework choice, ReAct loop explanation, personas and configurations tested, a small results table from runs.csv, and the answers to the reflection questions.

11. Submission checklist

Use-case summary included (in **README** or notebook intro) and C4_Reflection.pdf with answers and results.

Manual ReAct loop implemented (no prebuilt executor).

At least two personas and logs comparing configurations and prompt styles.

Tools working: record_customer_interest and record_feedback (**JSONL** entries created).

Demo notebook (app.ipynb) shows the four scripted tests and their outcomes.

Optional: Gradio demo (app.py) aligned with your custom loop.

Repo is runnable from a clean clone with clear requirements.txt.

12. Quick start commands (template)

Create and activate a virtual environment (optional): python -m venv .venv and then activate it.

Install dependencies: pip install -r requirements.txt

Run the notebook: jupyter lab (or jupyter notebook)

Optional Gradio app: python app.py

13. Tips to score full points

Be explicit in your code about the ReAct format: Thought, Action, Observation, Answer. Include a tiny few-shot example in the persona/system prompt to steer the model.

Log everything: persona, temperature, top-p, model, success, notes. Screenshots of logs/*.jsonl in the notebook help prove tool usage.

Always ground answers in /me/about_business.pdf and /me/business_summary.txt.

Keep personas clearly different; show why one is better in your Reflection **PDF**.