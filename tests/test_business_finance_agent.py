import pytest
from agents.business_finance_agent import BusinessFinanceAgent


def test_update_data():
    agent = BusinessFinanceAgent()
    updates = {
        'revenue': '10000',
        'fixed_costs': '2000',
        'variable_costs': '1500',
        'clients': '5',
        'pricing': '200'
    }
    agent.update_data(updates)
    assert agent.data['revenue'] == 10000.0
    assert agent.data['fixed_costs'] == 2000.0
    assert agent.data['variable_costs'] == 1500.0
    assert agent.data['clients'] == 5.0
    assert agent.data['pricing'] == 200.0


def test_extract_from_text():
    agent = BusinessFinanceAgent()
    text = "Our revenue is $10k, fixed costs are $2k, and we have 5 clients."
    extracted = agent.extract_from_text(text)
    assert extracted['revenue'] == 10000.0
    assert extracted['fixed_costs'] == 2000.0
    assert extracted['clients'] == 5.0


def test_analyze():
    agent = BusinessFinanceAgent()
    agent.data = {
        'revenue': 10000.0,
        'fixed_costs': 2000.0,
        'variable_costs': 1500.0,
        'clients': 5.0,
        'pricing': 200.0
    }
    analysis = agent.analyze()
    assert analysis['metrics']['total_costs'] == 3500.0
    assert analysis['metrics']['gross_profit'] == 6500.0
    assert analysis['metrics']['profit_margin_pct'] == 65.0
    assert analysis['metrics']['cost_ratio_pct'] == 35.0
