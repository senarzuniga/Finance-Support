"""Forecasting Agent — projects future cash flow in three scenarios."""

from typing import Any, Dict, List, Optional


class ForecastingAgent:
    """
    Produces best-case / expected / worst-case cash flow forecasts
    based on income and expense data supplied by the personal or
    business finance agents.
    """

    # Scenario adjustments for cash flow modelling:
    #   best     → income +10%, expenses -10%  (optimistic growth)
    #   expected → current figures unchanged
    #   worst    → income -20%, expenses +15% (recession / cost spike)
    SCENARIOS = {
        "best":     {"income_factor": 1.10, "expense_factor": 0.90},
        "expected": {"income_factor": 1.00, "expense_factor": 1.00},
        "worst":    {"income_factor": 0.80, "expense_factor": 1.15},
    }

    # ------------------------------------------------------------------
    # Core forecast logic
    # ------------------------------------------------------------------

    def forecast(
        self,
        monthly_income: Optional[float],
        monthly_expenses: Optional[float],
        current_savings: Optional[float] = None,
        months: int = 6,
    ) -> Dict[str, Any]:
        """
        Return a dict with projections for each scenario.

        Parameters
        ----------
        monthly_income    : current monthly net income
        monthly_expenses  : current monthly total expenses
        current_savings   : starting cash/savings balance
        months            : forecast horizon
        """
        result: Dict[str, Any] = {
            "horizon_months": months,
            "scenarios": {},
            "insights": [],
            "liquidity_warnings": [],
        }

        if monthly_income is None and monthly_expenses is None:
            result["insights"].append(
                "⚠️ Not enough data yet. Please provide at least monthly income or expenses."
            )
            return result

        income = monthly_income or 0.0
        expenses = monthly_expenses or 0.0
        savings = current_savings or 0.0

        for name, factors in self.SCENARIOS.items():
            adj_income = income * factors["income_factor"]
            adj_expenses = expenses * factors["expense_factor"]
            monthly_net = adj_income - adj_expenses

            balance_series: List[float] = []
            balance = savings
            for _ in range(months):
                balance += monthly_net
                balance_series.append(round(balance, 2))

            final_balance = balance_series[-1] if balance_series else savings
            months_until_zero: Optional[int] = None
            if monthly_net < 0:
                # Find first month where cumulative balance would go negative
                bal = savings
                for m in range(1, months + 1):
                    bal += monthly_net
                    if bal <= 0:
                        months_until_zero = m
                        break

            result["scenarios"][name] = {
                "monthly_net": round(monthly_net, 2),
                "adj_income": round(adj_income, 2),
                "adj_expenses": round(adj_expenses, 2),
                "final_balance": round(final_balance, 2),
                "balance_series": balance_series,
                "months_until_zero": months_until_zero,
            }

        # Generate insights
        expected = result["scenarios"]["expected"]
        worst = result["scenarios"]["worst"]

        if expected["monthly_net"] >= 0:
            result["insights"].append(
                f"✅ Expected scenario: positive monthly cash flow of **{expected['monthly_net']:+,.0f}**."
            )
        else:
            result["insights"].append(
                f"🚨 Expected scenario: negative monthly cash flow of **{expected['monthly_net']:+,.0f}**."
            )

        if worst["months_until_zero"] is not None:
            result["liquidity_warnings"].append(
                f"⚠️ In the worst-case scenario, you could run out of funds in "
                f"**{worst['months_until_zero']} month(s)**."
            )
        elif worst["final_balance"] < 0:
            result["liquidity_warnings"].append(
                "🚨 Worst-case scenario results in a negative balance within "
                f"{months} months — consider building reserves."
            )

        if expected["final_balance"] > 0 and worst["final_balance"] < 0:
            result["insights"].append(
                "📊 Outcomes diverge significantly between scenarios — reducing expenses "
                "now will greatly improve resilience."
            )

        return result

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

    def forecast_text(
        self,
        monthly_income: Optional[float],
        monthly_expenses: Optional[float],
        current_savings: Optional[float] = None,
        months: int = 6,
    ) -> str:
        """Return a human-readable forecast summary."""
        data = self.forecast(monthly_income, monthly_expenses, current_savings, months)

        if not data["scenarios"]:
            return "\n".join(data["insights"])

        lines: List[str] = [f"**{months}-Month Cash Flow Forecast**\n"]

        labels = {
            "best": "🟢 Best case     (+10% income / -10% expenses)",
            "expected": "🟡 Expected case  (current figures)",
            "worst": "🔴 Worst case    (-20% income / +15% expenses)",
        }

        for scenario, label in labels.items():
            s = data["scenarios"][scenario]
            lines.append(f"**{label}**")
            lines.append(f"  Monthly net: {s['monthly_net']:+,.0f}")
            lines.append(f"  Balance after {months} months: {s['final_balance']:,.0f}")
            if s["months_until_zero"] is not None:
                lines.append(
                    f"  ⚠️ Funds run out in ~{s['months_until_zero']} month(s)!"
                )
            lines.append("")

        if data["insights"]:
            lines.append("**Key Observations:**")
            lines.extend(f"- {i}" for i in data["insights"])
            lines.append("")

        if data["liquidity_warnings"]:
            lines.append("**Liquidity Warnings:**")
            lines.extend(f"- {w}" for w in data["liquidity_warnings"])

        return "\n".join(lines)
