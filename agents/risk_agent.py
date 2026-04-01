"""Risk Agent — detects financial risks and proposes mitigation actions."""

from typing import Any, Dict, List, Optional


class RiskAgent:
    """
    Analyses a financial snapshot (personal or business) and returns
    a structured risk assessment with level, explanation, and actions.
    """

    RISK_LEVELS = ("low", "medium", "high", "critical")

    # ------------------------------------------------------------------
    # Personal risk assessment
    # ------------------------------------------------------------------

    def assess_personal(
        self,
        income: Optional[float] = None,
        fixed_expenses: Optional[float] = None,
        variable_expenses: Optional[float] = None,
        savings: Optional[float] = None,
        debts: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Return a personal finance risk assessment."""
        risks: List[Dict[str, str]] = []

        total_expenses = (fixed_expenses or 0) + (variable_expenses or 0)

        # 1. Spending vs income
        if income and total_expenses:
            if total_expenses >= income:
                risks.append(
                    {
                        "name": "Negative or zero cash flow",
                        "level": "critical",
                        "detail": "Expenses meet or exceed income — you are accumulating debt.",
                        "action": "Cut non-essential spending immediately; look for extra income.",
                    }
                )
            elif total_expenses / income > 0.85:
                risks.append(
                    {
                        "name": "Very high expense ratio",
                        "level": "high",
                        "detail": f"Over 85% of income goes to expenses ({total_expenses/income*100:.0f}%).",
                        "action": "Conduct a full expense review and target a 20% reduction.",
                    }
                )
            elif total_expenses / income > 0.70:
                risks.append(
                    {
                        "name": "High expense ratio",
                        "level": "medium",
                        "detail": f"{total_expenses/income*100:.0f}% of income goes to expenses.",
                        "action": "Reduce variable spending and look for cheaper fixed-cost alternatives.",
                    }
                )

        # 2. Emergency fund
        if savings is not None and income:
            months = savings / income
            if months < 1:
                risks.append(
                    {
                        "name": "Critically low emergency fund",
                        "level": "critical",
                        "detail": "Less than 1 month of income in savings.",
                        "action": "Prioritise building an emergency fund before anything else.",
                    }
                )
            elif months < 3:
                risks.append(
                    {
                        "name": "Insufficient emergency fund",
                        "level": "high",
                        "detail": f"Only {months:.1f} month(s) of income saved.",
                        "action": "Target 3–6 months of expenses as an emergency buffer.",
                    }
                )

        # 3. Debt load
        if debts is not None and income:
            ratio = debts / income
            if ratio > 36:
                risks.append(
                    {
                        "name": "Very high debt load",
                        "level": "critical",
                        "detail": f"Debt is {ratio:.0f}× monthly income.",
                        "action": "Seek debt consolidation or professional financial counselling.",
                    }
                )
            elif ratio > 12:
                risks.append(
                    {
                        "name": "Elevated debt",
                        "level": "high",
                        "detail": f"Debt is {ratio:.0f}× monthly income.",
                        "action": "Apply the debt avalanche method — pay highest-rate debt first.",
                    }
                )

        # 4. Fixed expense concentration
        if fixed_expenses and total_expenses and income:
            fixed_ratio = fixed_expenses / income
            if fixed_ratio > 0.60:
                risks.append(
                    {
                        "name": "High fixed cost dependency",
                        "level": "medium",
                        "detail": f"Fixed expenses consume {fixed_ratio*100:.0f}% of income.",
                        "action": "Negotiate or downgrade fixed commitments (e.g., rent, subscriptions).",
                    }
                )

        # 5. Single income source — only flag when savings buffer is also low,
        # making income disruption immediately dangerous.
        if income and (fixed_expenses or variable_expenses):
            if savings is None or (savings is not None and income and savings / income < 3):
                risks.append(
                    {
                        "name": "Limited income resilience",
                        "level": "medium",
                        "detail": (
                            "With a savings buffer below 3 months, any unexpected income "
                            "disruption could quickly become a crisis."
                        ),
                        "action": "Build an emergency fund of 3–6 months of expenses and explore a secondary income source.",
                    }
                )

        return self._compile(risks)

    # ------------------------------------------------------------------
    # Business risk assessment
    # ------------------------------------------------------------------

    def assess_business(
        self,
        revenue: Optional[float] = None,
        fixed_costs: Optional[float] = None,
        variable_costs: Optional[float] = None,
        clients: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Return a business finance risk assessment."""
        risks: List[Dict[str, str]] = []

        total_costs = (fixed_costs or 0) + (variable_costs or 0)

        # 1. Profitability
        if revenue and total_costs:
            margin = (revenue - total_costs) / revenue * 100
            if margin < 0:
                risks.append(
                    {
                        "name": "Operating at a loss",
                        "level": "critical",
                        "detail": f"Costs exceed revenue by {abs(revenue - total_costs):,.0f}.",
                        "action": "Immediate cost reduction or price increase required.",
                    }
                )
            elif margin < 5:
                risks.append(
                    {
                        "name": "Near-zero margin",
                        "level": "high",
                        "detail": f"Profit margin is only {margin:.1f}%.",
                        "action": "Find one large cost to reduce and test a price increase.",
                    }
                )

        # 2. Fixed cost structure
        if fixed_costs and total_costs and revenue:
            fixed_ratio = fixed_costs / revenue * 100
            if fixed_ratio > 60:
                risks.append(
                    {
                        "name": "High fixed overhead",
                        "level": "high",
                        "detail": f"Fixed costs represent {fixed_ratio:.0f}% of revenue.",
                        "action": "Shift some fixed costs to variable (e.g., contractors).",
                    }
                )

        # 3. Client concentration
        if clients is not None:
            try:
                n = float(clients)
                if n <= 1:
                    risks.append(
                        {
                            "name": "Single client dependency",
                            "level": "critical",
                            "detail": "All revenue depends on one client.",
                            "action": "Acquire at least 2–3 new clients within 30 days.",
                        }
                    )
                elif n <= 3:
                    risks.append(
                        {
                            "name": "Client concentration risk",
                            "level": "high",
                            "detail": f"Only {n:.0f} clients — losing one has a major impact.",
                            "action": "Diversify client base — target a minimum of 5–7 clients.",
                        }
                    )
            except (TypeError, ValueError):
                pass

        # 4. Cash flow instability (no recurring revenue assumed without info)
        if revenue:
            risks.append(
                {
                    "name": "Cash flow unpredictability",
                    "level": "medium",
                    "detail": "Without recurring revenue data, monthly cash flow may be volatile.",
                    "action": "Introduce retainer or subscription contracts to stabilise income.",
                }
            )

        return self._compile(risks)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compile(self, risks: List[Dict[str, str]]) -> Dict[str, Any]:
        """Determine overall level and build the final assessment dict."""
        if not risks:
            return {
                "overall_level": "low",
                "risks": [],
                "summary": "✅ No major financial risks detected with the data provided.",
            }

        level_order = {l: i for i, l in enumerate(self.RISK_LEVELS)}
        overall = max(risks, key=lambda r: level_order.get(r["level"], 0))["level"]

        level_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }

        return {
            "overall_level": overall,
            "level_emoji": level_emoji.get(overall, "⚠️"),
            "risks": risks,
            "summary": (
                f"{level_emoji.get(overall, '⚠️')} Overall risk level: **{overall.upper()}**"
            ),
        }

    def risk_text(self, assessment: Dict[str, Any]) -> str:
        """Return a formatted string of the risk assessment."""
        lines: List[str] = [assessment.get("summary", ""), ""]
        for risk in assessment.get("risks", []):
            emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(
                risk["level"], "⚠️"
            )
            lines.append(f"{emoji} **{risk['name']}** ({risk['level'].upper()})")
            lines.append(f"   {risk['detail']}")
            lines.append(f"   → *{risk['action']}*")
            lines.append("")
        return "\n".join(lines).strip()
