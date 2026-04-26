import pytest
from agents.personal_finance_agent import PersonalFinanceAgent


def test_update_data():
    agent = PersonalFinanceAgent()
    updates = {
        'income': '5000',
        'fixed_expenses': '1500',
        'variable_expenses': '1000',
        'savings': '20000',
        'debts': '5000'
    }
    agent.update_data(updates)
    assert agent.data['income'] == 5000.0
    assert agent.data['fixed_expenses'] == 1500.0
    assert agent.data['variable_expenses'] == 1000.0
    assert agent.data['savings'] == 20000.0
    assert agent.data['debts'] == 5000.0


def test_extract_from_text():
    agent = PersonalFinanceAgent()
    text = "I earn $5k, my fixed expenses are $1.5k, and I have $20k in savings."
    extracted = agent.extract_from_text(text)
    assert extracted['income'] == 5000.0
    assert extracted['fixed_expenses'] == 1500.0
    assert extracted['savings'] == 20000.0


def test_analyze():
    agent = PersonalFinanceAgent()
    agent.data = {
        'income': 5000.0,
        'fixed_expenses': 1500.0,
        'variable_expenses': 1000.0,
        'savings': 20000.0,
        'debts': 5000.0
    }
    analysis = agent.analyze()
    assert analysis['metrics']['total_expenses'] == 2500.0
    assert analysis['metrics']['monthly_surplus'] == 2500.0
    assert analysis['metrics']['expense_ratio_pct'] == 50.0
    assert analysis['metrics']['savings_rate_pct'] == 50.0
