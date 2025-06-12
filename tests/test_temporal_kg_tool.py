import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.opendeepsearch.temporal_kg_tool import TemporalKGTool

class TestTemporalKGTool:
    
    @pytest.fixture
    def mock_neo4j_driver(self):
        """Mock Neo4j driver for testing"""
        driver = Mock()
        session = Mock()
        driver.session.return_value.__enter__.return_value = session
        driver.session.return_value.__exit__.return_value = None
        return driver, session
    
    @pytest.fixture
    def tool(self, mock_neo4j_driver):
        """Create tool instance with mocked dependencies"""
        driver, session = mock_neo4j_driver
        with patch('src.opendeepsearch.temporal_kg_tool.GraphDatabase.driver', return_value=driver):
            tool = TemporalKGTool(
                neo4j_uri="bolt://localhost:7687",
                username="neo4j",
                password="maxx3169"
            )
        return tool, session
    
    def test_tool_initialization(self):
        """Test tool initialization"""
        with patch('src.opendeepsearch.temporal_kg_tool.GraphDatabase.driver') as mock_driver:
            tool = TemporalKGTool("bolt://localhost:7687", "neo4j", "password")
            assert tool.name == "temporal_kg_search"
            assert "temporal query" in tool.description.lower()
            assert "query" in tool.inputs
            mock_driver.assert_called_once()
    
    @patch('src.opendeepsearch.temporal_kg_tool.completion')
    def test_llm_parse_query_single_event(self, mock_completion, tool):
        """Test LLM parsing for single event queries"""
        tool_instance, session = tool
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "customer_ids": ["CUST001"],
            "event_types": ["Purchase"],
            "sequence_type": "first",
            "comparison": False,
            "intent": "SINGLE_EVENT",
            "order": "ASC"
        })
        mock_completion.return_value = mock_response
        
        result = tool_instance._llm_parse_query("When did CUST001 make their first purchase?")
        
        assert result["customer_ids"] == ["CUST001"]
        assert result["event_types"] == ["Purchase"]
        assert result["intent"] == "SINGLE_EVENT"
        assert result["sequence_type"] == "first"
        assert not result["comparison"]
    
    @patch('src.opendeepsearch.temporal_kg_tool.completion')
    def test_llm_parse_query_comparison(self, mock_completion, tool):
        """Test LLM parsing for comparison queries"""
        tool_instance, session = tool
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "customer_ids": ["CUST001", "CUST002"],
            "event_types": ["Signup"],
            "sequence_type": "first",
            "comparison": True,
            "intent": "COMPARISON",
            "order": "ASC"
        })
        mock_completion.return_value = mock_response
        
        result = tool_instance._llm_parse_query("Who signed up first, CUST001 or CUST002?")
        
        assert result["customer_ids"] == ["CUST001", "CUST002"]
        assert result["event_types"] == ["Signup"]
        assert result["intent"] == "COMPARISON"
        assert result["comparison"]
    
    def test_fallback_parse_basic(self, tool):
        """Test fallback parsing when LLM fails"""
        tool_instance, session = tool
        
        result = tool_instance._fallback_parse("Show me CUST001 purchase events")
        
        assert "CUST001" in result["customer_ids"]
        assert "Purchase" in result["event_types"]
        assert result["intent"] == "EVENT_SEQUENCE"
    
    def test_fallback_parse_first_last(self, tool):
        """Test fallback parsing for first/last queries"""
        tool_instance, session = tool
        
        # Test "first" query
        result = tool_instance._fallback_parse("CUST001 first login")
        assert result["sequence_type"] == "first"
        assert result["intent"] == "SINGLE_EVENT"
        assert result["order"] == "ASC"
        
        # Test "last" query
        result = tool_instance._fallback_parse("CUST002 last purchase")
        assert result["sequence_type"] == "last"
        assert result["intent"] == "SINGLE_EVENT"
        assert result["order"] == "DESC"
    
    def test_validate_constraints(self, tool):
        """Test constraint validation"""
        tool_instance, session = tool
        
        # Test invalid constraints
        constraints = {
            "customer_ids": "CUST001",  # Should be list
            "event_types": ["Purchase", "InvalidEvent"],  # Contains invalid event
            "sequence_type": "first"
        }
        
        result = tool_instance._validate_constraints(constraints)
        
        assert result["customer_ids"] == []  # Fixed to empty list
        assert result["event_types"] == ["Purchase"]  # Invalid event removed
        assert "sequence_type" in result
        assert "intent" in result
    
    def test_generate_cypher_single_event(self, tool):
        """Test Cypher query generation for single events"""
        tool_instance, session = tool
        
        constraints = {
            "customer_ids": ["CUST001"],
            "event_types": ["Purchase"],
            "sequence_type": "first",
            "intent": "SINGLE_EVENT",
            "order": "ASC"
        }
        
        query, params = tool_instance._generate_cypher_query(constraints)
        
        assert "MATCH (c:Customer {id: $customer_id})" in query
        assert "ORDER BY r.timestamp ASC" in query
        assert params["customer_id"] == "CUST001"
        assert params["event_type"] == "Purchase"
    
    def test_generate_cypher_comparison(self, tool):
        """Test Cypher query generation for comparisons"""
        tool_instance, session = tool
        
        constraints = {
            "customer_ids": ["CUST001", "CUST002"],
            "event_types": ["Signup"],
            "intent": "COMPARISON",
            "comparison": True
        }
        
        query, params = tool_instance._generate_cypher_query(constraints)
        
        assert "WHERE c.id IN $customer_ids" in query
        assert params["customer_ids"] == ["CUST001", "CUST002"]
        assert params["event_type"] == "Signup"
    
    def test_format_single_event_results(self, tool):
        """Test result formatting for single events"""
        tool_instance, session = tool
        
        # Mock database record
        records = [{
            'c.name': 'John Doe',
            'c.id': 'CUST001',
            'e': {'plan': 'premium'},
            'event_labels': ['Event', 'Purchase'],
            'r.timestamp': datetime(2023, 6, 15, 10, 30)
        }]
        
        constraints = {
            "event_types": ["Purchase"],
            "sequence_type": "first"
        }
        
        result = tool_instance._format_single_event_results(records, constraints)
        
        assert "John Doe (CUST001)" in result
        assert "first Purchase" in result
        assert "2023-06-15 10:30" in result
        assert "premium" in result
    
    def test_format_comparison_results(self, tool):
        """Test result formatting for comparisons"""
        tool_instance, session = tool
        
        records = [
            {
                'customer_name': 'John Doe',
                'customer_id': 'CUST001',
                'timestamp': datetime(2023, 1, 15, 9, 0)
            },
            {
                'customer_name': 'Jane Smith',
                'customer_id': 'CUST002',
                'timestamp': datetime(2023, 1, 20, 14, 30)
            }
        ]
        
        constraints = {"event_types": ["Signup"]}
        
        result = tool_instance._format_comparison_results(records, constraints)
        
        assert "Comparison of Signup events" in result
        assert "John Doe (CUST001)" in result
        assert "Jane Smith (CUST002)" in result
        assert "2023-01-15 09:00" in result
        assert "2023-01-20 14:30" in result
    
    def test_format_timeline_results(self, tool):
        """Test result formatting for timelines"""
        tool_instance, session = tool
        
        records = [
            {
                'c.name': 'John Doe',
                'c.id': 'CUST001',
                'e': {'plan': 'basic'},
                'event_labels': ['Event', 'Signup'],
                'r.timestamp': datetime(2023, 1, 15, 9, 0)
            },
            {
                'c.name': 'John Doe',
                'c.id': 'CUST001',
                'e': {'from_plan': 'basic', 'to_plan': 'premium'},
                'event_labels': ['Event', 'Upgrade'],
                'r.timestamp': datetime(2023, 2, 15, 10, 0)
            }
        ]
        
        constraints = {}
        
        result = tool_instance._format_timeline_results(records, constraints)
        
        assert "Timeline for John Doe (CUST001)" in result
        assert "2023-01-15 09:00: Signup" in result
        assert "2023-02-15 10:00: Upgrade" in result
        assert "basic" in result and "premium" in result
    
    @patch('src.opendeepsearch.temporal_kg_tool.completion')
    def test_forward_integration_single_event(self, mock_completion, tool):
        """Test full integration for single event query"""
        tool_instance, session = tool
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "customer_ids": ["CUST001"],
            "event_types": ["Purchase"],
            "sequence_type": "first",
            "comparison": False,
            "intent": "SINGLE_EVENT",
            "order": "ASC"
        })
        mock_completion.return_value = mock_response
        
        # Mock database response
        mock_result = Mock()
        mock_record = Mock()
        mock_record.data.return_value = {
            'c.name': 'John Doe',
            'c.id': 'CUST001',
            'e': {'plan': 'premium'},
            'event_labels': ['Event', 'Purchase'],
            'r.timestamp': datetime(2023, 6, 15, 10, 30)
        }
        mock_result.__iter__.return_value = [mock_record]
        session.run.return_value = mock_result
        
        result = tool_instance.forward("When did CUST001 make their first purchase?")
        
        assert "John Doe (CUST001)" in result
        assert "first Purchase" in result
        assert "2023-06-15 10:30" in result
    
    @patch('src.opendeepsearch.temporal_kg_tool.completion')
    def test_forward_integration_comparison(self, mock_completion, tool):
        """Test full integration for comparison query"""
        tool_instance, session = tool
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "customer_ids": ["CUST001", "CUST002"],
            "event_types": ["Signup"],
            "sequence_type": "first",
            "comparison": True,
            "intent": "COMPARISON",
            "order": "ASC"
        })
        mock_completion.return_value = mock_response
        
        # Mock database response
        mock_result = Mock()
        mock_records = [
            Mock(),
            Mock()
        ]
        mock_records[0].data.return_value = {
            'customer_name': 'John Doe',
            'customer_id': 'CUST001',
            'timestamp': datetime(2023, 1, 15, 9, 0)
        }
        mock_records[1].data.return_value = {
            'customer_name': 'Jane Smith',
            'customer_id': 'CUST002',
            'timestamp': datetime(2023, 1, 20, 14, 30)
        }
        mock_result.__iter__.return_value = mock_records
        session.run.return_value = mock_result
        
        result = tool_instance.forward("Who signed up first, CUST001 or CUST002?")
        
        assert "Comparison of Signup events" in result
        assert "John Doe (CUST001)" in result
        assert "Jane Smith (CUST002)" in result
    
    def test_error_handling(self, tool):
        """Test error handling in forward method"""
        tool_instance, session = tool
        
        # Simulate database error
        session.run.side_effect = Exception("Database connection failed")
        
        result = tool_instance.forward("When did CUST001 sign up?")
        
        assert "Temporal search failed" in result
        assert "Database connection failed" in result
    
    def test_prompt_example_queries(self, tool):
        """Test that example queries from prompts can be parsed"""
        tool_instance, session = tool
        
        example_queries = [
            "When did CUST001 make their first purchase?",
            "Show me the complete timeline for CUST003",
            "Who signed up first, CUST001 or CUST002?",
            "What happened to CUST002 after their support ticket was resolved?",
            "Compare the upgrade dates of all customers",
            "Show me CUST003's events leading up to cancellation"
        ]
        
        for query in example_queries:
            # Test that fallback parsing doesn't crash
            constraints = tool_instance._fallback_parse(query)
            assert isinstance(constraints, dict)
            assert "customer_ids" in constraints
            assert "event_types" in constraints
            assert "intent" in constraints


