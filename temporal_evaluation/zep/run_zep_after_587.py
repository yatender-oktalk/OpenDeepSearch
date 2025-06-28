#!/usr/bin/env python3
"""
THREE-WAY RATE-LIMITED Academic Evaluation: Zep vs OpenDeepSearch vs GraphRAG
Implements rigorous academic methodology with API rate limiting for Gemini 2.0 Flash

Academic Methodologies:
- TREC IR Evaluation (Voorhees & Harman, 2005)  
- Knowledge Graph Evaluation (Bordes et al., 2013)
- TempEval Framework (Verhagen et al., 2007)
- CoNLL NER Evaluation (Tjong Kim Sang & De Meulder, 2003)

Rate Limiting Strategy:
- 10 calls/minute max for Gemini 2.0 Flash
- 6+ seconds between API calls
- Progress indicators during delays
"""

import os
import sys
import json
import time
import re
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
import scipy.stats as stats
import numpy as np

# Setup paths
def setup_paths():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    
    zep_tools_path = os.path.join(os.path.dirname(__file__), 'tools')
    sys.path.insert(0, zep_tools_path)

setup_paths()

@dataclass
class GroundTruth:
    """Ground truth data for academic evaluation."""
    query_id: str
    required_dates: Set[str]
    required_entities: Set[str]
    required_filing_types: Set[str]
    required_years: Set[str]
    temporal_patterns: List[str]
    difficulty_weight: float

@dataclass
class EvaluationMetrics:
    """Academic evaluation metrics with citations."""
    precision: float
    recall: float
    f1_score: float
    mrr: float
    hits_at_k: float
    temporal_accuracy: float
    temporal_reasoning: float
    entity_precision: float
    entity_recall: float
    weighted_score: float

@dataclass
class SystemResponse:
    """System response with extracted information."""
    system_name: str
    query: str
    response: str
    response_time: float
    extracted_dates: Set[str]
    extracted_entities: Set[str]
    extracted_filing_types: Set[str]
    extracted_years: Set[str]
    extracted_patterns: List[str]

