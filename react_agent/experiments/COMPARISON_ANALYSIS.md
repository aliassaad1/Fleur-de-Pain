# Experiment Comparison Analysis

## Overview
- **Total Experiments:** 24 (6 configurations × 4 scenarios)
- **Personas:** Friendly Advisor, Strict Expert
- **Temperatures:** 0.2, 0.7, 1.0
- **Scenarios:** Freshness, Custom Cake, Unknown Question, Pre-order

---

## Key Findings from Detailed Results

### 1. **Response Length by Persona**

**Friendly Advisor:**
- Average: ~280 characters
- Style: Conversational, warm, detailed
- Example: "I'd love to help with your custom cake! Just so you know..."

**Strict Expert:**
- Average: ~150 characters (47% shorter!)
- Style: Concise, policy-focused, minimal
- Example: "Custom cakes require 24-hour minimum notice per bakery policy."

**Winner:** Depends on use case
- Customer service: Friendly Advisor (more welcoming)
- High volume/efficiency: Strict Expert (faster responses)

---

### 2. **Temperature Impact**

#### Friendly Advisor (temp comparison):
- **0.2:** "Feel free to check it out when you visit..."
- **0.7:** "We bake fresh batches of bread every 3 hours..."
- **1.0:** "Great question! We update our 'Bake Times' board..."

**Observation:** Higher temps = more variation in phrasing, but still accurate

#### Strict Expert (temp comparison):
- **0.2:** "Current bread availability and next batch timing are not specified..."
- **0.7:** "Fresh batches are made every 3 hours. Please check..."

**Observation:** Less variation - expert stays concise regardless of temp

**Winner:** Temperature 0.7 for balanced creativity + consistency

---

### 3. **Tool Usage**

**Friendly Advisor:**
- Tool calls: Fewer overall
- Behavior: Tries to answer conversationally first
- Unknown questions: Calls `record_feedback` when truly unknown

**Strict Expert:**
- Tool calls: More frequent
- Behavior: Logs uncertainty immediately
- Example: Even for "freshness" question, logged as unknown

**Winner:** Friendly Advisor (better judgment on when tools needed)

---

### 4. **Policy Enforcement**

**Custom Cake Scenario (24h notice rule):**

**Friendly Advisor:**
> "Just so you know, we typically need 24 hours' notice... That said, let me take your details and our team will reach out to see if we can make it work."

**Strict Expert:**
> "Custom cakes require 24-hour minimum notice per bakery policy. Provide details. Team will assess if exception possible."

**Observation:** Both enforce policy, but:
- Friendly: Softens with "typically" and "see if we can make it work"
- Strict: Direct "require" and "assess if exception possible"

**Winner:** Friendly Advisor (customer-centric while still enforcing rules)

---

### 5. **Unknown Questions (Gluten-free sourdough)**

All configurations correctly:
- ✅ Identified question as unanswered in docs
- ✅ Called `record_feedback` tool
- ✅ Offered to collect contact info

**No significant difference** - both personas handle this well

---

## Recommendations

### Best Configuration Overall:
**Friendly Advisor, Temperature 0.7, Top-p 1.0**

**Why:**
1. **Natural conversation flow** - Feels like talking to a real person
2. **Appropriate tool usage** - Calls tools when needed, not excessively
3. **Policy enforcement** - Firm but flexible
4. **Customer satisfaction** - Warm, welcoming, helpful

### When to Use Strict Expert:
- High-volume customer service (faster responses)
- Internal policy enforcement dashboard
- Automated triage system
- When brevity is critical

---

## Sample Comparison - "Custom Cake Tomorrow"

### Friendly Advisor (temp=0.7):
```
I'd love to help with your custom cake! Just so you know, we typically
need 24 hours' notice for custom cakes to ensure we can create something
perfect for you. That said, let me take your details and our team will
reach out via WhatsApp to see if we can make it work. What size cake do
you need, and do you have a flavor preference?
```
**Pros:** Warm, inviting, offers hope
**Cons:** 333 characters (longer response time)

### Strict Expert (temp=0.2):
```
Custom cakes require 24-hour minimum notice per bakery policy. Provide
name, email/WhatsApp, cake details (size, flavor), and pickup time. Team
will assess if exception possible. STOP.
```
**Pros:** Clear, fast, policy-enforced
**Cons:** 184 characters (less personable)

---

## Metrics Summary

| Metric | Friendly Advisor | Strict Expert | Winner |
|--------|-----------------|---------------|---------|
| Avg Response Length | 280 chars | 150 chars | Depends |
| Tool Calls | 4/24 tests | 5/24 tests | Friendly (better judgment) |
| Customer Warmth | High | Low | Friendly |
| Response Speed | Slower | Faster | Strict |
| Policy Adherence | 100% | 100% | Tie |
| Flexibility | Higher | Lower | Friendly |

---

## Conclusion

For **Fleur de Pain bakery customer service**, the **Friendly Advisor with temperature 0.7** is the optimal configuration because:

1. Customers prefer warm, conversational interactions when ordering food
2. Still enforces all policies (24h notice, fresh batches, WhatsApp pre-orders)
3. Appropriate tool usage (doesn't over-log)
4. Creates positive brand experience
5. Balances helpfulness with efficiency

**Temperature 0.7** provides the best balance:
- Not too robotic (temp 0.2)
- Not too creative/risky (temp 1.0)
- Consistent but natural

---

## How to View Full Results

```bash
# View all 24 experiment results with full responses
python view_detailed_results.py

# View summary metrics
cat experiments/runs.csv

# View individual responses
cat experiments/detailed_results.jsonl
```

---

**Generated from:** 24 experiments across 6 configurations and 4 scenarios
**Date:** 2025-10-25
