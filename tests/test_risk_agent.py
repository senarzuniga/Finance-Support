import pytest
from agents.risk_agent import RiskAgent


def test_assess_personal():
    agent = RiskAgent()
    assessment = agent.assess_personal(income=5000, fixed_expenses=1500, variable_expenses=1000, savings=2000, debts=10000)
    assert any(risk['level'] == 'critical' for risk in assessment['risks'])


def test_assess_business():
    agent = RiskAgent()
    assessment = agent.assess_business(revenue=10000, fixed_costs=2000, variable_costs=1500, clients=5)
    assert any(risk['level'] == 'medium' for risk in assessment['risks'])
