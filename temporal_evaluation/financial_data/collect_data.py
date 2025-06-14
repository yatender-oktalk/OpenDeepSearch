import yfinance as yf
import os
import sys
from datetime import datetime, timedelta

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from dataset_schema import TemporalDataset

def collect_financial_dataset():
    """Collect financial data and create standardized dataset"""
    
    # Create dataset
    dataset = TemporalDataset(
        domain="financial_markets",
        description="Stock market events including IPOs, stock splits, dividends, and corporate actions for major tech companies"
    )
    
    # Add data sources
    dataset.add_data_source(
        source="Yahoo Finance API",
        url="https://finance.yahoo.com",
        description="Real-time and historical stock market data"
    )
    
    companies = [
        ('AAPL', 'Apple Inc.'),
        ('GOOGL', 'Alphabet Inc.'),
        ('MSFT', 'Microsoft Corporation'),
        ('TSLA', 'Tesla Inc.'),
        ('AMZN', 'Amazon.com Inc.'),
        ('META', 'Meta Platforms Inc.'),
        ('NVDA', 'NVIDIA Corporation'),
        ('NFLX', 'Netflix Inc.'),
        ('ORCL', 'Oracle Corporation'),
        ('CRM', 'Salesforce Inc.'),
        ('UBER', 'Uber Technologies Inc.'),
        ('LYFT', 'Lyft Inc.'),
        ('SNAP', 'Snap Inc.'),
        ('SPOT', 'Spotify Technology S.A.'),
        ('ZOOM', 'Zoom Video Communications'),
        ('SHOP', 'Shopify Inc.'),
        ('SQ', 'Block Inc.'),
        ('PYPL', 'PayPal Holdings Inc.'),
        ('ADBE', 'Adobe Inc.'),
        ('TWTR', 'Twitter Inc.')  # Historical data
    ]
    
    print(f"Collecting financial data for {len(companies)} companies...")
    
    event_counter = 0
    
    for ticker, company_name in companies:
        try:
            print(f"Processing {ticker} ({company_name})...")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Add company entity
            dataset.add_entity(
                entity_id=ticker,
                entity_type="public_company",
                name=company_name,
                properties={
                    "sector": info.get("sector", "Technology"),
                    "industry": info.get("industry", "Unknown"),
                    "market_cap": info.get("marketCap", 0),
                    "country": info.get("country", "US"),
                    "exchange": info.get("exchange", "NASDAQ"),
                    "currency": info.get("currency", "USD")
                }
            )
            
            # IPO Event
            if 'firstTradeDateEpochUtc' in info and info['firstTradeDateEpochUtc']:
                ipo_date = datetime.fromtimestamp(info['firstTradeDateEpochUtc'])
                dataset.add_event(
                    event_id=f"{ticker}_IPO_{event_counter}",
                    entity_id=ticker,
                    event_type="ipo",
                    date=ipo_date.strftime('%Y-%m-%d'),
                    timestamp=ipo_date.isoformat(),
                    details=f"{company_name} Initial Public Offering",
                    properties={
                        "shares_outstanding": info.get("sharesOutstanding", 0),
                        "ipo_price": info.get("ipoPrice", 0),
                        "exchange": info.get("exchange", "NASDAQ")
                    }
                )
                event_counter += 1
            
            # Stock Splits
            splits = stock.splits
            for split_date, ratio in splits.items():
                dataset.add_event(
                    event_id=f"{ticker}_SPLIT_{event_counter}",
                    entity_id=ticker,
                    event_type="stock_split",
                    date=split_date.strftime('%Y-%m-%d'),
                    timestamp=split_date.isoformat(),
                    details=f"{company_name} {ratio}:1 stock split",
                    properties={
                        "split_ratio": float(ratio),
                        "pre_split_shares": 0,  # Would need additional API call
                        "post_split_shares": 0
                    }
                )
                event_counter += 1
            
            # Dividends (last 5 years)
            dividends = stock.dividends
            five_years_ago = datetime.now() - timedelta(days=1825)
            
            for div_date, amount in dividends.items():
                if div_date >= five_years_ago:
                    dataset.add_event(
                        event_id=f"{ticker}_DIV_{event_counter}",
                        entity_id=ticker,
                        event_type="dividend_payment",
                        date=div_date.strftime('%Y-%m-%d'),
                        timestamp=div_date.isoformat(),
                        details=f"{company_name} dividend payment of ${amount:.2f}",
                        properties={
                            "dividend_amount": float(amount),
                            "currency": "USD",
                            "payment_type": "regular",
                            "yield_percentage": 0  # Would need calculation
                        }
                    )
                    event_counter += 1
            
            # Market Cap Milestones (if current market cap > 1T)
            current_market_cap = info.get("marketCap", 0)
            if current_market_cap > 1e12:  # Trillion dollar club
                # Approximate date (would need historical data for exact date)
                milestone_date = datetime.now()
                dataset.add_event(
                    event_id=f"{ticker}_MILESTONE_{event_counter}",
                    entity_id=ticker,
                    event_type="market_cap_milestone",
                    date=milestone_date.strftime('%Y-%m-%d'),
                    timestamp=milestone_date.isoformat(),
                    details=f"{company_name} reached $1 trillion market capitalization",
                    properties={
                        "milestone_value": current_market_cap,
                        "milestone_type": "trillion_dollar_club",
                        "currency": "USD",
                        "approximate_date": True
                    }
                )
                event_counter += 1
                
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    # Save dataset
    os.makedirs('datasets', exist_ok=True)
    dataset.save('datasets/financial_data.json')
    
    # Print summary
    summary = dataset.get_summary()
    print("\nDataset Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return dataset

if __name__ == "__main__":
    dataset = collect_financial_dataset()


# Add this function at the top to handle timezone issues
def make_timezone_naive(dt):
    """Convert timezone-aware datetime to naive"""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