# Integration test with actual prompt structure
class TestPromptIntegration:
    
    def test_temporal_reasoning_prompt_structure(self):
        """Test that the temporal reasoning prompt has correct structure"""
        from src.opendeepsearch.prompts import TEMPORAL_REASONING_PROMPT
        
        # Check key sections exist
        assert "temporal_kg_search" in TEMPORAL_REASONING_PROMPT
        assert "Direct Temporal Comparisons" in TEMPORAL_REASONING_PROMPT
        assert "Event Timeline Queries" in TEMPORAL_REASONING_PROMPT
        assert "CUST001" in TEMPORAL_REASONING_PROMPT
        assert "CUST002" in TEMPORAL_REASONING_PROMPT
        assert "CUST003" in TEMPORAL_REASONING_PROMPT
        
        # Check event types are listed
        event_types = ["Signup", "Upgrade", "Login", "Purchase", "SupportTicket", "TicketResolved", "Cancellation"]
        for event_type in event_types:
            assert event_type in TEMPORAL_REASONING_PROMPT
        
        # Check example queries exist
        assert "When did CUST001 make their first purchase?" in TEMPORAL_REASONING_PROMPT
        assert "Who signed up first, CUST001 or CUST002?" in TEMPORAL_REASONING_PROMPT
    
    def test_react_prompt_structure(self):
        """Test that the REACT prompt has correct structure"""
        from src.opendeepsearch.prompts import REACT_PROMPT
        
        # Check it's a PromptTemplates instance
        from smolagents import PromptTemplates
        assert isinstance(REACT_PROMPT, PromptTemplates)
        
        # Check system prompt exists
        assert hasattr(REACT_PROMPT, 'system_prompt')
        assert "tool calls" in REACT_PROMPT.system_prompt
        assert "final_answer" in REACT_PROMPT.system_prompt


if __name__ == "__main__":
    # Run specific test
    pytest.main([__file__, "-v"]) 