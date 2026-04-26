# Finance Co-Pilot 💰

A proactive multi-agent Finance Advisor that supports **personal** and **business** finances. It detects missing data, asks for it step-by-step, and always provides actionable next steps — even with incomplete information.

## Features

- 💼 **Personal Finance Agent** — income vs expenses, savings rate, debt analysis
- 🏢 **Business Finance Agent** — revenue, costs, margins, profitability
- 📈 **Forecasting Agent** — 6-month cash flow projections (best / expected / worst)
- ⚠️ **Risk Agent** — risk level detection with mitigation strategies
- 🤖 **Finance Orchestrator** — routes queries to the right agent and combines outputs
- 💬 **Proactive questioning** — never blocks on missing data; always asks the next question
- 🎨 **Streamlit UI** — clean chat interface with live data sidebar

## Structured Output

Every response follows this mandatory format:

```
### 1. Financial Snapshot
### 2. Missing Information
### 3. Key Risks
### 4. Cash Flow Insight
### 5. Improvement Actions (Immediate / Short-term / Strategic)
### 6. Next Questions
```

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Configure OpenAI API key

Copy `.env.example` to `.env` and add your key for AI-enhanced responses.  
The app also works in **rule-based mode** without an API key.

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

### 3. Run the app

```bash
streamlit run app.py
```

## Project Structure

```
Finance-Support/
├── agents/
│   ├── finance_agent.py           # Main orchestrator
│   ├── personal_finance_agent.py  # Personal finance tracking & analysis
│   ├── business_finance_agent.py  # Business finance analysis
│   ├── forecasting_agent.py       # Cash flow forecasting
│   └── risk_agent.py              # Risk detection & mitigation
├── app.py                         # Streamlit UI
├── requirements.txt
└── .env.example
```

## Example Queries

| Input | What happens |
|-------|-------------|
| *"I want to improve my finances"* | Agent asks structured questions + provides starter actions |
| *"I earn 2000€/month and spend around 1500€"* | Snapshot + risk analysis + 6-month forecast |
| *"My company revenue is 50k/month but profits are low"* | Cost analysis + margin insights + improvement plan |
| *"Will I run out of money in 6 months?"* | 3-scenario forecast + liquidity warnings |

## Comprehensive Usage Examples

### Personal Finance Agent

#### Example 1: Basic Income and Expense Analysis

**Input:**
```
I earn 3000€/month and my expenses are 2500€/month.
```
**Expected Output:**
- Financial Snapshot: Income vs Expenses
- Key Risks: High expense ratio
- Improvement Actions: Suggestions to reduce expenses

#### Example 2: Savings Rate Calculation

**Input:**
```
My monthly income is 4000€ and I save 500€.
```
**Expected Output:**
- Financial Snapshot: Savings rate calculation
- Improvement Actions: Increase savings rate

### Business Finance Agent

#### Example 1: Revenue and Cost Analysis

**Input:**
```
Our revenue is 100k/month, but costs are 80k.
```
**Expected Output:**
- Financial Snapshot: Revenue vs Costs
- Key Risks: Low profit margin
- Improvement Actions: Cost reduction strategies

### Forecasting Agent

#### Example 1: Cash Flow Projection

**Input:**
```
Project cash flow for the next 6 months.
```
**Expected Output:**
- Cash Flow Insight: Best, expected, and worst-case scenarios

### Risk Agent

#### Example 1: Risk Assessment

**Input:**
```
Assess risks for my current financial plan.
```
**Expected Output:**
- Key Risks: Identified risks with mitigation strategies

These examples are designed to guide users through typical interactions with the Finance Co-Pilot, ensuring they understand how to leverage each agent effectively.
