import requests
import time
import os
import sys
from datetime import datetime, timedelta
import json

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from dataset_schema import TemporalDataset

def collect_enhanced_sec_dataset():
    """Collect comprehensive SEC filings data"""
    
    dataset = TemporalDataset(
        domain="sec_filings_enhanced",
        description="Comprehensive SEC regulatory filings for 50+ major public companies over 5+ years"
    )
    
    dataset.add_data_source(
        source="SEC EDGAR Database",
        url="https://www.sec.gov/edgar",
        description="Official SEC database - comprehensive collection"
    )
    
    # 50+ major companies with CIK numbers
    companies = {
        # Tech Giants
        'AAPL': ('0000320193', 'Apple Inc.'),
        'GOOGL': ('0001652044', 'Alphabet Inc.'),
        'MSFT': ('0000789019', 'Microsoft Corporation'),
        'AMZN': ('0001018724', 'Amazon.com Inc.'),
        'META': ('0001326801', 'Meta Platforms Inc.'),
        'TSLA': ('0001318605', 'Tesla Inc.'),
        'NVDA': ('0001045810', 'NVIDIA Corporation'),
        'NFLX': ('0001065280', 'Netflix Inc.'),
        'ORCL': ('0000077476', 'Oracle Corporation'),
        'CRM': ('0001108524', 'Salesforce Inc.'),
        'ADBE': ('0000796343', 'Adobe Inc.'),
        'INTC': ('0000050863', 'Intel Corporation'),
        'AMD': ('0000002488', 'Advanced Micro Devices'),
        'QCOM': ('0000804328', 'Qualcomm Inc.'),
        
        # Financial
        'JPM': ('0000019617', 'JPMorgan Chase & Co.'),
        'BAC': ('0000070858', 'Bank of America Corp'),
        'WFC': ('0000072971', 'Wells Fargo & Company'),
        'GS': ('0000886982', 'Goldman Sachs Group Inc'),
        'MS': ('0000895421', 'Morgan Stanley'),
        'C': ('0000831001', 'Citigroup Inc.'),
        'V': ('0001403161', 'Visa Inc.'),
        'MA': ('0001141391', 'Mastercard Inc.'),
        'PYPL': ('0001633917', 'PayPal Holdings Inc.'),
        
        # Healthcare/Pharma
        'JNJ': ('0000200406', 'Johnson & Johnson'),
        'PFE': ('0000078003', 'Pfizer Inc.'),
        'UNH': ('0000731766', 'UnitedHealth Group Inc.'),
        'ABBV': ('0001551152', 'AbbVie Inc.'),
        'MRK': ('0000310158', 'Merck & Co. Inc.'),
        'TMO': ('0000097745', 'Thermo Fisher Scientific'),
        'ABT': ('0000001800', 'Abbott Laboratories'),
        'LLY': ('0000059478', 'Eli Lilly and Company'),
        
        # Consumer/Retail
        'WMT': ('0000104169', 'Walmart Inc.'),
        'HD': ('0000354950', 'Home Depot Inc.'),
        'PG': ('0000080424', 'Procter & Gamble Company'),
        'KO': ('0000021344', 'Coca-Cola Company'),
        'PEP': ('0000077476', 'PepsiCo Inc.'),
        'COST': ('0000909832', 'Costco Wholesale Corp'),
        'TGT': ('0000027419', 'Target Corporation'),
        'SBUX': ('0000829224', 'Starbucks Corporation'),
        
        # Energy/Industrial
        'XOM': ('0000034088', 'Exxon Mobil Corporation'),
        'CVX': ('0000093410', 'Chevron Corporation'),
        'CAT': ('0000018230', 'Caterpillar Inc.'),
        'BA': ('0000012927', 'Boeing Company'),
        'GE': ('0000040545', 'General Electric Company'),
        'MMM': ('0000066740', '3M Company'),
        
        # Growth/Recent IPOs
        'UBER': ('0001543151', 'Uber Technologies Inc.'),
        'LYFT': ('0001759509', 'Lyft Inc.'),
        'SNAP': ('0001564408', 'Snap Inc.'),
        'SPOT': ('0001639920', 'Spotify Technology S.A.'),
        'ZOOM': ('0001585521', 'Zoom Video Communications'),
        'SHOP': ('0001594805', 'Shopify Inc.'),
        'SQ': ('0001512673', 'Block Inc.'),
        'ROKU': ('0001428439', 'Roku Inc.')
    }
    
    headers = {
        'User-Agent': 'Research Project contact@university.edu',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'data.sec.gov'
    }
    
    # All important form types
    important_forms = [
        '10-K', '10-Q', '8-K', 'DEF 14A', 'DEF 14C',
        '10-K/A', '10-Q/A', '8-K/A', 'S-1', 'S-3', 'S-4',
        '20-F', '40-F', 'SC 13D', 'SC 13G', '3', '4', '5',
        '11-K', 'DEFA14A', 'NT 10-K', 'NT 10-Q'
    ]
    
    print(f"Collecting enhanced SEC data for {len(companies)} companies...")
    print(f"Target: 5+ years of data, {len(important_forms)} form types")
    
    event_counter = 0
    cutoff_date = datetime.now() - timedelta(days=1825)  # 5 years
    
    for ticker, (cik, company_name) in companies.items():
        try:
            print(f"Processing {ticker} ({company_name})...")
            
            # Add company entity
            dataset.add_entity(
                entity_id=ticker,
                entity_type="public_company",
                name=company_name,
                properties={
                    "cik": cik,
                    "ticker": ticker,
                    "sector": get_sector(ticker),
                    "exchange": get_exchange(ticker)
                }
            )
            
            # Get company filings
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                filings = data.get('filings', {}).get('recent', {})
                
                # Process each filing
                forms = filings.get('form', [])
                filing_dates = filings.get('filingDate', [])
                acceptance_dates = filings.get('acceptanceDateTime', [])
                accession_numbers = filings.get('accessionNumber', [])
                sizes = filings.get('size', [])
                is_xbrl = filings.get('isXBRL', [])
                
                for i in range(len(forms)):
                    form_type = forms[i]
                    filing_date = filing_dates[i] if i < len(filing_dates) else None
                    
                    if not filing_date or form_type not in important_forms:
                        continue
                    
                    try:
                        filing_dt = datetime.strptime(filing_date, '%Y-%m-%d')
                        if filing_dt < cutoff_date:
                            continue
                    except:
                        continue
                    
                    # Categorize filing
                    category = categorize_filing(form_type)
                    
                    dataset.add_event(
                        event_id=f"{ticker}_FILING_{event_counter}",
                        entity_id=ticker,
                        event_type="sec_filing",
                        date=filing_date,
                        timestamp=filing_date + 'T00:00:00',
                        details=f"{company_name} filed {form_type}",
                        properties={
                            'form_type': form_type,
                            'accession_number': accession_numbers[i] if i < len(accession_numbers) else None,
                            'file_size': sizes[i] if i < len(sizes) else 0,
                            'is_xbrl': is_xbrl[i] if i < len(is_xbrl) else False,
                            'acceptance_datetime': acceptance_dates[i] if i < len(acceptance_dates) else None,
                            'category': category,
                            'is_amendment': "/A" in form_type,
                            'is_late_filing': "NT" in form_type,
                            'quarter': get_quarter(filing_date),
                            'fiscal_year': get_fiscal_year(filing_date)
                        }
                    )
                    event_counter += 1
            
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    # Save dataset
    os.makedirs('datasets', exist_ok=True)
    dataset.save('datasets/sec_filings_enhanced.json')
    
    print(f"\nEnhanced SEC Dataset Summary:")
    summary = dataset.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return dataset

