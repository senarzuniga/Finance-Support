import pytest
from agents.forecasting_agent import ForecastingAgent


def test_forecast():
    agent = ForecastingAgent()
    forecast = agent.forecast(monthly_income=5000, monthly_expenses=3000, current_savings=10000, months=6)
    assert forecast['horizon_months'] == 6
    assert forecast['scenarios']['expected']['monthly_net'] == 2000.0
    assert forecast['scenarios']['expected']['final_balance'] == 22000.0
    assert forecast['scenarios']['worst']['months_until_zero'] is None


def test_forecast_text():
    agent = ForecastingAgent()
    text = agent.forecast_text(monthly_income=5000, monthly_expenses=3000, current_savings=10000, months=6)
    assert "6-Month Cash Flow Forecast" in text
    assert "Expected case" in text
    assert "Worst case" in text
