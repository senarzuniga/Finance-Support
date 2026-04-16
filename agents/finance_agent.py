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
    """Return (is_personal, is_business, is_forecast, is_risk)."""
    lower = text.lower()

    def matches(kw_set: set) -> bool:
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
        """Assemble the structured 6-section finance response."""

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

        # ----------------------------------------------------------------
        # Section 4 — Cash Flow Insight
        # ----------------------------------------------------------------
        cash_flow_parts: List[str] = []

        if is_personal or is_forecast:
            income = self.personal.data.get("income")
            total_exp_p = (self.personal.data.get("fixed_expenses") or 0) + (
                self.personal.data.get("variable_expenses") or 0
            )
            savings = self.personal.data.get("savings")

            if income or total_exp_p:
                cash_flow_parts.append(
                    self.forecaster.forecast_text(
                        monthly_income=income,
                        monthly_expenses=total_exp_p or None,
                        current_savings=savings,
                        months=6,
                    )
                )

        if is_business or is_forecast:
            revenue = self.business.data.get("revenue")
            total_costs_b = (self.business.data.get("fixed_costs") or 0) + (
                self.business.data.get("variable_costs") or 0
            )
            if revenue or total_costs_b:
                cash_flow_parts.append(
                    "**Business Cash Flow**\n"
                    + self.forecaster.forecast_text(
                        monthly_income=revenue,
                        monthly_expenses=total_costs_b or None,
                        current_savings=None,
                        months=6,
                    )
                )

        if not cash_flow_parts:
            sections["cash_flow"] = (
                "_Share your income and expenses and I will project your cash flow "
                "over the next 6 months._"
            )
        else:
            sections["cash_flow"] = "\n\n".join(cash_flow_parts)

        # ----------------------------------------------------------------
        # Section 5 — Improvement Actions
        # ----------------------------------------------------------------
        actions: Dict[str, List[str]] = {
            "immediate": [],
            "short_term": [],
            "strategic": [],
        }

        if is_personal and self.personal.has_any_data():
            analysis = self.personal.analyze()
            for bucket in actions:
                actions[bucket].extend(analysis["improvement_actions"].get(bucket, []))

        if is_business and self.business.has_any_data():
            analysis = self.business.analyze()
            for bucket in actions:
                actions[bucket].extend(analysis["improvement_actions"].get(bucket, []))

        # Augment with risk mitigation actions
        if is_personal and (
            self.personal.data["income"] or self.personal.data["fixed_expenses"]
        ):
            p_assessment = self.risk.assess_personal(
                income=self.personal.data["income"],
                fixed_expenses=self.personal.data["fixed_expenses"],
                variable_expenses=self.personal.data["variable_expenses"],
                savings=self.personal.data["savings"],
                debts=self.personal.data["debts"],
            )
            for risk in p_assessment.get("risks", []):
                action = risk.get("action", "")
                level = risk.get("level", "low")
                if action:
                    if level in ("critical", "high"):
                        if action not in actions["immediate"]:
                            actions["immediate"].append(action)
                    elif level == "medium":
                        if action not in actions["short_term"]:
                            actions["short_term"].append(action)

        if is_business and (
            self.business.data["revenue"] or self.business.data["fixed_costs"]
        ):
            b_assessment = self.risk.assess_business(
                revenue=self.business.data["revenue"],
                fixed_costs=self.business.data["fixed_costs"],
                variable_costs=self.business.data["variable_costs"],
                clients=self.business.data["clients"],
            )
            for risk in b_assessment.get("risks", []):
                action = risk.get("action", "")
                level = risk.get("level", "low")
                if action:
                    if level in ("critical", "high"):
                        if action not in actions["immediate"]:
                            actions["immediate"].append(action)
                    elif level == "medium":
                        if action not in actions["short_term"]:
                            actions["short_term"].append(action)

        # Fallback actions when no data at all
        if not any(actions.values()):
            actions["immediate"] = [
                "Write down all your monthly income sources.",
                "List every regular expense (fixed first, then variable).",
                "Check your current savings or cash balance.",
            ]
            actions["short_term"] = [
                "Set a monthly savings target (start with even 5% of income).",
                "Identify your top 3 largest unnecessary expenses.",
            ]
            actions["strategic"] = [
                "Build an emergency fund covering 3–6 months of expenses.",
                "Explore one additional income source.",
            ]
        else:
            # Ensure Immediate bucket always has at least one helpful action
            if not actions["immediate"]:
                missing_personal = self.personal.get_missing_fields() if is_personal else {}
                missing_business = self.business.get_missing_fields() if is_business else {}
                if "savings" in missing_personal:
                    actions["immediate"].append(
                        "Check and record your current savings or emergency fund balance."
                    )
                elif missing_personal or missing_business:
                    actions["immediate"].append(
                        "Gather the missing financial figures listed in Section 2 — "
                        "more data means better advice."
                    )
                else:
                    actions["immediate"].append(
                        "Review your finances against the plan and track any deviations."
                    )

        def fmt_list(items: List[str]) -> str:
            return "\n".join(f"- {item}" for item in items) if items else "- None identified yet."

        sections["actions"] = (
            f"**Immediate (today):**\n{fmt_list(actions['immediate'])}\n\n"
            f"**Short-term (30 days):**\n{fmt_list(actions['short_term'])}\n\n"
            f"**Strategic (long-term):**\n{fmt_list(actions['strategic'])}"
        )

        # ----------------------------------------------------------------
        # Section 6 — Next Questions
        # ----------------------------------------------------------------
        next_questions = self._generate_next_questions(is_personal, is_business)
        sections["next_questions"] = "\n".join(
            f"{i}. {q}" for i, q in enumerate(next_questions, 1)
        )

        # ----------------------------------------------------------------
        # Optionally enhance with LLM
        # ----------------------------------------------------------------
        if self._client:
            return self._llm_enhance(user_message, sections)

        return self._format_response(sections)

    # ------------------------------------------------------------------
    # LLM enhancement
    # ------------------------------------------------------------------

    def _llm_enhance(self, user_message: str, sections: Dict[str, str]) -> str:
        """Use OpenAI to produce a polished, beginner-friendly version."""
        structured_draft = self._format_response(sections)

        system_prompt = (
            "You are a proactive financial co-pilot — part financial coach, part analyst, "
            "part decision assistant. Your tone is warm, clear, and beginner-friendly. "
            "You NEVER use jargon without explaining it. You are always helpful even with "
            "incomplete data, clearly labelling facts vs. estimates vs. assumptions.\n\n"
            "The user has sent a message and the analytical engine has produced a "
            "structured draft response. Your task is to:\n"
            "1. Keep the exact six-section structure (### 1. Financial Snapshot, "
            "### 2. Missing Information, ### 3. Key Risks, ### 4. Cash Flow Insight, "
            "### 5. Improvement Actions, ### 6. Next Questions).\n"
            "2. Make the language warmer, clearer, and more actionable.\n"
            "3. Keep all numbers and facts unchanged.\n"
            "4. Do NOT add information not present in the draft.\n"
            "5. Keep the response concise but complete."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            *self._conversation_history[-6:],  # last 3 turns for context
            {
                "role": "user",
                "content": (
                    f"Original user message: {user_message}\n\n"
                    f"Structured draft:\n{structured_draft}"
                ),
            },
        ]

        try:
            response = self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1500,
                temperature=0.4,
            )
            return response.choices[0].message.content
        except Exception:
            # Fall back to the rule-based response on any API error
            return structured_draft

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _format_response(sections: Dict[str, str]) -> str:
        return (
            "### 1. Financial Snapshot\n"
            f"{sections['snapshot']}\n\n"
            "### 2. Missing Information\n"
            f"{sections['missing']}\n\n"
            "### 3. Key Risks\n"
            f"{sections['risks']}\n\n"
            "### 4. Cash Flow Insight\n"
            f"{sections['cash_flow']}\n\n"
            "### 5. Improvement Actions\n"
            f"{sections['actions']}\n\n"
            "### 6. Next Questions\n"
            f"{sections['next_questions']}"
        )

    # ------------------------------------------------------------------
    # Proactive question generation
    # ------------------------------------------------------------------

    def _generate_next_questions(self, is_personal: bool, is_business: bool) -> List[str]:
        questions: List[str] = []

        if is_personal:
            missing = self.personal.get_missing_fields()
            field_questions = {
                "income": "What is your total monthly income (salary + any other sources)?",
                "fixed_expenses": "What are your fixed monthly expenses? (rent/mortgage, utilities, subscriptions…)",
                "variable_expenses": "How much do you typically spend on variable costs per month? (food, transport, entertainment…)",
                "savings": "How much do you currently have in savings or an emergency fund?",
                "debts": "Do you have any outstanding debts? (loans, credit cards, overdraft…)",
            }
            for field in missing:
                if field in field_questions:
                    questions.append(field_questions[field])
                if len(questions) >= 3:
                    break

        if is_business:
            missing = self.business.get_missing_fields()
            field_questions = {
                "revenue": "What is your average monthly revenue?",
                "fixed_costs": "What are your monthly fixed costs? (staff, rent, software…)",
                "variable_costs": "What are your monthly variable costs? (materials, commissions, shipping…)",
                "pricing": "How do you price your product/service?",
                "clients": "How many active clients or customers do you currently have?",
            }
            for field in missing:
                if field in field_questions:
                    questions.append(field_questions[field])
                if len(questions) >= 5:
                    break

        if not questions:
            questions = [
                "Would you like a deeper analysis of any specific area?",
                "Is there a financial goal you are working towards?",
                "Would you like me to run a forecast for a longer time horizon?",
            ]

        return questions[:5]  # max 5 questions at a time

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def reset_session(self) -> None:
        """Clear all stored data and conversation history."""
        self.personal = PersonalFinanceAgent()
        self.business = BusinessFinanceAgent()
        self._conversation_history = []

    @property
    def has_openai(self) -> bool:
        return self._client is not None
