import unittest
from unittest.mock import patch, MagicMock
from agent import Agent

class TestAgent(unittest.TestCase):
    
    @patch('agent.external_api_call')
    def test_agent_behavior_with_mocked_api(self, mock_api_call):
        # Arrange
        mock_api_call.return_value = {'status': 'success', 'data': 'mocked_data'}
        agent = Agent()
        
        # Act
        result = agent.perform_action()
        
        # Assert
        self.assertEqual(result, 'expected_result_based_on_mocked_data')
        mock_api_call.assert_called_once()

    @patch('agent.database_interaction')
    def test_agent_behavior_with_mocked_db(self, mock_db_interaction):
        # Arrange
        mock_db_interaction.return_value = {'status': 'success', 'data': 'mocked_db_data'}
        agent = Agent()
        
        # Act
        result = agent.perform_db_action()
        
        # Assert
        self.assertEqual(result, 'expected_result_based_on_mocked_db_data')
        mock_db_interaction.assert_called_once()

if __name__ == '__main__':
    unittest.main()
