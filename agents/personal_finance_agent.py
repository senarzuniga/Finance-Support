"""Personal Finance Agent — tracks income, expenses, savings and debts."""

import re
from typing import Any, Dict, List, Optional


class PersonalFinanceAgent:
    """Agent responsible for personal finance analysis and coaching."""

    FIELD_LABELS: Dict[str, str] = {
        "income": "Monthly income (salary, freelance, etc.)",
        "fixed_expenses": "Monthly fixed expenses (rent, utilities, subscriptions…)",
        "variable_expenses": "Monthly variable expenses (food, transport, entertainment…)",
        "savings": "Current total savings",
        "debts": "Total outstanding debts (loans, credit cards…)",
    }

    def __init__(self) -> None:
        self.data: Dict[str, Optional[float]] = {
            field: None for field in self.FIELD_LABELS
        }

    # ------------------------------------------------------------------
    # Data management
    # ------------------------------------------------------------------

    def update_data(self, updates: Dict[str, Any]) -> None:
        """Merge new values into the data model."""
        for key, value in updates.items():
            if key in self.data and value is not None:
                try:
                    self.data[key] = float(value)
                except (TypeError, ValueError):
                    pass

    def extract_from_text(self, text: str) -> Dict[str, float]:
        """Extract personal finance figures from free-form user text."""
        extracted: Dict[str, float] = {}
        text_lower = text.lower()

        # Generic amount pattern (handles 1,500 or 1500 or 1.500)
        amt = r"[\€\$\£]?\s*(\d[\d,\.]*)"

        patterns: List[tuple] = [
            (
                "income",
                r"(?:earn|make|income|salary|wage|paid|receive|get)\D{0,25}" + amt,
            ),
            (
                "fixed_expenses",
                r"(?:fixed\s+(?:cost|expense)|rent|mortgage|subscription)\D{0,25}" + amt,
            ),
            (
                "variable_expenses",
                r"(?:variable\s+(?:cost|expense)|spend|spending|food|groceries|transport)\D{0,25}"
                + amt,
            ),
            ("savings", r"(?:saving|saved|savings|emergency\s+fund)\D{0,25}" + amt),
            ("debts", r"(?:debt|loan|owe|credit\s+card|mortgage\s+balance)\D{0,25}" + amt),
        ]

        for field, pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                raw = match.group(1)
                # Normalise number format — support European and US conventions
                if raw.count(".") > 1:
                    # Multiple dots = thousands separators (e.g. 1.500.000 → 1500000)
                    raw = raw.replace(".", "").replace(",", "")
                elif raw.count(".") == 1:
                    parts = raw.split(".")
                    if len(parts[1]) == 3 and not parts[1].startswith("0"):
                        # Dot followed by exactly 3 digits = European thousands sep (1.500 → 1500)
                        raw = raw.replace(".", "").replace(",", "")
                    else:
                        # Decimal dot (1.50, 1.5, 1.500 where right side starts with 0)
                        raw = raw.replace(",", "")
                else:
                    # No dot — remove commas as thousands separators
                    raw = raw.replace(",", "")
                try:
                    extracted[field] = float(raw)
                except ValueError:
                    pass

        # Fallback: plain "X€/month" or "X$/month" anywhere
        if "income" not in extracted:
            fallback = re.search(
                r"(\d[\d,\.]*)\s*(?:€|\$|£)\s*(?:/\s*month|per\s+month)?.*?(?:earn|income|salary)",
                text_lower,
            )
            if fallback:
                try:
                    extracted["income"] = float(fallback.group(1).replace(",", ""))
                except ValueError:
                    pass

        return extracted

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def get_missing_fields(self) -> Dict[str, str]:
        """Return {field: label} for every unfilled data point."""
        return {
            field: label
            for field, label in self.FIELD_LABELS.items()
            if self.data[field] is None
        }

    def has_any_data(self) -> bool:
        return any(v is not None for v in self.data.values())

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze(self) -> Dict[str, Any]:
        """Produce an analysis dict from whatever data is available."""
        d = self.data
        result: Dict[str, Any] = {
            "metrics": {},
            "insights": [],
            "improvement_actions": {
                "immediate": [],
                "short_term": [],
                "strategic": [],
            },
        }

        income: Optional[float] = d["income"]
        fixed: float = d["fixed_expenses"] or 0.0
        variable: float = d["variable_expenses"] or 0.0
        savings: Optional[float] = d["savings"]
        debts: Optional[float] = d["debts"]

        total_expenses = fixed + variable
        result["metrics"]["total_expenses"] = total_expenses if total_expenses > 0 else None

        if income:
            surplus = income - total_expenses
            result["metrics"]["monthly_surplus"] = surplus
            if total_expenses > 0:
                expense_ratio = total_expenses / income * 100
                savings_rate = surplus / income * 100
                result["metrics"]["expense_ratio_pct"] = round(expense_ratio, 1)
                result["metrics"]["savings_rate_pct"] = round(savings_rate, 1)

                if savings_rate < 0:
                    result["insights"].append(
                        "🚨 You are spending MORE than you earn — this is unsustainable."
                    )
                    result["improvement_actions"]["immediate"].append(
                        "Identify and cut the largest non-essential expense immediately."
                    )
                    result["improvement_actions"]["immediate"].append(
                        "Contact any lenders about payment flexibility."
                    )
                elif savings_rate < 10:
                    result["insights"].append(
                        "⚠️ Savings rate is below 10% — little cushion for emergencies."
                    )
                    result["improvement_actions"]["immediate"].append(
                        "Find one expense to eliminate or reduce this week."
                    )
                    result["improvement_actions"]["short_term"].append(
                        "Set up an automatic transfer of at least 5% of income to savings."
                    )
                elif savings_rate < 20:
                    result["insights"].append(
                        "📊 Savings rate is between 10–20% — decent, but there is room to grow."
                    )
                    result["improvement_actions"]["short_term"].append(
                        "Aim to raise your savings rate to 20% over the next 3 months."
                    )
                else:
                    result["insights"].append(
                        "✅ Strong savings rate (≥ 20%) — you are building wealth effectively."
                    )

        if savings is not None and income:
            months = savings / income
            result["metrics"]["emergency_fund_months"] = round(months, 1)
            if months < 1:
                result["insights"].append(
                    "🚨 Emergency fund covers less than 1 month — critical gap."
                )
                result["improvement_actions"]["immediate"].append(
                    "Start building an emergency fund — even small deposits matter now."
                )
            elif months < 3:
                result["insights"].append(
                    "⚠️ Emergency fund covers fewer than 3 months — aim for 3–6 months."
                )
                result["improvement_actions"]["short_term"].append(
                    "Build emergency fund to cover at least 3 months of expenses."
                )
            else:
                result["insights"].append(
                    "✅ Emergency fund looks healthy (3+ months of income covered)."
                )

        if debts is not None and income:
            debt_to_income = debts / income
            result["metrics"]["debt_to_income_ratio"] = round(debt_to_income, 2)
            if debt_to_income > 36:
                result["insights"].append(
                    "🚨 Debt-to-income ratio exceeds 36 months — high financial stress risk."
                )
                result["improvement_actions"]["immediate"].append(
                    "List all debts by interest rate and focus on the highest-rate debt first (avalanche method)."
                )
            elif debt_to_income > 12:
                result["insights"].append(
                    "⚠️ Significant debt load — create a structured repayment plan."
                )
                result["improvement_actions"]["short_term"].append(
                    "Set a monthly debt-repayment target above the minimum payment."
                )

        # Strategic
        result["improvement_actions"]["strategic"].append(
            "Review and diversify income sources over the next 6–12 months."
        )
        result["improvement_actions"]["strategic"].append(
            "Once debts are controlled, direct surplus into an investment or pension account."
        )

        return result

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

    def snapshot_text(self) -> str:
        """One-paragraph summary of the current personal finance picture."""
        d = self.data
        parts: List[str] = []
        if d["income"]:
            parts.append(f"Monthly income: **{d['income']:,.0f}**")
        total = (d["fixed_expenses"] or 0) + (d["variable_expenses"] or 0)
        if total:
            parts.append(f"Total monthly expenses: **{total:,.0f}**")
            if d["fixed_expenses"]:
                parts.append(f"  • Fixed: {d['fixed_expenses']:,.0f}")
            if d["variable_expenses"]:
                parts.append(f"  • Variable: {d['variable_expenses']:,.0f}")
        if d["income"] and total:
            surplus = d["income"] - total
            parts.append(f"Monthly surplus/deficit: **{surplus:+,.0f}**")
        if d["savings"] is not None:
            parts.append(f"Current savings: **{d['savings']:,.0f}**")
        if d["debts"] is not None:
            parts.append(f"Total debts: **{d['debts']:,.0f}**")
        return "\n".join(parts) if parts else "_No personal finance data captured yet._"

    def missing_info_text(self) -> str:
        missing = self.get_missing_fields()
        if not missing:
            return "_All personal finance data is complete._"
        lines = ["To give you a complete picture, I still need:"]
        for i, (field, label) in enumerate(missing.items(), 1):
            lines.append(f"{i}. **{label}**")
        return "\n".join(lines)
