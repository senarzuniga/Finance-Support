
"""
Finance Agent — main orchestrator.

Routes user queries to the appropriate sub-agents, combines their
outputs and (optionally) uses the OpenAI API to produce a polished,
beginner-friendly response in the mandatory structured format.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from .business_finance_agent import BusinessFinanceAgent
from .forecasting_agent import ForecastingAgent
from .personal_finance_agent import PersonalFinanceAgent
from .risk_agent import RiskAgent

try:
    from openai import OpenAI  # type: ignore

    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


# ---------------------------------------------------------------------------
# Keyword routing tables
# ---------------------------------------------------------------------------

_PERSONAL_KEYWORDS = {
    "income", "salary", "wage", "earn", "expenses", "spending", "savings",
    "save", "debt", "loan", "budget", "personal", "home finances",
    "money", "rent", "mortgage", "bills", "groceries", "monthly",
}

_BUSINESS_KEYWORDS = {
    "revenue", "clients", "customers", "business", "company", "profit",
    "margin", "sales", "turnover", "costs", "pricing", "b2b", "startup",
    "invoice", "overhead", "fixed costs", "variable costs",
}

_FORECAST_KEYWORDS = {
    "forecast", "future", "next month", "projection", "predict",
    "will i", "run out", "months", "years", "plan ahead",
}

_RISK_KEYWORDS = {
    "risk", "danger", "worry", "concerned", "afraid", "stable", "stability",
    "secure", "emergency", "crisis", "problem", "issue",
}


def _detect_context(text: str) -> Tuple[bool, bool, bool, bool]:
    """
    Analyze the input text to determine the context.

    Returns a tuple of booleans indicating whether the text matches
    personal, business, forecast, or risk contexts.

    :param text: The input text to analyze.
    :return: A tuple (is_personal, is_business, is_forecast, is_risk).
    """
    lower = text.lower()

    def matches(kw_set: set) -> bool:
        """Check if any keyword in the set is present in the text."""
        for kw in kw_set:
            if kw in lower:
                return True
        return False

    return (
        matches(_PERSONAL_KEYWORDS),
        matches(_BUSINESS_KEYWORDS),
        matches(_FORECAST_KEYWORDS),
        matches(_RISK_KEYWORDS),
    )


# ---------------------------------------------------------------------------
# Finance Agent (orchestrator)
# ---------------------------------------------------------------------------


class FinanceAgent:
    """
    Top-level finance orchestrator.

    Maintains session state for personal and business data models and
    dispatches to sub-agents based on query intent.
    """

    def __init__(self, openai_api_key: Optional[str] = None) -> None:
        """
        Initialize the FinanceAgent with optional OpenAI API key.

        :param openai_api_key: API key for OpenAI, if available.
        """
        self.personal = PersonalFinanceAgent()
        self.business = BusinessFinanceAgent()
        self.forecaster = ForecastingAgent()
        self.risk = RiskAgent()

        self._api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self._client: Optional[Any] = None
        if _OPENAI_AVAILABLE and self._api_key:
            self._client = OpenAI(api_key=self._api_key)

        self._conversation_history: List[Dict[str, str]] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """
        Process a user message and return a structured finance response.

        If an OpenAI API key is configured the response is enhanced by the
        LLM; otherwise a purely rule-based response is generated.

        :param user_message: The message from the user.
        :return: A structured response based on the message.
        """
        self._conversation_history.append({"role": "user", "content": user_message})

        # Detect intent
        is_personal, is_business, is_forecast, is_risk = _detect_context(user_message)

        # If nothing matches → assume personal (most common beginner case)
        if not any([is_personal, is_business, is_forecast, is_risk]):
            is_personal = True

        # Extract data from the user message
        if is_personal:
            extracted = self.personal.extract_from_text(user_message)
            if extracted:
                self.personal.update_data(extracted)

        if is_business:
            extracted = self.business.extract_from_text(user_message)
            if extracted:
                self.business.update_data(extracted)

        # Build structured output
        response = self._build_response(
            user_message,
            is_personal=is_personal,
            is_business=is_business,
            is_forecast=is_forecast,
            is_risk=is_risk,
        )

        self._conversation_history.append({"role": "assistant", "content": response})
        return response

    # ------------------------------------------------------------------
    # Response builder
    # ------------------------------------------------------------------

    def _build_response(
        self,
        user_message: str,
        is_personal: bool,
        is_business: bool,
        is_forecast: bool,
        is_risk: bool,
    ) -> str:
        """
        Assemble the structured 6-section finance response.

        :param user_message: The original user message.
        :param is_personal: Whether the message relates to personal finance.
        :param is_business: Whether the message relates to business finance.
        :param is_forecast: Whether the message relates to forecasting.
        :param is_risk: Whether the message relates to risk assessment.
        :return: A structured response string.
        """

        sections: Dict[str, str] = {}

        # ----------------------------------------------------------------
        # Section 1 — Financial Snapshot
        # ----------------------------------------------------------------
        snapshot_parts: List[str] = []
        if is_personal and self.personal.has_any_data():
            snapshot_parts.append("**Personal Finances**\n" + self.personal.snapshot_text())
        if is_business and self.business.has_any_data():
            snapshot_parts.append("**Business Finances**\n" + self.business.snapshot_text())

        if not snapshot_parts:
            sections["snapshot"] = (
                "_No financial data captured yet — answers to the questions below will "
                "help me build your snapshot._"
            )
        else:
            sections["snapshot"] = "\n\n".join(snapshot_parts)

        # ----------------------------------------------------------------
        # Section 2 — Missing Information
        # ----------------------------------------------------------------
        missing_parts: List[str] = []
        if is_personal:
            missing_parts.append(self.personal.missing_info_text())
        if is_business:
            missing_parts.append(self.business.missing_info_text())
        if missing_parts:
            sections["missing"] = "\n\n".join(missing_parts)
        else:
            sections["missing"] = "_I have all the data I need to complete your analysis._"

        # ----------------------------------------------------------------
        # Section 3 — Key Risks
        # ----------------------------------------------------------------
        risk_texts: List[str] = []
        if is_personal and (
            self.personal.data["income"] or self.personal.data["fixed_expenses"]
        ):
            assessment = self.risk.assess_personal(
                income=self.personal.data["income"],
                fixed_expenses=self.personal.data["fixed_expenses"],
                variable_expenses=self.personal.data["variable_expenses"],
                savings=self.personal.data["savings"],
                debts=self.personal.data["debts"],
            )
            risk_texts.append("**Personal Finance Risks**\n" + self.risk.risk_text(assessment))

        if is_business and (
            self.business.data["revenue"] or self.business.data["fixed_costs"]
        ):
            assessment = self.risk.assess_business(
                revenue=self.business.data["revenue"],
                fixed_costs=self.business.data["fixed_costs"],
                variable_costs=self.business.data["variable_costs"],
                clients=self.business.data["clients"],
            )
            risk_texts.append("**Business Finance Risks**\n" + self.risk.risk_text(assessment))

        if not risk_texts:
            sections["risks"] = (
                "_Risk assessment will be available once you share some financial figures._"
            )
        else:
            sections["risks"] = "\n\n".join(risk_texts)

        # Additional sections would be added here...

        # Combine all sections into a final response
        return "\n\n".join(f"**{title}**\n{content}" for title, content in sections.items())
