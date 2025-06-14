import requests
import xml.etree.ElementTree as ET
import os
import sys
from datetime import datetime, timedelta
import json
import time

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from dataset_schema import TemporalDataset

def collect_clinical_trials_dataset():
    """Collect clinical trials data and create standardized dataset"""
    
    # Create dataset
    dataset = TemporalDataset(
        domain="clinical_trials",
        description="Clinical trial data including study phases, enrollment periods, completion dates, and regulatory milestones"
    )
    
    # Add data sources
    dataset.add_data_source(
        source="ClinicalTrials.gov",
        url="https://clinicaltrials.gov",
        description="U.S. National Library of Medicine clinical trials database"
    )
    
    # Major therapeutic areas and conditions
    conditions = [
        "Cancer", "Diabetes", "Alzheimer Disease", "COVID-19", "Heart Disease",
        "Hypertension", "Depression", "Asthma", "Arthritis", "Stroke",
        "Parkinson Disease", "Multiple Sclerosis", "Epilepsy", "Obesity"
    ]
    
    # Major pharmaceutical companies (sponsors)
    sponsors = [
        "Pfizer", "Johnson & Johnson", "Roche", "Novartis", "Merck",
        "Bristol-Myers Squibb", "AbbVie", "Amgen", "Gilead Sciences",
        "Biogen", "Moderna", "Regeneron"
    ]
    
    print(f"Collecting clinical trials for {len(conditions)} conditions...")
    
    event_counter = 0
    trial_counter = 0
    
    for condition in conditions:
        try:
            print(f"Processing trials for {condition}...")
            
            # ClinicalTrials.gov API
            base_url = "https://clinicaltrials.gov/api/query/study_fields"
            
            fields = [
                "NCTId", "BriefTitle", "StudyType", "Phase", "StudyFirstSubmitDate",
                "StudyFirstPostDate", "LastUpdateSubmitDate", "StartDate", 
                "CompletionDate", "PrimaryCompletionDate", "OverallStatus",
                "Condition", "InterventionName", "LeadSponsorName", "EnrollmentCount"
            ]
            
            params = {
                "expr": condition,
                "fields": ",".join(fields),
                "min_rnk": 1,
                "max_rnk": 200,  # 200 trials per condition
                "fmt": "json"
            }
            
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                studies = data.get("StudyFieldsResponse", {}).get("StudyFields", [])
                
                for study in studies:
                    nct_id = study.get("NCTId", [None])[0]
                    if not nct_id:
                        continue
                    
                    title = study.get("BriefTitle", ["Unknown"])[0]
                    study_type = study.get("StudyType", ["Unknown"])[0]
                    phase = study.get("Phase", ["Unknown"])[0]
                    sponsor = study.get("LeadSponsorName", ["Unknown"])[0]
                    status = study.get("OverallStatus", ["Unknown"])[0]
                    enrollment = study.get("EnrollmentCount", [0])[0]
                    
                    # Add trial as entity
                    dataset.add_entity(
                        entity_id=nct_id,
                        entity_type="clinical_trial",
                        name=title,
                        properties={
                            "study_type": study_type,
                            "phase": phase,
                            "condition": condition,
                            "sponsor": sponsor,
                            "status": status,
                            "enrollment_count": enrollment
                        }
                    )
                    
                    # Add sponsor as entity if it's a major pharma company
                    if sponsor in sponsors:
                        dataset.add_entity(
                            entity_id=sponsor.replace(" ", "_").upper(),
                            entity_type="pharmaceutical_company",
                            name=sponsor,
                            properties={
                                "industry": "Pharmaceutical",
                                "type": "Sponsor"
                            }
                        )
                        
                        # Add relationship
                        dataset.add_relationship(
                            from_entity=sponsor.replace(" ", "_").upper(),
                            to_entity=nct_id,
                            relationship_type="SPONSORS"
                        )
                    
                    # Process dates and create events
                    date_fields = {
                        "StudyFirstSubmitDate": "study_submitted",
                        "StudyFirstPostDate": "study_posted", 
                        "StartDate": "study_started",
                        "PrimaryCompletionDate": "primary_completion",
                        "CompletionDate": "study_completed"
                    }
                    
                    for field, event_type in date_fields.items():
                        date_value = study.get(field, [None])[0]
                        if date_value:
                            try:
                                # Parse date (format can vary)
                                if len(date_value) == 10:  # YYYY-MM-DD
                                    date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                                elif len(date_value) == 7:  # YYYY-MM
                                    date_obj = datetime.strptime(date_value + '-01', '%Y-%m-%d')
                                elif len(date_value) == 4:  # YYYY
                                    date_obj = datetime.strptime(date_value + '-01-01', '%Y-%m-%d')
                                else:
                                    continue
                                
                                # Only include recent trials (last 10 years)
                                if date_obj.replace(tzinfo=None) >= datetime.now() - timedelta(days=3650):
                                    dataset.add_event(
                                        event_id=f"{nct_id}_{event_type.upper()}_{event_counter}",
                                        entity_id=nct_id,
                                        event_type=event_type,
                                        date=date_obj.strftime('%Y-%m-%d'),
                                        timestamp=date_obj.isoformat(),
                                        details=f"Trial {nct_id} {event_type.replace('_', ' ')}",
                                        properties={
                                            "phase": phase,
                                            "condition": condition,
                                            "sponsor": sponsor,
                                            "status": status,
                                            "enrollment": enrollment
                                        }
                                    )
                                    event_counter += 1
                                    
                            except ValueError:
                                continue
                    
                    trial_counter += 1
            
            # Rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error processing {condition}: {e}")
            continue
    
    # Save dataset
    os.makedirs('datasets', exist_ok=True)
    dataset.save('datasets/clinical_trials.json')
    
    # Print summary
    summary = dataset.get_summary()
    print(f"\nClinical Trials Dataset Summary:")
    print(f"  Trials processed: {trial_counter}")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return dataset

if __name__ == "__main__":
    dataset = collect_clinical_trials_dataset()
    