import json
import random
import os
from itertools import combinations

def generate_sec_queries():
    """Generate comprehensive SEC filing queries"""
    
    companies = [
        'Apple', 'Google', 'Microsoft', 'Amazon', 'Meta', 'Tesla', 'NVIDIA',
        'Netflix', 'Oracle', 'Salesforce', 'Adobe', 'Intel', 'AMD', 'Qualcomm',
        'JPMorgan', 'Bank of America', 'Wells Fargo', 'Goldman Sachs', 'Morgan Stanley',
        'Johnson & Johnson', 'Pfizer', 'UnitedHealth', 'AbbVie', 'Merck',
        'Walmart', 'Home Depot', 'Procter & Gamble', 'Coca-Cola', 'PepsiCo'
    ]
    
    tickers = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NVDA',
        'NFLX', 'ORCL', 'CRM', 'ADBE', 'INTC', 'AMD', 'QCOM',
        'JPM', 'BAC', 'WFC', 'GS', 'MS',
        'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK',
        'WMT', 'HD', 'PG', 'KO', 'PEP'
    ]
    
    form_types = ['10-K', '10-Q', '8-K', 'DEF 14A', '10-K/A', '10-Q/A']
    
    queries = []
    
    # 1. Single filing queries (300 queries)
    single_templates = [
        "When did {company} file its last 10-K annual report?",
        "Show me {company}'s 10-Q quarterly filings in 2023",
        "What 8-K current reports did {company} submit this year?",
        "When was {company}'s most recent proxy statement filed?",
        "Show me all {company} SEC filings in chronological order",
        "What amendments did {company} file in 2023?",
        "When did {company} file its annual report for fiscal year 2023?",
        "Show me {company}'s quarterly filing timeline for 2022",
        "What was {company}'s filing pattern during Q4 2023?",
        "List all {company} filings within 90 days of fiscal year end"
    ]
    
    for template in single_templates:
        for company in companies:
            queries.append(template.format(company=company))
    
    # 2. Filing pattern and timing queries (400 queries)
    pattern_templates = [
        "Which companies filed 10-K within 60 days of fiscal year end in 2023?",
        "Show me companies with the most 8-K current reports in 2023",
        "Find companies that filed amendments within 30 days of original filing",
        "Which companies have the most consistent 10-Q quarterly filing schedule?",
        "Show me filing patterns during earnings season in Q1 2023",
        "Find companies that filed proxy statements earliest in 2023",
        "Which companies had the longest gap between consecutive 10-Q filings?",
        "Show me companies with irregular SEC filing patterns",
        "Find all companies that filed 8-K reports on the same day",
        "Which companies filed the most amendments in 2022?",
        "Show me companies that filed late notices (NT forms)",
        "Find filing clusters: companies filing within 48 hours of each other",
        "Which companies filed 10-K and 10-Q within the same week?",
        "Show me seasonal patterns in SEC filing submissions",
        "Find companies with the shortest time between fiscal year end and 10-K filing",
        "Which companies filed proxy statements closest to annual meeting dates?",
        "Show me companies that consistently meet SEC filing deadlines",
        "Find patterns in weekend vs weekday SEC filings",
        "Which companies had the most XBRL-formatted filings?",
        "Show me filing size patterns: largest vs smallest submissions"
    ]
    
    for template in pattern_templates:
        for i in range(20):  # 20 variations each
            queries.append(template)
    
    # 3. Temporal relationship queries (300 queries)
    temporal_templates = [
        "Show me all 8-K filings within 5 days of quarterly earnings periods",
        "Find companies that filed 10-K and proxy statements within 2 weeks",
        "Which companies filed amendments most quickly after original submissions?",
        "Show me the average time between 10-Q filings for each company",
        "Find correlations between filing timing and market volatility periods",
        "Which filings happened during SEC comment letter periods?",
        "Show me filing patterns around major market events in 2022",
        "Find companies with overlapping SEC filing deadlines",
        "Which companies filed during holiday periods or market closures?",
        "Show me the sequence of filings leading up to major corporate events",
        "Find temporal patterns in insider trading form submissions",
        "Which companies filed beneficial ownership reports after stock movements?",
        "Show me filing cascades: when one company's filing triggers others",
        "Find the relationship between filing timing and stock price changes",
        "Which companies filed registration statements before major announcements?"
    ]
    
    for template in temporal_templates:
        for i in range(20):  # 20 variations each
            queries.append(template)
    
    # 4. Compliance and deadline queries (300 queries)
    compliance_templates = [
        "Which companies filed their 10-K annual reports late in 2023?",
        "Show me companies that consistently meet all SEC filing deadlines",
        "Find all filings submitted exactly on the deadline day",
        "Which companies filed extensions for their annual reports?",
        "Show me the filing timeline for companies with fiscal year changes",
        "Find companies with the shortest time from fiscal year end to 10-K filing",
        "Which companies had the most SEC filing deadline violations?",
        "Show me companies that filed early versus exactly on deadline",
        "Find patterns in accelerated vs non-accelerated filer deadlines",
        "Which companies filed during SEC examination periods?",
        "Show me filing patterns for newly public companies",
        "Find companies that switched from large accelerated to accelerated filer status",
        "Which companies filed the most current reports (8-K) in a single quarter?",
        "Show me proxy statement filing patterns relative to annual meetings",
        "Find companies with the most consistent quarterly filing schedules"
    ]
    
    for template in compliance_templates:
        for i in range(20):  # 20 variations each
            queries.append(template)
    
    # 5. Comparative analysis queries (200 queries)
    comparison_templates = [
        "Compare {company1} and {company2}'s SEC filing schedules",
        "Which filed their 10-K earlier: {company1} or {company2}?",
        "Show me the filing timeline comparison between {company1} and {company2}",
        "Compare amendment patterns between {company1} and {company2}",
        "Which company has more consistent filing timing: {company1} or {company2}?",
        "Compare proxy statement filing dates for {company1} and {company2}",
        "Show me 8-K filing frequency comparison: {company1} vs {company2}",
        "Which company filed more amendments: {company1} or {company2}?"
    ]
    
    company_pairs = list(combinations(companies[:20], 2))[:25]  # 25 pairs
    
    for template in comparison_templates:
        for company1, company2 in company_pairs:
            queries.append(template.format(company1=company1, company2=company2))
    
    # Remove duplicates and shuffle
    unique_queries = list(set(queries))
    random.shuffle(unique_queries)
    
    return unique_queries

if __name__ == "__main__":
    queries = generate_sec_queries()
    
    print(f"Generated {len(queries)} SEC filing queries")
    
    # Save queries
    os.makedirs('sec_filings', exist_ok=True)
    with open('sec_filings/queries.json', 'w') as f:
        json.dump(queries, f, indent=2)
    
    # Save sample for quick testing
    with open('sec_filings/sample_queries.json', 'w') as f:
        json.dump(queries[:100], f, indent=2)
    
    print("SEC filing queries saved")
    print(f"Full queries: sec_filings/queries.json")
    print(f"Sample (100): sec_filings/sample_queries.json")