def categorize_filing(form_type):
    """Categorize filing types"""
    if form_type in ['10-K', '10-K/A']:
        return 'annual_report'
    elif form_type in ['10-Q', '10-Q/A']:
        return 'quarterly_report'
    elif form_type in ['8-K', '8-K/A']:
        return 'current_report'
    elif 'DEF 14' in form_type:
        return 'proxy_statement'
    elif form_type in ['S-1', 'S-3', 'S-4']:
        return 'registration_statement'
    elif form_type in ['3', '4', '5']:
        return 'insider_trading'
    elif form_type in ['SC 13D', 'SC 13G']:
        return 'beneficial_ownership'
    elif 'NT' in form_type:
        return 'late_filing_notice'
    else:
        return 'other_filing'

def get_quarter(date_str):
    """Get quarter from date"""
    month = int(date_str.split('-')[1])
    return f"Q{(month-1)//3 + 1}"

def get_fiscal_year(date_str):
    """Get fiscal year from date"""
    return date_str.split('-')[0]

def get_sector(ticker):
    """Get sector for ticker"""
    sector_map = {
        # Tech
        'AAPL': 'Technology', 'GOOGL': 'Technology', 'MSFT': 'Technology',
        'AMZN': 'Technology', 'META': 'Technology', 'TSLA': 'Technology',
        'NVDA': 'Technology', 'NFLX': 'Technology', 'ORCL': 'Technology',
        'CRM': 'Technology', 'ADBE': 'Technology', 'INTC': 'Technology',
        'AMD': 'Technology', 'QCOM': 'Technology',
        
        # Financial
        'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial',
        'GS': 'Financial', 'MS': 'Financial', 'C': 'Financial',
        'V': 'Financial', 'MA': 'Financial', 'PYPL': 'Financial',
        
        # Healthcare
        'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare',
        'ABBV': 'Healthcare', 'MRK': 'Healthcare', 'TMO': 'Healthcare',
        'ABT': 'Healthcare', 'LLY': 'Healthcare',
        
        # Consumer
        'WMT': 'Consumer', 'HD': 'Consumer', 'PG': 'Consumer',
        'KO': 'Consumer', 'PEP': 'Consumer', 'COST': 'Consumer',
        'TGT': 'Consumer', 'SBUX': 'Consumer',
        
        # Energy/Industrial
        'XOM': 'Energy', 'CVX': 'Energy', 'CAT': 'Industrial',
        'BA': 'Industrial', 'GE': 'Industrial', 'MMM': 'Industrial'
    }
    return sector_map.get(ticker, 'Other')

def get_exchange(ticker):
    """Get exchange for ticker"""
    # Most are NASDAQ or NYSE
    nasdaq_tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX']
    return 'NASDAQ' if ticker in nasdaq_tickers else 'NYSE'

if __name__ == "__main__":
    dataset = collect_enhanced_sec_dataset()