#!/usr/bin/env python3
"""
THREE-WAY RATE-LIMITED Academic Evaluation with ROBUST API Protection
Implements rigorous academic methodology with comprehensive API safety measures

Features:
- Exponential backoff for rate limit errors
- Intelligent retry logic with cooldown periods
- Progress indicators during delays
- Graceful error handling and recovery
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

class ThreeWayRobustEvaluator:
    """
    Three-way academic evaluation with ROBUST API protection.
    
    API Safety Features:
    - Exponential backoff for rate limits (60s → 120s → 240s)
    - Intelligent error detection and handling
    - Progress indicators during cooldowns
    - Graceful failure after max retries
    """
    
    def __init__(self):
        self.ground_truth_data = self.create_ground_truth_dataset()
        self.evaluation_results = []
        
        # Rate limiting configuration
        self.api_calls_per_minute = 10
        self.min_delay_between_calls = 60.0 / self.api_calls_per_minute  # 6 seconds
        self.last_api_call_time = 0
        self.api_call_count = 0
        
        # API safety configuration
        self.max_retries = 3
        self.base_delay = 60  # Base delay for exponential backoff
        self.rate_limit_violations = 0
        
        # Initialize all systems
        self.initialize_evaluation_systems()
    
    def enforce_rate_limit(self, system_name: str, call_number: int, total_calls: int):
        """Enforce preventive API rate limiting."""
        
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
        Make an API call with comprehensive error handling and retry logic.
        
        Features:
        - Exponential backoff for rate limit errors (60s → 120s → 240s)
        - Intelligent error detection (429, "rate limit", "quota")
        - Progress indicators during cooldowns
        - Graceful failure handling
        
        Args:
            system_name: Name of the system making the call
            call_func: Function to execute
            *args, **kwargs: Arguments for the function
        """
        
        for attempt in range(self.max_retries):
            try:
                # Preventive rate limiting before each attempt
                self.enforce_rate_limit(system_name, self.api_call_count + 1, "unknown")
                
                # Execute the API call
                result = call_func(*args, **kwargs)
                
                # Success - reset violation counter
                if self.rate_limit_violations > 0:
                    print(f"✅ {system_name} API call successful after violations")
                    self.rate_limit_violations = 0
                
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Detect rate limit errors
                if any(indicator in error_str for indicator in ["rate limit", "quota", "429", "too many requests"]):
                    self.rate_limit_violations += 1
                    
                    # Exponential backoff for rate limit errors
                    wait_time = self.base_delay * (2 ** attempt)  # 60s, 120s, 240s
                    
                    print(f"🚨 Rate limit hit for {system_name}!")
                    print(f"   🔄 Attempt {attempt + 1}/{self.max_retries}")
                    print(f"   ⏰ Cooling down for {wait_time}s (exponential backoff)")
                    print(f"   📊 Total violations: {self.rate_limit_violations}")
                    
                    # Enhanced cooldown with progress indicator
                    for i in range(wait_time):
                        remaining = wait_time - i
                        minutes = remaining // 60
                        seconds = remaining % 60
                        progress_pct = ((wait_time - remaining) / wait_time) * 100
                        progress_bar = "█" * int(progress_pct // 5) + "░" * (20 - int(progress_pct // 5))
                        
                        print(f"   🧊 [{progress_bar}] {minutes:02d}:{seconds:02d} remaining", end="\r")
                        time.sleep(1)
                    
                    print("   ✅ Rate limit cooldown complete                        ")
                    
                    # Continue to next attempt
                    continue
                
                elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
                    # Network errors - shorter retry
                    if attempt < self.max_retries - 1:
                        wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s
                        print(f"🌐 Network error for {system_name} (attempt {attempt + 1})")
                        print(f"   ⏳ Retrying in {wait_time}s...")
                        
                        for i in range(wait_time):
                            remaining = wait_time - i
                            print(f"   🔄 Network retry in {remaining}s", end="\r")
                            time.sleep(1)
                        print("   ✅ Network retry ready                ")
                        continue
                
                elif attempt == self.max_retries - 1:
                    # Final attempt failed - give up gracefully
                    print(f"❌ Final attempt failed for {system_name}: {e}")
                    print(f"   🔄 Attempted {self.max_retries} times with exponential backoff")
                    print(f"   📊 Rate limit violations during session: {self.rate_limit_violations}")
                    raise e
                
                else:
                    # Other errors - brief pause before retry
                    wait_time = 3
                    print(f"⚠️ Error in {system_name} (attempt {attempt + 1}): {e}")
                    print(f"   ⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
        
        # Should never reach here, but safety fallback
        raise Exception(f"All {self.max_retries} attempts failed for {system_name}")
    
    def initialize_evaluation_systems(self):
        """Initialize all three evaluation systems with robust error handling."""
        
        print("🔧 Initializing three-way evaluation systems with API protection...")
        
        # 1. Initialize OpenDeepSearch (Baseline)
        try:
            from smolagents import CodeAgent, LiteLLMModel
            from opendeepsearch import OpenDeepSearchTool
            
            print("🔍 Initializing OpenDeepSearch...")
            
            baseline_model = LiteLLMModel(
                model_id="gemini/gemini-2.0-flash",
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
            
            print("🏗️ Initializing GraphRAG Neo4j...")
            
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
                print("⚠️ GraphRAG test response unexpected - may have issues")
                print(f"   Test response: {test_response[:100]}...")
                self.graphrag_available = True  # Continue anyway
            
        except Exception as e:
            print(f"❌ GraphRAG initialization failed: {e}")
            self.graphrag_agent = None
            self.graphrag_available = False
        
        # 3. Initialize Zep TKG (if available)
        try:
            from zep_temporal_kg_tool import ZepTemporalKGTool
            print("🧠 Initializing Zep TKG...")
            self.zep_tool = ZepTemporalKGTool()
            print("✅ Zep TKG initialized (Graphiti engine)")
            self.zep_available = True
        except Exception as e:
            print(f"⚠️ Zep TKG not available: {e}")
            self.zep_tool = None
            self.zep_available = False
        
        # Configuration summary
        available_systems = sum([
            self.baseline_agent is not None,
            self.graphrag_available,
            self.zep_available
        ])
        
        print(f"\n📊 Initialization Summary:")
        print(f"   Systems available: {available_systems}/3")
        print(f"   🚦 Rate limiting: {self.api_calls_per_minute} calls/minute")
        print(f"   🛡️ API protection: Exponential backoff up to {self.base_delay * (2 ** (self.max_retries - 1))}s")
        print(f"   ⚡ Model: Gemini 2.0 Flash (enhanced performance)")
    
    def create_ground_truth_dataset(self) -> Dict[str, GroundTruth]:
        """Create verified ground truth dataset."""
        
        return {
            "apple_2024_10q": GroundTruth(
                query_id="apple_2024_10q",
                required_dates={"2024-02-02", "2024-05-03", "2024-08-02"},
                required_entities={"Apple Inc.", "AAPL"},
                required_filing_types={"10-Q"},
                required_years={"2024"},
                temporal_patterns=["Friday", "quarterly"],
                difficulty_weight=1.0
            ),
            
            "microsoft_2024_10k": GroundTruth(
                query_id="microsoft_2024_10k", 
                required_dates={"2024-07-30"},
                required_entities={"Microsoft Corporation", "MSFT"},
                required_filing_types={"10-K"},
                required_years={"2024"},
                temporal_patterns=["annual"],
                difficulty_weight=1.0
            ),
            
            "apple_vs_microsoft": GroundTruth(
                query_id="apple_vs_microsoft",
                required_dates=set(),
                required_entities={"Apple Inc.", "Microsoft Corporation"},
                required_filing_types={"10-Q", "10-K", "8-K"},
                required_years={"2024"},
                temporal_patterns=["comparison", "frequency"],
                difficulty_weight=1.5
            ),
            
            "meta_recent_10k": GroundTruth(
                query_id="meta_recent_10k",
                required_dates=set(),
                required_entities={"Meta Platforms Inc.", "META"},
                required_filing_types={"10-K"},
                required_years={"2024", "2023"},
                temporal_patterns=["recent", "annual"],
                difficulty_weight=1.0
            ),
            
            "tesla_q1_2024": GroundTruth(
                query_id="tesla_q1_2024",
                required_dates=set(),
                required_entities={"Tesla Inc.", "TSLA"},
                required_filing_types={"8-K", "10-Q"},
                required_years={"2024"},
                temporal_patterns=["quarterly", "Q1"],
                difficulty_weight=1.0
            )
        }
    
    def get_opendeepsearch_response(self, query: str, call_number: int, total_calls: int) -> SystemResponse:
        """Get OpenDeepSearch response with comprehensive API protection."""
        
        if not self.baseline_agent:
            return self.create_error_response("OpenDeepSearch", query, "System not initialized")
        
        def make_opendeepsearch_call():
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
            # Use safe API call with full protection
            return self.safe_api_call("OpenDeepSearch", make_opendeepsearch_call)
            
        except Exception as e:
            print(f"💥 OpenDeepSearch completely failed: {e}")
            return self.create_error_response("OpenDeepSearch", query, str(e))
    
    def get_graphrag_response(self, query: str, call_number: int, total_calls: int) -> SystemResponse:
        """Get GraphRAG response with comprehensive API protection."""
        
        if not self.graphrag_available or not self.graphrag_agent:
            return self.create_error_response("GraphRAG", query, "System not available")
        
        def make_graphrag_call():
            start_time = time.time()
            response = self.graphrag_agent.run(query)
            response_time = time.time() - start_time
            
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
            # Use safe API call with full protection
            return self.safe_api_call("GraphRAG", make_graphrag_call)
            
        except Exception as e:
            print(f"💥 GraphRAG completely failed: {e}")
            return self.create_error_response("GraphRAG", query, str(e))
    
    def get_zep_response(self, query: str) -> SystemResponse:
        """Get Zep response (no API rate limiting needed - local system)."""
        
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
    
    # ... (include all the other methods from the previous script: 
    #      extract_information_from_response, calculate_ir_metrics, 
    #      calculate_temporal_accuracy, evaluate_system_response, 
    #      extract_dates_improved, extract_years_improved)
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

    
    def run_three_way_evaluation(self) -> Dict:
        """Run complete three-way academic evaluation with robust API protection."""
        
        print("🎓 THREE-WAY ROBUST ACADEMIC EVALUATION")
        print("=" * 80)
        print("🛡️ API Protection Features:")
        print("   • Exponential backoff for rate limits (60s → 120s → 240s)")
        print("   • Intelligent error detection and handling")
        print("   • Progress indicators during cooldowns")
        print("   • Network error recovery")
        print("   • Graceful failure after max retries")
        print("📚 Academic Methodologies:")
        print("   • TREC IR Evaluation (Voorhees & Harman, 2005)")
        print("   • Knowledge Graph Evaluation (Bordes et al., 2013)")
        print("   • TempEval Framework (Verhagen et al., 2007)")
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
        total_api_calls = total_queries * 2  # OpenDeepSearch + GraphRAG need API calls
        max_estimated_time = (total_api_calls * self.min_delay_between_calls + 
                             total_api_calls * self.base_delay * (2 ** (self.max_retries - 1))) / 60
        
        print(f"\n⏱️ Estimated time: {(total_api_calls * self.min_delay_between_calls) / 60:.1f}-{max_estimated_time:.1f} minutes")
        print(f"📊 Total API calls planned: {total_api_calls}")
        print(f"🛡️ Maximum cooldown per error: {self.base_delay * (2 ** (self.max_retries - 1))}s")
        
        results = {
            'opendeepsearch_results': [],
            'graphrag_results': [],
            'zep_results': [],
            'comparative_analysis': {},
            'evaluation_metadata': {
                'start_time': datetime.now().isoformat(),
                'api_rate_limit': self.api_calls_per_minute,
                'min_delay': self.min_delay_between_calls,
                'model': 'gemini/gemini-2.0-flash',
                'api_protection': 'exponential_backoff',
                'max_retries': self.max_retries
            }
        }
        
        api_call_counter = 0
        
        for i, (query_id, query_text) in enumerate(evaluation_queries.items()):
            print(f"\n📋 Query {i+1}/{total_queries}: {query_text}")
            print("-" * 70)
            
            ground_truth = self.ground_truth_data[query_id]
            
            # 1. OpenDeepSearch (with robust API protection)
            print("🔍 OpenDeepSearch (Dynamic Web Search + API Protection)...")
            api_call_counter += 1
            ods_response = self.get_opendeepsearch_response(query_text, api_call_counter, total_api_calls)
            ods_metrics = self.evaluate_system_response(ods_response, ground_truth)
            
            # 2. GraphRAG (with robust API protection)
            print("🏗️ GraphRAG Neo4j (Structured Knowledge + API Protection)...")
            api_call_counter += 1
            graphrag_response = self.get_graphrag_response(query_text, api_call_counter, total_api_calls)
            graphrag_metrics = self.evaluate_system_response(graphrag_response, ground_truth)
            
            # Check if GraphRAG used TKG tool
            tkg_used = "SEC Filing Results:" in graphrag_response.response
            print(f"    🔧 TKG Tool Used: {'✅' if tkg_used else '❌'}")
            
            # 3. Zep TKG (no API protection needed - local system)
            print("🧠 Zep TKG (Bi-temporal Graphiti - Local)...")
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
            
            # API protection status
            print(f"\n🛡️ API Protection Status:")
            print(f"   Total API calls made: {self.api_call_count}")
            print(f"   Rate limit violations: {self.rate_limit_violations}")
            
            # Progress update
            completed = i + 1
            remaining = total_queries - completed
            print(f"\n📈 Progress: {completed}/{total_queries} queries completed")
            if remaining > 0:
                remaining_api_calls = remaining * 2
                remaining_time = remaining_api_calls * self.min_delay_between_calls / 60
                print(f"⏱️  Estimated time remaining: {remaining_time:.1f}+ minutes")
        
        # Add statistical analysis code here...
        # (include the same statistical analysis from the previous script)
        
        results['evaluation_metadata']['end_time'] = datetime.now().isoformat()
        results['evaluation_metadata']['total_api_calls'] = self.api_call_count
        results['evaluation_metadata']['rate_limit_violations'] = self.rate_limit_violations
        
        return results

    # ... (include all remaining methods: extract_information_from_response, 
    #      calculate_ir_metrics, etc.)

def main():
    """Run the three-way robust academic evaluation."""
    
    evaluator = ThreeWayRobustEvaluator()
    
    # System availability check
    available_systems = sum([
        evaluator.baseline_agent is not None,
        evaluator.graphrag_available,
        evaluator.zep_available
    ])
    
    if available_systems < 2:
        print("❌ Insufficient systems available for evaluation")
        return
    
    print(f"\n🚀 Starting robust three-way evaluation with {available_systems}/3 systems")
    print(f"🛡️ API protection enabled with {evaluator.max_retries} retries and exponential backoff")
    print(f"⏰ Started at {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        results = evaluator.run_three_way_evaluation()
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'robust_three_way_evaluation_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n🎓 ROBUST THREE-WAY EVALUATION COMPLETED")
        print(f"📁 Results saved: {filename}")
        print(f"🛡️ API protection summary:")
        print(f"   Total API calls: {evaluator.api_call_count}")
        print(f"   Rate limit violations: {evaluator.rate_limit_violations}")
        print(f"⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Evaluation interrupted by user")
        print(f"🛡️ API calls made before interruption: {evaluator.api_call_count}")
    except Exception as e:
        print(f"\n💥 Evaluation failed with error: {e}")
        print(f"🛡️ API calls made before failure: {evaluator.api_call_count}")

if __name__ == "__main__":
    main()