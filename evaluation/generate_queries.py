import random
from itertools import combinations, product

# Company data
companies = {
    'AAPL': 'Apple',
    'GOOGL': 'Google', 
    'MSFT': 'Microsoft',
    'TSLA': 'Tesla',
    'AMZN': 'Amazon',
    'META': 'Facebook',
    'NVDA': 'Nvidia',
    'NFLX': 'Netflix',
    'ORCL': 'Oracle',
    'CRM': 'Salesforce',
    'UBER': 'Uber',
    'LYFT': 'Lyft',
    'SNAP': 'Snapchat',
    'TWTR': 'Twitter',
    'SPOT': 'Spotify'
}

# Event types
event_types = ['stock split', 'IPO', 'dividend', 'earnings', 'acquisition']

# Time periods
time_periods = [
    '2020', '2021', '2022', '2023', '2024',
    'Q1 2020', 'Q2 2021', 'Q3 2022', 'Q4 2023',
    'January 2020', 'March 2021', 'June 2022',
    'between 2020 and 2022', 'after 2019', 'before 2024'
]

def generate_single_event_queries():
    """Generate queries about single events"""
    templates = [
        "When did {company} have its {event}?",
        "What was the date of {company}'s {event}?", 
        "Show me {company}'s {event} date",
        "When exactly did {company} {event_verb}?",
        "What happened when {company} had its {event}?",
        "Give me the exact date of {company}'s {event}",
        "When was {company}'s {event} announced?",
        "Show me details of {company}'s {event}"
    ]
    
    event_verbs = {
        'stock split': 'split its stock',
        'IPO': 'go public', 
        'dividend': 'pay dividends',
        'earnings': 'report earnings',
        'acquisition': 'make an acquisition'
    }
    
    queries = []
    for template in templates:
        for ticker, company in companies.items():
            for event in event_types:
                query = template.format(
                    company=company,
                    event=event,
                    event_verb=event_verbs.get(event, event)
                )
                queries.append(query)
    
    return queries

def generate_comparison_queries():
    """Generate comparison queries between companies"""
    templates = [
        "Compare {company1} and {company2}'s {event} dates",
        "Which happened first: {company1}'s {event} or {company2}'s {event}?",
        "Show me {company1} vs {company2} {event} timeline",
        "Who had their {event} earlier: {company1} or {company2}?",
        "Compare the {event} timing of {company1} and {company2}",
        "Which company had their {event} first: {company1} or {company2}?",
        "Show me the chronological order of {event} for {company1} and {company2}",
        "Compare {company1} and {company2}'s {event} performance"
    ]
    
    queries = []
    company_pairs = list(combinations(companies.items(), 2))
    
    for template in templates:
        for (ticker1, company1), (ticker2, company2) in company_pairs[:20]:  # Limit pairs
            for event in event_types:
                query = template.format(
                    company1=company1,
                    company2=company2, 
                    event=event
                )
                queries.append(query)
    
    return queries

def generate_temporal_range_queries():
    """Generate queries with time ranges"""
    templates = [
        "Show me all {event} events in {period}",
        "Which companies had {event} in {period}?",
        "List all {event} that happened {period}",
        "Show me {company}'s events in {period}",
        "What {event} occurred {period}?",
        "Find all companies that had {event} {period}",
        "Show me the timeline of {event} events {period}",
        "Which {event} happened {period}?"
    ]
    
    queries = []
    for template in templates:
        for event in event_types:
            for period in time_periods:
                if '{company}' in template:
                    for ticker, company in list(companies.items())[:10]:  # Limit companies
                        query = template.format(event=event, period=period, company=company)
                        queries.append(query)
                else:
                    query = template.format(event=event, period=period)
                    queries.append(query)
    
    return queries

def generate_sequence_queries():
    """Generate queries about event sequences"""
    templates = [
        "Show me {company}'s complete timeline",
        "What happened to {company} between {start_year} and {end_year}?",
        "List all {company} events chronologically", 
        "Show me {company}'s major events in order",
        "What was the sequence of events for {company}?",
        "Give me {company}'s event timeline",
        "Show me all {company} activities from {start_year} to {end_year}",
        "What major events happened to {company}?"
    ]
    
    year_ranges = [
        ('2020', '2022'), ('2021', '2023'), ('2019', '2021'),
        ('2020', '2024'), ('2018', '2020'), ('2022', '2024')
    ]
    
    queries = []
    for template in templates:
        for ticker, company in companies.items():
            if '{start_year}' in template:
                for start_year, end_year in year_ranges:
                    query = template.format(
                        company=company,
                        start_year=start_year,
                        end_year=end_year
                    )
                    queries.append(query)
            else:
                query = template.format(company=company)
                queries.append(query)
    
    return queries

def generate_analytical_queries():
    """Generate analytical/pattern queries"""
    templates = [
        "How many companies had {event} in {period}?",
        "What's the average time between {event1} and {event2}?",
        "Which companies had multiple {event} events?",
        "Show me the pattern of {event} timing across companies",
        "Find companies that had {event} within 6 months of each other",
        "What's the trend in {event} timing over the years?",
        "Which {event} events happened closest together?",
        "Show me companies with similar {event} patterns"
    ]
    
    queries = []
    for template in templates:
        for event in event_types:
            for period in time_periods[:5]:  # Limit periods
                if '{event1}' in template:
                    for event2 in event_types:
                        if event != event2:
                            query = template.format(event1=event, event2=event2)
                            queries.append(query)
                            break
                elif '{period}' in template:
                    query = template.format(event=event, period=period)
                    queries.append(query)
                else:
                    query = template.format(event=event)
                    queries.append(query)
    
    return queries

def generate_all_queries():
    """Generate all query types"""
    all_queries = []
    
    print("Generating single event queries...")
    all_queries.extend(generate_single_event_queries())
    
    print("Generating comparison queries...")
    all_queries.extend(generate_comparison_queries())
    
    print("Generating temporal range queries...")
    all_queries.extend(generate_temporal_range_queries())
    
    print("Generating sequence queries...")
    all_queries.extend(generate_sequence_queries())
    
    print("Generating analytical queries...")
    all_queries.extend(generate_analytical_queries())
    
    # Remove duplicates and shuffle
    unique_queries = list(set(all_queries))
    random.shuffle(unique_queries)
    
    return unique_queries

if __name__ == "__main__":
    queries = generate_all_queries()
    
    print(f"Generated {len(queries)} unique queries")
    
    # Save to file
    with open('test_queries_large.txt', 'w') as f:
        for i, query in enumerate(queries, 1):
            f.write(f"{i}. {query}\n")
    
    # Save first 100 for quick testing
    with open('test_queries_sample.txt', 'w') as f:
        for i, query in enumerate(queries[:100], 1):
            f.write(f"{i}. {query}\n")
    
    print(f"Saved {len(queries)} queries to test_queries_large.txt")
    print(f"Saved first 100 queries to test_queries_sample.txt")
    
    # Show some examples
    print("\nSample queries:")
    for i, query in enumerate(queries[:10], 1):
        print(f"{i}. {query}")