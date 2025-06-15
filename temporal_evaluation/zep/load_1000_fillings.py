# Create: temporal_evaluation/zep/load_1000_filings.py
from tools.zep_temporal_kg_tool import ZepTemporalKGTool
import json
import time

def load_1000_filings():
    """Load 1000 filings for meaningful temporal analysis"""
    print("🚀 Loading 1000 SEC Filings for Temporal Analysis")
    print("=" * 60)
    
    tool = ZepTemporalKGTool()
    
    # Load from actual SEC data
    try:
        with open('../datasets/sec_filings_enhanced.json', 'r') as f:
            sec_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading SEC data: {e}")
        return None
    
    # Extract 1000 filings
    filings_1000 = []
    if isinstance(sec_data, dict):
        # Convert dict to list and take first 1000
        for key, value in list(sec_data.items())[:1000]:
            if isinstance(value, dict):
                value['id'] = key
                filings_1000.append(value)
    elif isinstance(sec_data, list):
        filings_1000 = sec_data[:1000]
    
    print(f"📊 Processing {len(filings_1000)} SEC filings...")
    print(f"💰 Estimated cost: ~{len(filings_1000) * 0.01:.2f} credits")
    
    loaded_count = 0
    batch_size = 20
    
    for i in range(0, len(filings_1000), batch_size):
        batch_end = min(i + batch_size, len(filings_1000))
        batch = filings_1000[i:batch_end]
        
        print(f"\n📦 Processing batch {i//batch_size + 1}: filings {i+1}-{batch_end}")
        
        for j, filing in enumerate(batch):
            # Extract filing info with better error handling
            company = filing.get('company', filing.get('name', filing.get('entity_id', 'Unknown Company')))
            filing_type = filing.get('filing_type', filing.get('type', filing.get('form_type', 'Unknown Filing')))
            date = filing.get('filing_date', filing.get('date', filing.get('timestamp', '2024-01-01')))
            
            # Clean up the date if it has timestamp
            if 'T' in str(date):
                date = str(date).split('T')[0]
            
            # Create structured text optimized for Zep's entity extraction
            filing_text = f"""SEC Filing Event: On {date}, {company} submitted a {filing_type} filing to the Securities and Exchange Commission. 
            
Company: {company}
Filing Type: {filing_type}  
Filing Date: {date}
Regulatory Purpose: This {filing_type} filing provides required financial and business disclosures to investors and regulators.
            
This represents a formal regulatory compliance event in the corporate timeline."""
            
            try:
                tool.client.graph.add(
                    user_id=tool.user_id,
                    type="text",
                    data=filing_text
                )
                loaded_count += 1
                
            except Exception as e:
                print(f"    ❌ Error loading filing {i+j+1}: {e}")
        
        print(f"  ✅ Batch complete. Total loaded: {loaded_count}")
        
        # Pause between batches to respect rate limits
        if i + batch_size < len(filings_1000):
            print("  ⏳ Pausing 10 seconds...")
            time.sleep(10)
    
    print(f"\n🎉 Successfully loaded {loaded_count}/{len(filings_1000)} filings")
    
    # Wait for Zep to process the knowledge graph
    print("⏳ Waiting 5 minutes for Zep to build temporal knowledge graph...")
    print("   (This is where the magic happens - Zep extracts entities and builds relationships)")
    time.sleep(300)
    
    return tool, loaded_count

def test_1000_filings(tool):
    """Test 1000 filings with sophisticated temporal queries"""
    print("\n🧪 Testing 1000 Filings - Temporal Knowledge Graph Analysis:")
    print("=" * 70)
    
    # Advanced temporal queries that showcase TKG capabilities
    advanced_queries = [
        "Which companies show irregular filing patterns compared to their historical schedule?",
        "Show me Apple's complete SEC filing timeline and identify patterns",
        "Compare filing frequencies between Apple, Microsoft, and Meta over time",
        "Find companies with unusual gaps between quarterly filings",
        "Identify seasonal patterns in SEC filing submissions across all companies",
        "Show me the most active filing periods and which companies filed together",
        "Which companies have accelerating or decelerating filing schedules?",
        "Find temporal correlations between different filing types (10-K, 10-Q, 8-K)",
        "Show me companies that tend to file on similar dates (clustering analysis)",
        "Identify anomalies in filing schedules across the entire dataset"
    ]
    
    results = {}
    for i, query in enumerate(advanced_queries, 1):
        print(f"\n[{i}/{len(advanced_queries)}] Advanced Query: {query}")
        print("-" * 70)
        
        start_time = time.time()
        result = tool.forward(query)
        response_time = time.time() - start_time
        
        # Comprehensive analysis
        analysis = analyze_advanced_result(result)
        analysis['response_time'] = response_time
        analysis['query'] = query
        
        results[f"Query_{i}"] = analysis
        
        print(f"📊 Temporal Intelligence Score: {analysis['temporal_score']}/100")
        print(f"📈 Pattern Detection: {analysis['pattern_detection']}")
        print(f"🏢 Companies Identified: {analysis['companies_found']}")
        print(f"📅 Temporal Data Points: {analysis['temporal_data_points']}")
        print(f"⏱️ Response Time: {response_time:.1f}s")
        print(f"📝 Result Length: {len(result)} chars")
        
        # Show preview
        preview = result[:400] + "..." if len(result) > 400 else result
        print(f"Preview: {preview}")
    
    return results

