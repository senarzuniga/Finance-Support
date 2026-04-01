"""Business Finance Agent — revenue, costs, margins and profitability."""

import re
from typing import Any, Dict, List, Optional


class BusinessFinanceAgent:
    """Agent responsible for business finance analysis."""

    FIELD_LABELS: Dict[str, str] = {
        "revenue": "Monthly revenue (total sales / billings)",
        "fixed_costs": "Monthly fixed costs (salaries, rent, SaaS tools…)",
        "variable_costs": "Monthly variable costs (materials, shipping, commissions…)",
        "pricing": "Average price per product/service (or pricing model description)",
        "clients": "Number of active clients / monthly customers",
    }

    def __init__(self) -> None:
        self.data: Dict[str, Optional[Any]] = {
            field: None for field in self.FIELD_LABELS
        }

    # ------------------------------------------------------------------
    # Data management
    # ------------------------------------------------------------------

    def update_data(self, updates: Dict[str, Any]) -> None:
        """Merge new values into the data model."""
        for key, value in updates.items():
            if key in self.data and value is not None:
                # clients and pricing may be strings
                if key in ("clients", "pricing"):
                    try:
                        self.data[key] = float(value)
                    except (TypeError, ValueError):
                        self.data[key] = str(value)
                else:
                    try:
                        self.data[key] = float(value)
                    except (TypeError, ValueError):
                        pass

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract business finance figures from free-form user text."""
        extracted: Dict[str, Any] = {}
        text_lower = text.lower()

        amt = r"[\€\$\£]?\s*(\d[\d,\.k]*)"

        def parse_amount(raw: str) -> Optional[float]:
            raw = raw.strip()
            multiplier = 1.0
            if raw.endswith("k"):
                multiplier = 1_000
                raw = raw[:-1]
            try:
                return float(raw.replace(",", "")) * multiplier
            except ValueError:
                return None

        patterns: List[tuple] = [
            (
                "revenue",
                r"(?:revenue|turnover|sales|billing|income|earn)\D{0,25}" + amt,
            ),
            (
                "fixed_costs",
                r"(?:fixed\s+(?:cost|expense)|overhead|staff\s+cost|payroll|salaries?|rent)\D{0,25}"
                + amt,
            ),
            (
                "variable_costs",
                r"(?:variable\s+(?:cost|expense)|cogs|cost\s+of\s+goods|commissions?|materials?)\D{0,25}"
                + amt,
            ),
            (
                "clients",
                r"(\d+)\s+(?:clients?|customers?|accounts?)",
            ),
        ]

        for field, pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                raw = match.group(1)
                value = parse_amount(raw)
                if value is not None:
                    extracted[field] = value

        return extracted

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def get_missing_fields(self) -> Dict[str, str]:
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
        """Produce a business finance analysis dict."""
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

        revenue: Optional[float] = d["revenue"]
        fixed: float = d["fixed_costs"] or 0.0
        variable: float = d["variable_costs"] or 0.0
        clients: Optional[Any] = d["clients"]

        total_costs = fixed + variable
        result["metrics"]["total_costs"] = total_costs if total_costs > 0 else None

        if revenue:
            profit = revenue - total_costs
            result["metrics"]["gross_profit"] = profit

            if total_costs > 0:
                margin = profit / revenue * 100
                result["metrics"]["profit_margin_pct"] = round(margin, 1)
                cost_ratio = total_costs / revenue * 100
                result["metrics"]["cost_ratio_pct"] = round(cost_ratio, 1)

                if margin < 0:
                    result["insights"].append(
                        "🚨 Business is operating at a loss — costs exceed revenue."
                    )
                    result["improvement_actions"]["immediate"].append(
                        "Conduct an urgent cost audit — identify the largest cost line and cut it."
                    )
                    result["improvement_actions"]["immediate"].append(
                        "Review pricing — you may be undercharging for your product/service."
                    )
                elif margin < 10:
                    result["insights"].append(
                        "⚠️ Thin profit margin (< 10%) — vulnerable to any revenue dip."
                    )
                    result["improvement_actions"]["short_term"].append(
                        "Identify at least one cost line to reduce by 10–15%."
                    )
                    result["improvement_actions"]["short_term"].append(
                        "Consider a modest price increase (5–10%) — test with new clients first."
                    )
                elif margin < 20:
                    result["insights"].append(
                        "📊 Acceptable margin (10–20%) — room to improve operational efficiency."
                    )
                    result["improvement_actions"]["short_term"].append(
                        "Optimise variable cost structure — renegotiate supplier terms."
                    )
                else:
                    result["insights"].append(
                        "✅ Healthy profit margin (≥ 20%) — focus on scaling."
                    )

            if fixed > 0 and total_costs > 0:
                fixed_ratio = fixed / total_costs * 100
                result["metrics"]["fixed_cost_ratio_pct"] = round(fixed_ratio, 1)
                if fixed_ratio > 70:
                    result["insights"].append(
                        "⚠️ High fixed cost structure (> 70%) — limited flexibility in a downturn."
                    )
                    result["improvement_actions"]["strategic"].append(
                        "Explore converting fixed costs to variable (e.g., contractors vs. full-time staff)."
                    )

        if clients is not None:
            try:
                n_clients = float(clients)
                if revenue and n_clients > 0:
                    revenue_per_client = revenue / n_clients
                    result["metrics"]["revenue_per_client"] = round(revenue_per_client, 2)
                if n_clients <= 3:
                    result["insights"].append(
                        "⚠️ Very few clients — high dependency risk if one leaves."
                    )
                    result["improvement_actions"]["short_term"].append(
                        "Actively pursue at least 2–3 new client leads this month."
                    )
            except (TypeError, ValueError):
                pass

        # Universal strategic actions
        result["improvement_actions"]["strategic"].append(
            "Build a recurring revenue stream (subscriptions, retainers) for predictability."
        )
        result["improvement_actions"]["strategic"].append(
            "Create a 12-month financial plan with quarterly reviews."
        )

        return result

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

    def snapshot_text(self) -> str:
        d = self.data
        parts: List[str] = []
        if d["revenue"]:
            parts.append(f"Monthly revenue: **{d['revenue']:,.0f}**")
        total = (d["fixed_costs"] or 0) + (d["variable_costs"] or 0)
        if total:
            parts.append(f"Total monthly costs: **{total:,.0f}**")
            if d["fixed_costs"]:
                parts.append(f"  • Fixed: {d['fixed_costs']:,.0f}")
            if d["variable_costs"]:
                parts.append(f"  • Variable: {d['variable_costs']:,.0f}")
        if d["revenue"] and total:
            profit = d["revenue"] - total
            margin = profit / d["revenue"] * 100
            parts.append(f"Gross profit: **{profit:+,.0f}** ({margin:.1f}% margin)")
        if d["clients"] is not None:
            parts.append(f"Active clients: **{d['clients']}**")
        return "\n".join(parts) if parts else "_No business finance data captured yet._"

    def missing_info_text(self) -> str:
        missing = self.get_missing_fields()
        if not missing:
            return "_All business finance data is complete._"
        lines = ["To properly analyse your business finances, I still need:"]
        for i, (field, label) in enumerate(missing.items(), 1):
            lines.append(f"{i}. **{label}**")
        return "\n".join(lines)
