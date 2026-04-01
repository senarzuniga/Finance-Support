"""
Finance Support — Streamlit UI

A proactive financial co-pilot that supports both personal and business
finances. Run with:

    streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv

from agents.finance_agent import FinanceAgent

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Finance Co-Pilot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------


def _init_session() -> None:
    if "agent" not in st.session_state:
        api_key = st.session_state.get("openai_key") or os.getenv("OPENAI_API_KEY")
        st.session_state.agent = FinanceAgent(openai_api_key=api_key)
    if "messages" not in st.session_state:
        st.session_state.messages = []


_init_session()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("💰 Finance Co-Pilot")
    st.caption("Personal · Business · Forecasting · Risk")

    st.divider()

    # OpenAI API key input
    st.subheader("🔑 OpenAI API Key (optional)")
    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-...",
        help="Provide your OpenAI API key to enable AI-enhanced responses. Without it, the system uses a rule-based engine.",
        key="openai_key_input",
    )

    if api_key_input:
        if (
            "agent" not in st.session_state
            or st.session_state.agent._api_key != api_key_input
        ):
            st.session_state.agent = FinanceAgent(openai_api_key=api_key_input)
            st.success("API key set — AI mode active.")
    else:
        st.info("Running in rule-based mode. Add an API key above for AI-enhanced responses.")

    st.divider()

    # Current data summary
    agent: FinanceAgent = st.session_state.agent
    personal = agent.personal
    business = agent.business

    st.subheader("📊 Current Data")

    if personal.has_any_data():
        st.markdown("**Personal Finances**")
        for field, val in personal.data.items():
            if val is not None:
                label = personal.FIELD_LABELS.get(field, field)
                st.markdown(f"- {label}: **{val:,.0f}**")
    else:
        st.caption("No personal data yet.")

    if business.has_any_data():
        st.markdown("**Business Finances**")
        for field, val in business.data.items():
            if val is not None:
                label = business.FIELD_LABELS.get(field, field)
                if isinstance(val, float):
                    st.markdown(f"- {label}: **{val:,.0f}**")
                else:
                    st.markdown(f"- {label}: **{val}**")
    else:
        st.caption("No business data yet.")

    st.divider()

    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.agent.reset_session()
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(
        "💡 **Tip:** Just describe your finances naturally. "
        "For example: *'I earn 3000€/month and spend about 2200€'* or "
        "*'My company makes 50k/month but profits are low.'*"
    )

# ---------------------------------------------------------------------------
# Main chat interface
# ---------------------------------------------------------------------------

st.title("💰 Finance Co-Pilot")
st.caption(
    "Your proactive financial advisor — personal finances, business analysis, "
    "cash flow forecasting and risk assessment."
)

# Welcome message (shown only once)
if not st.session_state.messages:
    welcome = (
        "👋 Hello! I'm your **Finance Co-Pilot** — a proactive financial advisor "
        "that helps with both **personal** and **business** finances.\n\n"
        "I can help you with:\n"
        "- 💼 **Personal budgeting** — income, expenses, savings, debts\n"
        "- 🏢 **Business analysis** — revenue, costs, margins, profitability\n"
        "- 📈 **Cash flow forecasting** — 6-month projections (best/expected/worst)\n"
        "- ⚠️ **Risk assessment** — detect threats and get mitigation strategies\n\n"
        "**Just tell me about your finances and I'll take it from there.**\n\n"
        "---\n"
        "To get started, try one of these:\n"
        "- *'I want to improve my finances'*\n"
        "- *'I earn 2000€/month and spend around 1500€'*\n"
        "- *'My company revenue is 50k/month but profits are low'*\n"
        "- *'Will I run out of money in 6 months?'*"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="💰" if message["role"] == "assistant" else None):
        st.markdown(message["content"])

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

if prompt := st.chat_input("Describe your finances or ask a question…"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and show response
    with st.chat_message("assistant", avatar="💰"):
        with st.spinner("Analysing your finances…"):
            response = st.session_state.agent.chat(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
