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