def analyze_advanced_result(result: str) -> dict:
    """Advanced analysis of temporal query results"""
    analysis = {
        'temporal_score': 0,
        'pattern_detection': False,
        'companies_found': 0,
        'temporal_data_points': 0,
        'has_relationships': False,
        'has_anomaly_detection': False,
        'has_comparative_analysis': False
    }
    
    # Temporal intelligence scoring (0-100)
    score = 0
    
    # Company recognition (20 points)
    companies = ["Apple", "Microsoft", "Meta", "Amazon", "Google", "Netflix", "Tesla", "Adobe", "Oracle", "Salesforce"]
    companies_found = sum(1 for company in companies if company in result)
    analysis['companies_found'] = companies_found
    score += min(companies_found * 2, 20)
    
    # Temporal data (25 points)
    temporal_indicators = ["2024-", "2023-", "2022-", "Valid From:", "Valid Until:", "filed", "timeline", "pattern"]
    temporal_count = sum(1 for indicator in temporal_indicators if indicator in result)
    analysis['temporal_data_points'] = temporal_count
    score += min(temporal_count * 3, 25)
    
    # Pattern detection (20 points)
    pattern_words = ["pattern", "irregular", "frequency", "trend", "schedule", "correlation", "clustering"]
    if any(word in result.lower() for word in pattern_words):
        analysis['pattern_detection'] = True
        score += 20
    
    # Relationship quality (15 points)
    if "Temporal Relationship:" in result or "Knowledge Graph" in result:
        analysis['has_relationships'] = True
        score += 15
    
    # Anomaly detection (10 points)
    anomaly_words = ["anomaly", "unusual", "deviation", "outlier", "irregular"]
    if any(word in result.lower() for word in anomaly_words):
        analysis['has_anomaly_detection'] = True
        score += 10
    
    # Comparative analysis (10 points)
    comparative_words = ["compare", "between", "versus", "correlation", "similar", "different"]
    if any(word in result.lower() for word in comparative_words):
        analysis['has_comparative_analysis'] = True
        score += 10
    
    analysis['temporal_score'] = score
    return analysis

def print_final_summary(results):
    """Print comprehensive summary of 1000 filing analysis"""
    print("\n🎯 FINAL SUMMARY - 1000 Filings Temporal Analysis:")
    print("=" * 70)
    
    avg_temporal_score = sum(r['temporal_score'] for r in results.values()) / len(results)
    avg_response_time = sum(r['response_time'] for r in results.values()) / len(results)
    total_companies = sum(r['companies_found'] for r in results.values())
    pattern_detection_rate = sum(1 for r in results.values() if r['pattern_detection']) / len(results) * 100
    
    print(f"📊 Average Temporal Intelligence Score: {avg_temporal_score:.1f}/100")
    print(f"⏱️ Average Response Time: {avg_response_time:.1f}s")
    print(f"🏢 Total Company Mentions: {total_companies}")
    print(f"📈 Pattern Detection Rate: {pattern_detection_rate:.1f}%")
    
    if avg_temporal_score >= 70:
        print("🎉 EXCELLENT - Ready for full evaluation!")
    elif avg_temporal_score >= 50:
        print("👍 GOOD - Minor improvements needed")
    else:
        print("⚠️ NEEDS WORK - Significant issues to address")

if __name__ == "__main__":
    # Load 1000 filings
    tool, loaded_count = load_1000_filings()
    
    if tool and loaded_count > 0:
        # Test with advanced queries
        results = test_1000_filings(tool)
        
        # Print final summary
        print_final_summary(results)
    else:
        print("❌ Failed to load data")