class ThreeWayAcademicEvaluator:
    """
    Three-way academic evaluation framework with API rate limiting.
    
    Systems Evaluated:
    1. Zep Temporal Knowledge Graph (Graphiti engine)
    2. OpenDeepSearch (Dynamic web search baseline)  
    3. GraphRAG Neo4j (Your structured implementation)
    """
    
    def __init__(self):
        self.ground_truth_data = self.create_ground_truth_dataset()
        self.evaluation_results = []
        
        # Rate limiting configuration for Gemini 2.0 Flash
        self.api_calls_per_minute = 10
        self.min_delay_between_calls = 60.0 / self.api_calls_per_minute  # 6 seconds
        self.last_api_call_time = 0
        self.api_call_count = 0
        
        # Initialize all three systems
        self.initialize_evaluation_systems()
    
    def enforce_rate_limit(self, system_name: str, call_number: int, total_calls: int):
        """Enforce API rate limiting with progress indicators."""
        
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time
        
        if time_since_last_call < self.min_delay_between_calls:
            wait_time = self.min_delay_between_calls - time_since_last_call
            
            print(f"🚦 Rate Limiting: Waiting {wait_time:.1f}s for {system_name}")
            print(f"   📊 Progress: {call_number}/{total_calls} API calls")
            print(f"   ⚡ Model: Gemini 2.0 Flash ({self.api_calls_per_minute} calls/minute)")
            
            # Progress bar during wait
            for i in range(int(wait_time)):
                remaining = int(wait_time) - i
                progress = "█" * (10 - min(10, remaining)) + "░" * min(10, remaining)
                print(f"   ⏳ [{progress}] {remaining}s remaining", end="\r")
                time.sleep(1)
            
            time.sleep(wait_time % 1)
            print("   ✅ Rate limit satisfied                    ")
        
        self.last_api_call_time = time.time()
        self.api_call_count += 1

    def safe_api_call(self, system_name: str, call_func, *args, **kwargs):
        """
        Make an API call with rate limiting and error handling.
        
        Args:
            system_name: Name of the system
            call_func: Function to call
            *args, **kwargs: Arguments for the function
        """
        
        max_retries = 3
        base_delay = 60  # Base delay for exponential backoff
        
        for attempt in range(max_retries):
            try:
                # Enforce rate limiting
                self.enforce_rate_limit(system_name, self.api_call_count + 1, "unknown")
                
                # Make the API call
                result = call_func(*args, **kwargs)
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                
                if "rate limit" in error_str or "quota" in error_str or "429" in error_str:
                    # Rate limit error - wait longer
                    wait_time = base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"🚨 Rate limit hit! Waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    
                    for i in range(wait_time):
                        remaining = wait_time - i
                        print(f"   ⏳ Rate limit cooldown: {remaining}s remaining", end="\r")
                        time.sleep(1)
                    print("   ✅ Cooldown complete                        ")
                    
                elif attempt == max_retries - 1:
                    # Final attempt failed
                    print(f"❌ Final attempt failed for {system_name}: {e}")
                    raise e
                else:
                    # Other error - shorter wait
                    wait_time = 2
                    print(f"⚠️ Error in {system_name} (attempt {attempt + 1}): {e}")
                    print(f"   ⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
    
    def initialize_evaluation_systems(self):
        """Initialize all three evaluation systems."""
        
        print("🔧 Initializing three-way evaluation systems...")
        
        # 1. Initialize OpenDeepSearch (Baseline)
        try:
            from smolagents import CodeAgent, LiteLLMModel
            from opendeepsearch import OpenDeepSearchTool
            
            baseline_model = LiteLLMModel(
                model_id="gemini/gemini-2.0-flash",  # Enhanced model
                max_tokens=2048,
                temperature=0.1
            )
            
            baseline_tool = OpenDeepSearchTool(
                model_name="gemini/gemini-2.0-flash",
                reranker="jina",
                search_provider="serper"
            )
            
            self.baseline_agent = CodeAgent(tools=[baseline_tool], model=baseline_model)
            print("✅ OpenDeepSearch initialized (Gemini 2.0 Flash + Serper)")
            
        except Exception as e:
            print(f"❌ OpenDeepSearch initialization failed: {e}")
            self.baseline_agent = None
        
        # 2. Initialize GraphRAG (Your Neo4j system)
        try:
            from opendeepsearch.simplified_temporal_kg_tool import SimplifiedTemporalKGTool
            
            graphrag_tool = SimplifiedTemporalKGTool(
                neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
                username=os.getenv('NEO4J_USERNAME', 'neo4j'),
                password=os.getenv('NEO4J_PASSWORD', 'maxx3169'),
                model_name="gemini/gemini-2.0-flash"
            )
            
            # Enhanced GraphRAG agent with SEC-specific prompting
            graphrag_model = LiteLLMModel(
                model_id="gemini/gemini-2.0-flash",
                max_tokens=2048,
                temperature=0.1,
                system_prompt="""You are a SEC filing specialist with access to comprehensive temporal data.

CRITICAL: For SEC filing queries, ALWAYS use 'sec_filing_temporal_search' tool FIRST.
This tool contains 25,606+ SEC filings with precise dates and structured data.

Only use web_search if the temporal search returns insufficient results.
Always prioritize the structured temporal knowledge graph for SEC-related queries."""
            )
            
            self.graphrag_agent = CodeAgent(
                tools=[baseline_tool, graphrag_tool], 
                model=graphrag_model
            )
            
            # Test GraphRAG connectivity
            test_response = graphrag_tool.forward("Test connection")
            if "SEC Filing Results:" in test_response or "filing" in test_response.lower():
                print("✅ GraphRAG Neo4j initialized (25,606 filings + Gemini 2.0 Flash)")
                self.graphrag_available = True
            else:
                print("⚠️ GraphRAG test failed - may have connectivity issues")
                self.graphrag_available = False
            
        except Exception as e:
            print(f"❌ GraphRAG initialization failed: {e}")
            self.graphrag_agent = None
            self.graphrag_available = False
        
        # 3. Initialize Zep TKG (if available)
        try:
            from zep_temporal_kg_tool import ZepTemporalKGTool
            self.zep_tool = ZepTemporalKGTool()
            print("✅ Zep TKG initialized (Graphiti engine)")
            self.zep_available = True
        except Exception as e:
            print(f"⚠️ Zep TKG not available: {e}")
            self.zep_tool = None
            self.zep_available = False
        
        # Summary
        available_systems = sum([
            self.baseline_agent is not None,
            self.graphrag_available,
            self.zep_available
        ])
        
        print(f"\n📊 Systems Status: {available_systems}/3 systems available")
        print(f"🚦 Rate limiting: {self.api_calls_per_minute} calls/minute (Gemini 2.0 Flash)")
    
    def create_ground_truth_dataset(self) -> Dict[str, GroundTruth]:
        """Create ground truth dataset based on verified SEC filing data."""
        
        return {
            "apple_2024_10q": GroundTruth(
                query_id="apple_2024_10q",
                required_dates={"2024-02-02", "2024-05-03", "2024-08-02"},  # Verified dates
                required_entities={"Apple Inc.", "AAPL"},
                required_filing_types={"10-Q"},
                required_years={"2024"},
                temporal_patterns=["Friday", "quarterly"],
                difficulty_weight=1.0
            ),
            
            "microsoft_2024_10k": GroundTruth(
                query_id="microsoft_2024_10k", 
                required_dates={"2024-07-30"},  # Verified Microsoft 10-K date
                required_entities={"Microsoft Corporation", "MSFT"},
                required_filing_types={"10-K"},
                required_years={"2024"},
                temporal_patterns=["annual"],
                difficulty_weight=1.0
            ),
            
            "apple_vs_microsoft": GroundTruth(
                query_id="apple_vs_microsoft",
                required_dates=set(),  # Comparative query
                required_entities={"Apple Inc.", "Microsoft Corporation"},
                required_filing_types={"10-Q", "10-K", "8-K"},
                required_years={"2024"},
                temporal_patterns=["comparison", "frequency"],
                difficulty_weight=1.5
            ),
            
            "meta_recent_10k": GroundTruth(
                query_id="meta_recent_10k",
                required_dates=set(),  # Recent query - dates may vary
                required_entities={"Meta Platforms Inc.", "META"},
                required_filing_types={"10-K"},
                required_years={"2024", "2023"},
                temporal_patterns=["recent", "annual"],
                difficulty_weight=1.0
            ),
            
            "tesla_q1_2024": GroundTruth(
                query_id="tesla_q1_2024",
                required_dates=set(),  # Q1 date range
                required_entities={"Tesla Inc.", "TSLA"},
                required_filing_types={"8-K", "10-Q"},
                required_years={"2024"},
                temporal_patterns=["quarterly", "Q1"],
                difficulty_weight=1.0
            )
        }
    
    def get_opendeepsearch_response(self, query: str, call_number: int, total_calls: int) -> SystemResponse:
        """Get OpenDeepSearch response with rate limiting."""
        
        if not self.baseline_agent:
            return self.create_error_response("OpenDeepSearch", query, "System not initialized")
        
        def make_api_call():
            enhanced_query = f"SEC filing information: {query}"
            start_time = time.time()
            response = self.baseline_agent.run(enhanced_query)
            response_time = time.time() - start_time
            
            return SystemResponse(
                system_name="OpenDeepSearch",
                query=query,
                response=str(response),
                response_time=response_time,
                extracted_dates=set(),
                extracted_entities=set(),
                extracted_filing_types=set(),
                extracted_years=set(),
                extracted_patterns=[]
            )
        
        try:
            # Enforce rate limiting before API call
            self.enforce_rate_limit("OpenDeepSearch", call_number, total_calls)
            return make_api_call()
            
        except Exception as e:
            return self.create_error_response("OpenDeepSearch", query, str(e))
    
    def get_graphrag_response(self, query: str, call_number: int, total_calls: int) -> SystemResponse:
        """Get GraphRAG response with rate limiting."""
        
        if not self.graphrag_available or not self.graphrag_agent:
            return self.create_error_response("GraphRAG", query, "System not available")
        
        def make_api_call():
            start_time = time.time()
            response = self.graphrag_agent.run(query)
            response_time = time.time() - start_time
            
            # Check if TKG tool was used
            tkg_used = "SEC Filing Results:" in str(response)
            
            return SystemResponse(
                system_name="GraphRAG",
                query=query,
                response=str(response),
                response_time=response_time,
                extracted_dates=set(),
                extracted_entities=set(),
                extracted_filing_types=set(),
                extracted_years=set(),
                extracted_patterns=[]
            )
        
        try:
            # Enforce rate limiting before API call
            self.enforce_rate_limit("GraphRAG", call_number, total_calls)
            return make_api_call()
            
        except Exception as e:
            return self.create_error_response("GraphRAG", query, str(e))
    
    def get_zep_response(self, query: str) -> SystemResponse:
        """Get Zep response (no rate limiting - local system)."""
        
        if not self.zep_available or not self.zep_tool:
            return self.create_error_response("Zep", query, "System not available")
        
        try:
            start_time = time.time()
            response = self.zep_tool.forward(query)
            response_time = time.time() - start_time
            
            return SystemResponse(
                system_name="Zep",
                query=query,
                response=str(response),
                response_time=response_time,
                extracted_dates=set(),
                extracted_entities=set(),
                extracted_filing_types=set(),
                extracted_years=set(),
                extracted_patterns=[]
            )
            
        except Exception as e:
            return self.create_error_response("Zep", query, str(e))
    
    def create_error_response(self, system_name: str, query: str, error_msg: str) -> SystemResponse:
        """Create standardized error response."""
        return SystemResponse(
            system_name=system_name,
            query=query,
            response=f"Error: {error_msg}",
            response_time=0.0,
            extracted_dates=set(),
            extracted_entities=set(),
            extracted_filing_types=set(),
            extracted_years=set(),
            extracted_patterns=[]
        )
    
    def extract_information_from_response(self, response: str) -> Tuple[Set[str], Set[str], Set[str], Set[str], List[str]]:
        """Extract structured information from system response."""
        
        # Extract dates with improved handling
        dates = self.extract_dates_improved(response)
        
        # Extract years from dates and context
        years = self.extract_years_improved(response, dates)
        
        # Extract filing types
        filing_types = set()
        response_upper = response.upper()
        for filing_type in ['10-Q', '10-K', '8-K', 'DEF 14A', 'DEFA14A', '4', '3', '5']:
            if filing_type in response_upper:
                filing_types.add(filing_type)
        
        # Extract entities (company names)
        entities = set()
        response_lower = response.lower()
        entity_mappings = {
            'apple': 'Apple Inc.',
            'microsoft': 'Microsoft Corporation',
            'tesla': 'Tesla Inc.',
            'meta': 'Meta Platforms Inc.',
            'alphabet': 'Alphabet Inc.',
            'google': 'Alphabet Inc.',
            'aapl': 'Apple Inc.',
            'msft': 'Microsoft Corporation',
            'tsla': 'Tesla Inc.'
        }
        
        for keyword, full_name in entity_mappings.items():
            if keyword in response_lower:
                entities.add(full_name)
        
        # Extract temporal patterns
        patterns = []
        pattern_keywords = {
            'friday': 'Friday',
            'quarterly': 'quarterly',
            'annual': 'annual',
            'q1': 'Q1',
            'comparison': 'comparison',
            'pattern': 'pattern',
            'recent': 'recent',
            'frequency': 'frequency'
        }
        
        for keyword, pattern in pattern_keywords.items():
            if keyword in response_lower:
                patterns.append(pattern)
        
        return dates, entities, filing_types, years, patterns
    
    def calculate_ir_metrics(self, extracted: Set, ground_truth: Set) -> Tuple[float, float, float]:
        """Calculate Information Retrieval metrics (Voorhees & Harman, 2005)."""
        
        if len(extracted) == 0 and len(ground_truth) == 0:
            return 1.0, 1.0, 1.0
        
        if len(extracted) == 0:
            return 0.0, 0.0, 0.0
        
        if len(ground_truth) == 0:
            return 0.0, 1.0, 0.0
        
        tp = len(extracted.intersection(ground_truth))
        fp = len(extracted - ground_truth)
        fn = len(ground_truth - extracted)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return precision, recall, f1_score
    
    def calculate_temporal_accuracy(self, extracted_dates: Set[str], ground_truth_dates: Set[str]) -> float:
        """Calculate temporal accuracy (Verhagen et al., 2007)."""
        
        if not ground_truth_dates:
            return 1.0 if not extracted_dates else 0.5
        
        scores = []
        
        for true_date in ground_truth_dates:
            best_score = 0.0
            
            for extracted_date in extracted_dates:
                if extracted_date == true_date:
                    best_score = 1.0  # Exact match
                    break
                elif extracted_date[:7] == true_date[:7]:  # Same year-month
                    best_score = max(best_score, 0.7)
                elif extracted_date[:4] == true_date[:4]:  # Same year
                    best_score = max(best_score, 0.4)
            
            scores.append(best_score)
        
        return statistics.mean(scores)
    
    def evaluate_system_response(self, response: SystemResponse, ground_truth: GroundTruth) -> EvaluationMetrics:
        """Comprehensive evaluation using academic methodologies."""
        
        # Handle error responses
        if "Error:" in response.response or len(response.response.strip()) == 0:
            return EvaluationMetrics(
                precision=0.0, recall=0.0, f1_score=0.0, mrr=0.0, hits_at_k=0.0,
                temporal_accuracy=0.0, temporal_reasoning=0.0, entity_precision=0.0,
                entity_recall=0.0, weighted_score=0.0
            )
        
        # Extract information from response
        dates, entities, filing_types, years, patterns = self.extract_information_from_response(response.response)
        
        # Update response with extracted info
        response.extracted_dates = dates
        response.extracted_entities = entities
        response.extracted_filing_types = filing_types
        response.extracted_years = years
        response.extracted_patterns = patterns
        
        # Calculate academic metrics
        date_precision, date_recall, date_f1 = self.calculate_ir_metrics(dates, ground_truth.required_dates)
        entity_precision, entity_recall, entity_f1 = self.calculate_ir_metrics(entities, ground_truth.required_entities)
        
        # Knowledge Graph metrics
        all_extracted = list(dates) + list(entities)
        all_required = ground_truth.required_dates.union(ground_truth.required_entities)
        
        # MRR calculation
        reciprocal_ranks = []
        for true_item in all_required:
            rank = None
            for i, extracted_item in enumerate(all_extracted):
                if true_item in str(extracted_item):
                    rank = i + 1
                    break
            reciprocal_ranks.append(1.0 / rank if rank else 0.0)
        
        mrr_score = statistics.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
        hits_at_3 = 1.0 if len(dates.intersection(ground_truth.required_dates)) > 0 else 0.0
        
        # Temporal processing metrics
        temporal_accuracy = self.calculate_temporal_accuracy(dates, ground_truth.required_dates)
        
        pattern_scores = []
        for true_pattern in ground_truth.temporal_patterns:
            found = any(true_pattern.lower() in extracted_pattern.lower() 
                       for extracted_pattern in patterns)
            pattern_scores.append(1.0 if found else 0.0)
        temporal_reasoning = statistics.mean(pattern_scores) if pattern_scores else 0.0
        
        # Calculate weighted score (academic standard)
        weighted_score = (
            date_precision * 0.25 +
            date_recall * 0.25 +
            date_f1 * 0.20 +
            mrr_score * 0.15 +
            hits_at_3 * 0.10 +
            temporal_accuracy * 0.20 +
            temporal_reasoning * 0.15 +
            entity_precision * 0.10 +
            entity_recall * 0.10
        ) * 100
        
        return EvaluationMetrics(
            precision=date_precision,
            recall=date_recall,
            f1_score=date_f1,
            mrr=mrr_score,
            hits_at_k=hits_at_3,
            temporal_accuracy=temporal_accuracy,
            temporal_reasoning=temporal_reasoning,
            entity_precision=entity_precision,
            entity_recall=entity_recall,
            weighted_score=weighted_score
        )
    
    def run_three_way_evaluation(self) -> Dict:
        """Run complete three-way academic evaluation."""
        
        print("🎓 THREE-WAY RATE-LIMITED ACADEMIC EVALUATION")
        print("=" * 80)
        print("📚 Academic Methodologies:")
        print("   • TREC IR Evaluation (Voorhees & Harman, 2005)")
        print("   • Knowledge Graph Evaluation (Bordes et al., 2013)")
        print("   • TempEval Framework (Verhagen et al., 2007)")
        print("   • CoNLL NER Evaluation (Tjong Kim Sang & De Meulder, 2003)")
        print("🚦 Rate Limiting:")
        print(f"   • Gemini 2.0 Flash: {self.api_calls_per_minute} calls/minute")
        print(f"   • Minimum delay: {self.min_delay_between_calls:.1f}s between calls")
        print("🔬 Systems Under Test:")
        print("   1. 🔍 OpenDeepSearch (Dynamic web search)")
        print("   2. 🏗️ GraphRAG Neo4j (Structured 25,606 filings)")
        print("   3. 🧠 Zep TKG (Graphiti bi-temporal engine)")
        print("=" * 80)
        
        evaluation_queries = {
            "apple_2024_10q": "What are Apple's exact 10-Q filing dates for 2024?",
            "microsoft_2024_10k": "When did Microsoft file its 2024 annual report (10-K)?",
            "apple_vs_microsoft": "Compare the number of SEC filings between Apple and Microsoft in 2024",
            "meta_recent_10k": "Show me Meta's recent 10-K filings",
            "tesla_q1_2024": "List Tesla's SEC filings from Q1 2024"
        }
        
        total_queries = len(evaluation_queries)
        # API calls: 2 systems need rate limiting (OpenDeepSearch + GraphRAG)
        total_api_calls = total_queries * 2
        estimated_time = (total_api_calls * self.min_delay_between_calls) / 60
        
        print(f"\n⏱️ Estimated evaluation time: {estimated_time:.1f} minutes")
        print(f"📊 Total API calls planned: {total_api_calls}")
        
        results = {
            'opendeepsearch_results': [],
            'graphrag_results': [],
            'zep_results': [],
            'comparative_analysis': {},
            'evaluation_metadata': {
                'start_time': datetime.now().isoformat(),
                'api_rate_limit': self.api_calls_per_minute,
                'min_delay': self.min_delay_between_calls,
                'model': 'gemini/gemini-2.0-flash'
            }
        }
        
        api_call_counter = 0
        
        for i, (query_id, query_text) in enumerate(evaluation_queries.items()):
            print(f"\n📋 Query {i+1}/{total_queries}: {query_text}")
            print("-" * 70)
            
            ground_truth = self.ground_truth_data[query_id]
            
            # 1. OpenDeepSearch (with rate limiting)
            print("🔍 OpenDeepSearch (Dynamic Web Search)...")
            api_call_counter += 1
            ods_response = self.get_opendeepsearch_response(query_text, api_call_counter, total_api_calls)
            ods_metrics = self.evaluate_system_response(ods_response, ground_truth)
            
            # 2. GraphRAG (with rate limiting)
            print("🏗️ GraphRAG Neo4j (Structured Knowledge)...")
            api_call_counter += 1
            graphrag_response = self.get_graphrag_response(query_text, api_call_counter, total_api_calls)
            graphrag_metrics = self.evaluate_system_response(graphrag_response, ground_truth)
            
            # Check if GraphRAG used TKG tool
            tkg_used = "SEC Filing Results:" in graphrag_response.response
            print(f"    🔧 TKG Tool Used: {'✅' if tkg_used else '❌'}")
            
            # 3. Zep TKG (no rate limiting - local system)
            print("🧠 Zep TKG (Bi-temporal Graphiti)...")
            zep_response = self.get_zep_response(query_text)
            zep_metrics = self.evaluate_system_response(zep_response, ground_truth)
            
            # Store results
            results['opendeepsearch_results'].append((query_id, ods_response, ods_metrics))
            results['graphrag_results'].append((query_id, graphrag_response, graphrag_metrics))
            results['zep_results'].append((query_id, zep_response, zep_metrics))
            
            # Display metrics comparison
            print(f"\n📊 Academic Metrics Comparison:")
            print(f"   OpenDeepSearch: {ods_metrics.weighted_score:.2f}/100")
            print(f"     • Precision: {ods_metrics.precision:.3f} | Recall: {ods_metrics.recall:.3f}")
            print(f"     • Temporal Accuracy: {ods_metrics.temporal_accuracy:.3f}")
            
            print(f"   GraphRAG Neo4j: {graphrag_metrics.weighted_score:.2f}/100")
            print(f"     • Precision: {graphrag_metrics.precision:.3f} | Recall: {graphrag_metrics.recall:.3f}")
            print(f"     • Temporal Accuracy: {graphrag_metrics.temporal_accuracy:.3f}")
            
            print(f"   Zep TKG: {zep_metrics.weighted_score:.2f}/100")
            print(f"     • Precision: {zep_metrics.precision:.3f} | Recall: {zep_metrics.recall:.3f}")
            print(f"     • Temporal Accuracy: {zep_metrics.temporal_accuracy:.3f}")
            
            # Determine winner
            scores = [
                ("OpenDeepSearch", ods_metrics.weighted_score),
                ("GraphRAG", graphrag_metrics.weighted_score),
                ("Zep", zep_metrics.weighted_score)
            ]
            winner = max(scores, key=lambda x: x[1])
            print(f"\n🏆 Query Winner: {winner[0]} ({winner[1]:.2f} points)")
            
            # Progress update
            completed = i + 1
            remaining = total_queries - completed
            print(f"\n📈 Progress: {completed}/{total_queries} queries completed")
            if remaining > 0:
                remaining_api_calls = remaining * 2
                remaining_time = remaining_api_calls * self.min_delay_between_calls / 60
                print(f"⏱️  Estimated time remaining: {remaining_time:.1f} minutes")
        
        # Three-way statistical analysis
        ods_scores = [metrics.weighted_score for _, _, metrics in results['opendeepsearch_results']]
        graphrag_scores = [metrics.weighted_score for _, _, metrics in results['graphrag_results']]
        zep_scores = [metrics.weighted_score for _, _, metrics in results['zep_results']]
        
        # ANOVA for three-way comparison
        f_stat, p_value_anova = stats.f_oneway(ods_scores, graphrag_scores, zep_scores)
        
        # Pairwise t-tests
        t_ods_graphrag, p_ods_graphrag = stats.ttest_rel(ods_scores, graphrag_scores)
        t_ods_zep, p_ods_zep = stats.ttest_rel(ods_scores, zep_scores)
        t_graphrag_zep, p_graphrag_zep = stats.ttest_rel(graphrag_scores, zep_scores)
        
        # Effect sizes (Cohen's d)
        pooled_std = statistics.stdev(ods_scores + graphrag_scores + zep_scores)
        cohens_d_ods_graphrag = (statistics.mean(ods_scores) - statistics.mean(graphrag_scores)) / pooled_std if pooled_std > 0 else 0.0
        cohens_d_ods_zep = (statistics.mean(ods_scores) - statistics.mean(zep_scores)) / pooled_std if pooled_std > 0 else 0.0
        cohens_d_graphrag_zep = (statistics.mean(graphrag_scores) - statistics.mean(zep_scores)) / pooled_std if pooled_std > 0 else 0.0
        
        results['comparative_analysis'] = {
            'opendeepsearch_mean': statistics.mean(ods_scores),
            'opendeepsearch_std': statistics.stdev(ods_scores) if len(ods_scores) > 1 else 0.0,
            'graphrag_mean': statistics.mean(graphrag_scores),
            'graphrag_std': statistics.stdev(graphrag_scores) if len(graphrag_scores) > 1 else 0.0,
            'zep_mean': statistics.mean(zep_scores),
            'zep_std': statistics.stdev(zep_scores) if len(zep_scores) > 1 else 0.0,
            'anova_f_statistic': f_stat,
            'anova_p_value': p_value_anova,
            'pairwise_comparisons': {
                'ods_vs_graphrag': {'t_stat': t_ods_graphrag, 'p_value': p_ods_graphrag, 'cohens_d': cohens_d_ods_graphrag},
                'ods_vs_zep': {'t_stat': t_ods_zep, 'p_value': p_ods_zep, 'cohens_d': cohens_d_ods_zep},
                'graphrag_vs_zep': {'t_stat': t_graphrag_zep, 'p_value': p_graphrag_zep, 'cohens_d': cohens_d_graphrag_zep}
            },
            'significant_differences': {
                'ods_vs_graphrag': p_ods_graphrag < 0.05,
                'ods_vs_zep': p_ods_zep < 0.05,
                'graphrag_vs_zep': p_graphrag_zep < 0.05
            }
        }
        
        results['evaluation_metadata']['end_time'] = datetime.now().isoformat()
        results['evaluation_metadata']['total_api_calls'] = self.api_call_count
        
        return results
    
    def extract_dates_improved(self, response: str) -> Set[str]:
        """Enhanced date extraction for multiple formats."""
        
        dates = set()
        
        # YYYY-MM-DD format
        dates.update(re.findall(r'\d{4}-\d{2}-\d{2}', response))
        
        # Month DD, YYYY format (OpenDeepSearch style)
        month_day_year = re.findall(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', response)
        
        for month, day, year in month_day_year:
            month_num = {
                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                'September': '09', 'October': '10', 'November': '11', 'December': '12'
            }[month]
            
            formatted_date = f"{year}-{month_num}-{day.zfill(2)}"
            dates.add(formatted_date)
        
        return dates
    
    def extract_years_improved(self, response: str, extracted_dates: Set[str]) -> Set[str]:
        """Enhanced year extraction with context awareness."""
        
        years = set()
        
        # Extract years from already found dates (most reliable)
        for date in extracted_dates:
            if len(date) >= 4:
                year = date[:4]
                if year.isdigit() and 2020 <= int(year) <= 2030:
                    years.add(year)
        
        # Extract years from SEC filing context
        date_context_years = re.findall(r'(?:filed|filing|report|dated?)\s+(?:on\s+|in\s+)?.*?(20[12]\d)', response, re.IGNORECASE)
        years.update(date_context_years)
        
        return years

def main():
    """Run the three-way rate-limited academic evaluation."""
    
    evaluator = ThreeWayAcademicEvaluator()
    
    # Check system availability
    available_systems = sum([
        evaluator.baseline_agent is not None,
        evaluator.graphrag_available,
        evaluator.zep_available
    ])
    
    if available_systems < 2:
        print("❌ Insufficient systems available for evaluation")
        return
    
    print(f"\n🚀 Starting three-way evaluation with {available_systems}/3 systems")
    print(f"⏰ Started at {datetime.now().strftime('%H:%M:%S')}")
    
    results = evaluator.run_three_way_evaluation()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'three_way_evaluation_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print final summary
    print(f"\n🎓 THREE-WAY ACADEMIC EVALUATION COMPLETED")
    print("=" * 70)
    
    comp_analysis = results['comparative_analysis']
    
    print(f"📊 FINAL RESULTS:")
    print(f"   🔍 OpenDeepSearch: {comp_analysis['opendeepsearch_mean']:.2f} ± {comp_analysis['opendeepsearch_std']:.2f}")
    print(f"   🏗️ GraphRAG Neo4j:  {comp_analysis['graphrag_mean']:.2f} ± {comp_analysis['graphrag_std']:.2f}")
    print(f"   🧠 Zep TKG:         {comp_analysis['zep_mean']:.2f} ± {comp_analysis['zep_std']:.2f}")
    
    print(f"\n📈 STATISTICAL SIGNIFICANCE:")
    print(f"   ANOVA p-value: {comp_analysis['anova_p_value']:.4f}")
    
    pairwise = comp_analysis['pairwise_comparisons']
    sig = comp_analysis['significant_differences']
    
    print(f"   OpenDeepSearch vs GraphRAG: p={pairwise['ods_vs_graphrag']['p_value']:.4f} {'✅' if sig['ods_vs_graphrag'] else '❌'}")
    print(f"   OpenDeepSearch vs Zep: p={pairwise['ods_vs_zep']['p_value']:.4f} {'✅' if sig['ods_vs_zep'] else '❌'}")
    print(f"   GraphRAG vs Zep: p={pairwise['graphrag_vs_zep']['p_value']:.4f} {'✅' if sig['graphrag_vs_zep'] else '❌'}")
    
    print(f"\n📁 Results saved: {filename}")
    print(f"🚦 Total API calls: {evaluator.api_call_count}")
    print(f"⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()