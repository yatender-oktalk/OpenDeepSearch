import os
import sys
from datetime import datetime, timedelta
import json
import random

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from dataset_schema import TemporalDataset

def collect_supply_chain_dataset():
    """Collect supply chain disruption data and create standardized dataset"""
    
    # Create dataset
    dataset = TemporalDataset(
        domain="supply_chain",
        description="Supply chain disruption events including port congestion, shipping delays, factory shutdowns, and recovery timelines"
    )
    
    # Add data sources
    dataset.add_data_source(
        source="Maritime Trade Data",
        description="Simulated supply chain disruption events based on real patterns"
    )
    
    # Major ports and shipping routes
    ports = [
        ("Los Angeles", "US", "West Coast"),
        ("Long Beach", "US", "West Coast"), 
        ("Shanghai", "China", "Asia Pacific"),
        ("Shenzhen", "China", "Asia Pacific"),
        ("Rotterdam", "Netherlands", "Europe"),
        ("Hamburg", "Germany", "Europe"),
        ("Singapore", "Singapore", "Asia Pacific"),
        ("Hong Kong", "Hong Kong", "Asia Pacific"),
        ("Antwerp", "Belgium", "Europe"),
        ("Felixstowe", "UK", "Europe")
    ]
    
    # Shipping companies
    carriers = [
        "Maersk", "MSC", "COSCO", "Hapag-Lloyd", "ONE", 
        "Evergreen", "Yang Ming", "HMM", "PIL", "ZIM"
    ]
    
    # Manufacturing regions
    manufacturing_hubs = [
        ("Shenzhen", "China", "Electronics"),
        ("Taiwan", "Taiwan", "Semiconductors"),
        ("Vietnam", "Vietnam", "Textiles"),
        ("Mexico", "Mexico", "Automotive"),
        ("Eastern Europe", "Poland", "Automotive"),
        ("Bangladesh", "Bangladesh", "Textiles"),
        ("Thailand", "Thailand", "Electronics"),
        ("Malaysia", "Malaysia", "Electronics")
    ]
    
    print("Generating supply chain disruption dataset...")
    
    event_counter = 0
    
    # Add port entities
    for port_name, country, region in ports:
        dataset.add_entity(
            entity_id=f"PORT_{port_name.replace(' ', '_').upper()}",
            entity_type="port",
            name=f"Port of {port_name}",
            properties={
                "country": country,
                "region": region,
                "type": "seaport"
            }
        )
    
    # Add carrier entities
    for carrier in carriers:
        dataset.add_entity(
            entity_id=f"CARRIER_{carrier.replace(' ', '_').upper()}",
            entity_type="shipping_company",
            name=carrier,
            properties={
                "industry": "Maritime Shipping",
                "type": "container_carrier"
            }
        )
    
    # Add manufacturing hub entities
    for hub_name, country, industry in manufacturing_hubs:
        dataset.add_entity(
            entity_id=f"HUB_{hub_name.replace(' ', '_').upper()}",
            entity_type="manufacturing_hub",
            name=hub_name,
            properties={
                "country": country,
                "primary_industry": industry,
                "type": "manufacturing_region"
            }
        )
    
    # Generate disruption events (2020-2024)
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # Major known disruptions
    major_disruptions = [
        {
            "name": "COVID-19 Factory Shutdowns",
            "start": "2020-02-01",
            "end": "2020-05-31",
            "type": "pandemic_shutdown",
            "affected_entities": ["HUB_SHENZHEN", "HUB_TAIWAN"],
            "severity": "high"
        },
        {
            "name": "Suez Canal Blockage",
            "start": "2021-03-23",
            "end": "2021-03-29",
            "type": "canal_blockage",
            "affected_entities": ["PORT_ROTTERDAM", "PORT_HAMBURG"],
            "severity": "critical"
        },
        {
            "name": "Shanghai Port Lockdown",
            "start": "2022-03-28",
            "end": "2022-06-01",
            "type": "covid_lockdown",
            "affected_entities": ["PORT_SHANGHAI"],
            "severity": "high"
        },
        {
            "name": "LA/Long Beach Congestion",
            "start": "2021-08-01",
            "end": "2022-02-28",
            "type": "port_congestion",
            "affected_entities": ["PORT_LOS_ANGELES", "PORT_LONG_BEACH"],
            "severity": "high"
        }
    ]
    
    # Add major disruption events
    for disruption in major_disruptions:
        start_dt = datetime.strptime(disruption["start"], '%Y-%m-%d')
        end_dt = datetime.strptime(disruption["end"], '%Y-%m-%d')
        
        for entity_id in disruption["affected_entities"]:
            # Disruption start event
            dataset.add_event(
                event_id=f"DISRUPTION_START_{event_counter}",
                entity_id=entity_id,
                event_type="disruption_start",
                date=disruption["start"],
                timestamp=start_dt.isoformat(),
                details=f"{disruption['name']} begins",
                properties={
                    "disruption_type": disruption["type"],
                    "severity": disruption["severity"],
                    "disruption_name": disruption["name"],
                    "expected_duration": (end_dt - start_dt).days
                }
            )
            event_counter += 1
            
            # Disruption end event
            dataset.add_event(
                event_id=f"DISRUPTION_END_{event_counter}",
                entity_id=entity_id,
                event_type="disruption_end",
                date=disruption["end"],
                timestamp=end_dt.isoformat(),
                details=f"{disruption['name']} ends",
                properties={
                    "disruption_type": disruption["type"],
                    "severity": disruption["severity"],
                    "disruption_name": disruption["name"],
                    "actual_duration": (end_dt - start_dt).days
                }
            )
            event_counter += 1
    
    # Generate additional random disruptions
    disruption_types = [
        "weather_delay", "labor_strike", "equipment_failure", 
        "cyber_attack", "regulatory_delay", "capacity_shortage"
    ]
    
    current_date = start_date
    while current_date < end_date:
        # Random chance of disruption each week
        if random.random() < 0.1:  # 10% chance per week
            
            # Select random entity and disruption type
            all_entities = [f"PORT_{p[0].replace(' ', '_').upper()}" for p in ports]
            all_entities.extend([f"CARRIER_{c.replace(' ', '_').upper()}" for c in carriers])
            all_entities.extend([f"HUB_{h[0].replace(' ', '_').upper()}" for h in manufacturing_hubs])
            
            entity_id = random.choice(all_entities)
            disruption_type = random.choice(disruption_types)
            severity = random.choice(["low", "medium", "high"])
            
            # Random duration (1-30 days)
            duration = random.randint(1, 30)
            end_disruption = current_date + timedelta(days=duration)
            
            # Start event
            dataset.add_event(
                event_id=f"DISRUPTION_START_{event_counter}",
                entity_id=entity_id,
                event_type="disruption_start",
                date=current_date.strftime('%Y-%m-%d'),
                timestamp=current_date.isoformat(),
                details=f"{disruption_type.replace('_', ' ').title()} disruption begins",
                properties={
                    "disruption_type": disruption_type,
                    "severity": severity,
                    "expected_duration": duration,
                    "generated": True
                }
            )
            event_counter += 1
            
            # End event
            dataset.add_event(
                event_id=f"DISRUPTION_END_{event_counter}",
                entity_id=entity_id,
                event_type="disruption_end",
                date=end_disruption.strftime('%Y-%m-%d'),
                timestamp=end_disruption.isoformat(),
                details=f"{disruption_type.replace('_', ' ').title()} disruption ends",
                properties={
                    "disruption_type": disruption_type,
                    "severity": severity,
                    "actual_duration": duration,
                    "generated": True
                }
            )
            event_counter += 1
        
        current_date += timedelta(days=7)  # Move to next week
    
    # Save dataset
    os.makedirs('datasets', exist_ok=True)
    dataset.save('datasets/supply_chain.json')
    
    # Print summary
    summary = dataset.get_summary()
    print("\nSupply Chain Dataset Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return dataset

if __name__ == "__main__":
    dataset = collect_supply_chain_dataset()
