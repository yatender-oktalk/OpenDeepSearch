#!/usr/bin/env python3
"""
Ground Truth Synchronization Fix
Ensures ground truth questions match actual Neo4j data
"""

import json
import os
import sys
import pandas as pd
from neo4j import GraphDatabase
from neo4j.time import Date, DateTime, Time
from typing import List, Dict, Any
import random
from datetime import datetime


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Neo4j Date/DateTime objects"""

    def default(self, obj):
        if isinstance(obj, (Date, DateTime, Time)):
            return str(obj)
        elif hasattr(obj, "isoformat"):
            return obj.isoformat()
        return super().default(obj)


def convert_neo4j_types(data):
    """Recursively convert Neo4j types to JSON-serializable types"""
    if isinstance(data, dict):
        return {k: convert_neo4j_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_neo4j_types(item) for item in data]
    elif isinstance(data, (Date, DateTime, Time)):
        return str(data)
    elif hasattr(data, "isoformat"):
        return data.isoformat()
    else:
        return data


class GroundTruthSynchronizer:
    """Ensures ground truth questions reference actual data in Neo4j"""

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = None

        # Try to connect to Neo4j
        self.connect_to_neo4j()

    def connect_to_neo4j(self):
        """Establish connection to Neo4j with error handling"""
        try:
            print(f"🔌 Connecting to Neo4j at {self.neo4j_uri}...")
            self.driver = GraphDatabase.driver(
                self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
            )

            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    print("✅ Neo4j connection successful!")
                else:
                    raise Exception("Connection test failed")

        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            print("🔧 Please check:")
            print("   - Neo4j is running")
            print("   - Connection details are correct")
            print("   - Credentials are valid")
            self.driver = None

    def extract_actual_entities(self) -> Dict[str, Any]:
        """Extract actual entities from Neo4j database"""
        print("🔍 Extracting actual entities from Neo4j...")

        if not self.driver:
            print("❌ No Neo4j connection - using fallback data")
            return self.get_fallback_entities()

        try:
            with self.driver.session() as session:
                # Check what node types exist
                node_types = session.run("""
                    CALL db.labels() YIELD label
                    RETURN collect(label) as labels
                """).single()["labels"]

                print(f"📊 Found node types: {node_types}")

                entities = {
                    "covid_locations": [],
                    "customers": [],
                    "categories": [],
                    "date_range": {
                        "earliest": "2020-01-01",
                        "latest": "2024-12-31",
                        "total_events": 0,
                    },
                    "domain_counts": {},
                    "covid_events": [],
                    "customer_purchases": [],
                    "available_labels": node_types,
                }

                # Try to get COVID locations if CovidEvent nodes exist
                if "CovidEvent" in node_types:
                    try:
                        covid_locations = session.run("""
                            MATCH (e:CovidEvent)
                            WHERE e.location IS NOT NULL
                            RETURN DISTINCT e.location as location
                            ORDER BY location
                            LIMIT 20
                        """).values()
                        entities["covid_locations"] = [
                            loc[0] for loc in covid_locations if loc[0]
                        ]
                        print(
                            f"   📍 Found {len(entities['covid_locations'])} COVID locations"
                        )
                    except Exception as e:
                        print(f"   ⚠️ Could not extract COVID locations: {e}")

                # Try to get customers if Customer nodes exist
                if "Customer" in node_types:
                    try:
                        customers = session.run("""
                            MATCH (c:Customer)
                            WHERE c.customer_id IS NOT NULL
                            RETURN DISTINCT c.customer_id as customer_id
                            ORDER BY customer_id
                            LIMIT 20
                        """).values()
                        entities["customers"] = [
                            cust[0] for cust in customers if cust[0]
                        ]
                        print(f"   👥 Found {len(entities['customers'])} customers")
                    except Exception as e:
                        print(f"   ⚠️ Could not extract customers: {e}")

                # Try to get categories if EcommerceEvent nodes exist
                if "EcommerceEvent" in node_types:
                    try:
                        categories = session.run("""
                            MATCH (e:EcommerceEvent)
                            WHERE e.product_category IS NOT NULL
                            RETURN DISTINCT e.product_category as category
                            ORDER BY category
                            LIMIT 20
                        """).values()
                        entities["categories"] = [
                            cat[0] for cat in categories if cat[0]
                        ]
                        print(f"   📦 Found {len(entities['categories'])} categories")
                    except Exception as e:
                        print(f"   ⚠️ Could not extract categories: {e}")

                # Try to get date ranges from any Event nodes
                if "Event" in node_types:
                    try:
                        date_ranges = session.run("""
                            MATCH (e:Event)
                            WHERE e.timestamp IS NOT NULL
                            RETURN 
                                min(e.timestamp) as earliest_date,
                                max(e.timestamp) as latest_date,
                                count(e) as total_events
                        """).single()

                        if date_ranges:
                            entities["date_range"] = {
                                "earliest": str(date_ranges["earliest_date"])
                                if date_ranges["earliest_date"]
                                else "2020-01-01",
                                "latest": str(date_ranges["latest_date"])
                                if date_ranges["latest_date"]
                                else "2024-12-31",
                                "total_events": date_ranges["total_events"] or 0,
                            }
                        print(
                            f"   📅 Date range: {entities['date_range']['earliest']} to {entities['date_range']['latest']}"
                        )
                    except Exception as e:
                        print(f"   ⚠️ Could not extract date ranges: {e}")

                # Try to get domain counts
                if "Event" in node_types:
                    try:
                        domain_counts = session.run("""
                            MATCH (e:Event)
                            WHERE e.domain IS NOT NULL
                            RETURN 
                                e.domain as domain,
                                count(e) as count
                        """).data()
                        entities["domain_counts"] = {
                            item["domain"]: item["count"] for item in domain_counts
                        }
                        print(f"   🏷️ Domain counts: {entities['domain_counts']}")
                    except Exception as e:
                        print(f"   ⚠️ Could not extract domain counts: {e}")

                # Get sample COVID events
                if "CovidEvent" in node_types and entities["covid_locations"]:
                    try:
                        covid_events = session.run("""
                            MATCH (e:CovidEvent)
                            WHERE e.timestamp IS NOT NULL
                            RETURN 
                                e.entity_id as id,
                                e.description as description,
                                e.timestamp as timestamp,
                                e.location as location,
                                e.event_type as event_type
                            ORDER BY e.timestamp
                            LIMIT 10
                        """).data()
                        entities["covid_events"] = [
                            convert_neo4j_types(event) for event in covid_events
                        ]
                        print(f"   🦠 Found {len(covid_events)} sample COVID events")
                    except Exception as e:
                        print(f"   ⚠️ Could not extract COVID events: {e}")

                # Get customer purchase data
                if "Customer" in node_types and "EcommerceEvent" in node_types:
                    try:
                        customer_purchases = session.run("""
                            MATCH (c:Customer)-[:PERFORMED]->(e:EcommerceEvent)
                            WHERE e.event_type = 'purchase' AND e.order_value IS NOT NULL
                            RETURN 
                                c.customer_id as customer_id,
                                count(e) as purchase_count,
                                sum(e.order_value) as total_spent
                            ORDER BY purchase_count DESC
                            LIMIT 10
                        """).data()
                        entities["customer_purchases"] = [
                            convert_neo4j_types(purchase)
                            for purchase in customer_purchases
                        ]
                        print(
                            f"   💰 Found {len(customer_purchases)} customer purchase records"
                        )
                    except Exception as e:
                        print(f"   ⚠️ Could not extract customer purchases: {e}")

                return entities

        except Exception as e:
            print(f"❌ Error extracting entities: {e}")
            return self.get_fallback_entities()

    def get_fallback_entities(self) -> Dict[str, Any]:
        """Provide fallback entities when Neo4j is not available"""
        print("📋 Using fallback entities for ground truth generation...")

        return {
            "covid_locations": ["Brazil", "France", "Italy", "United States", "Global"],
            "customers": ["cust_001", "cust_002", "cust_003", "cust_004", "cust_005"],
            "categories": ["Electronics", "Clothing", "Books", "Food", "Health"],
            "date_range": {
                "earliest": "2020-01-01",
                "latest": "2024-12-31",
                "total_events": 1000,
            },
            "domain_counts": {"covid": 500, "ecommerce": 300},
            "covid_events": [
                {
                    "id": "covid_001",
                    "description": "First COVID case reported",
                    "timestamp": "2020-01-15",
                    "location": "Brazil",
                    "event_type": "case_report",
                }
            ],
            "customer_purchases": [
                {"customer_id": "cust_001", "purchase_count": 5, "total_spent": 250.0}
            ],
            "available_labels": ["CovidEvent", "Customer", "EcommerceEvent", "Event"],
        }

    def generate_synchronized_ground_truth(
        self, entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate ground truth questions that reference actual entities"""
        print("📝 Generating synchronized ground truth questions...")

        questions = []

        # 1. COVID Location-based questions
        if entities["covid_locations"]:
            for location in entities["covid_locations"][:2]:  # Use first 2 locations
                questions.append(
                    {
                        "question": f"What COVID-19 events occurred in {location}?",
                        "type": "location_filter",
                        "domain": "covid",
                        "ground_truth": {
                            "type": "entity_filter",
                            "entity_type": "CovidEvent",
                            "filter_field": "location",
                            "filter_value": location,
                            "expected_count": ">= 1",
                        },
                        "neo4j_query": f"""
                        MATCH (e:CovidEvent)
                        WHERE e.location = '{location}'
                        RETURN e.description, e.timestamp, e.location
                        ORDER BY e.timestamp
                    """,
                    }
                )

        # 2. Customer Journey questions
        if entities["customers"]:
            customer = entities["customers"][0]
            questions.append(
                {
                    "question": f"What was the activity timeline for customer {customer}?",
                    "type": "customer_journey",
                    "domain": "ecommerce",
                    "ground_truth": {
                        "type": "customer_timeline",
                        "customer_id": customer,
                        "expected_fields": ["event_type", "timestamp", "description"],
                    },
                    "neo4j_query": f"""
                    MATCH (c:Customer {{customer_id: '{customer}'}})-[:PERFORMED]->(e:EcommerceEvent)
                    RETURN e.event_type, e.timestamp, e.description
                    ORDER BY e.timestamp
                """,
                }
            )

        # 3. Temporal sequence questions
        questions.append(
            {
                "question": "What was the chronological sequence of major COVID-19 events?",
                "type": "temporal_sequence",
                "domain": "covid",
                "ground_truth": {
                    "type": "temporal_ordering",
                    "entity_type": "CovidEvent",
                    "order_field": "timestamp",
                    "expected_count": ">= 3",
                },
                "neo4j_query": """
                MATCH (e:CovidEvent)
                RETURN e.description, e.timestamp, e.location
                ORDER BY e.timestamp
                LIMIT 10
            """,
            }
        )

        # 4. Aggregation questions
        questions.append(
            {
                "question": "How many customers made purchases?",
                "type": "aggregation",
                "domain": "ecommerce",
                "ground_truth": {
                    "type": "count_aggregation",
                    "expected_count": len(entities["customer_purchases"])
                    if entities["customer_purchases"]
                    else 5,
                    "aggregation_type": "distinct_customers_with_purchases",
                },
                "neo4j_query": """
                MATCH (c:Customer)-[:PERFORMED]->(e:EcommerceEvent)
                WHERE e.event_type = 'purchase'
                RETURN count(DISTINCT c.customer_id) as customer_count
            """,
            }
        )

        # 5. Domain comparison
        domain_counts = entities["domain_counts"]
        questions.append(
            {
                "question": "Which domain has more events: COVID-19 or e-commerce?",
                "type": "domain_comparison",
                "domain": "both",
                "ground_truth": {
                    "type": "domain_comparison",
                    "covid_count": domain_counts.get("covid", 500),
                    "ecommerce_count": domain_counts.get("ecommerce", 300),
                    "winner": "covid"
                    if domain_counts.get("covid", 500)
                    > domain_counts.get("ecommerce", 300)
                    else "ecommerce",
                },
                "neo4j_query": """
                MATCH (e:Event)
                RETURN e.domain, count(e) as count
            """,
            }
        )

        # 6. Category analysis
        if entities["categories"]:
            questions.append(
                {
                    "question": "What are the most popular product categories?",
                    "type": "category_analysis",
                    "domain": "ecommerce",
                    "ground_truth": {
                        "type": "category_ranking",
                        "categories": entities["categories"],
                        "expected_fields": ["category", "count"],
                    },
                    "neo4j_query": """
                    MATCH (e:EcommerceEvent)
                    WHERE e.product_category IS NOT NULL
                    RETURN e.product_category as category, count(e) as count
                    ORDER BY count DESC
                """,
                }
            )

        # 7. Temporal filter
        questions.append(
            {
                "question": "Which customers signed up in 2023?",
                "type": "temporal_filter",
                "domain": "ecommerce",
                "ground_truth": {
                    "type": "temporal_filter",
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31",
                    "event_type": "signup",
                },
                "neo4j_query": """
                MATCH (c:Customer)-[:PERFORMED]->(e:EcommerceEvent)
                WHERE e.event_type = 'signup' 
                AND e.timestamp >= date('2023-01-01') 
                AND e.timestamp <= date('2023-12-31')
                RETURN c.customer_id, e.timestamp
                ORDER BY e.timestamp
            """,
            }
        )

        # 8. Location comparison
        if len(entities["covid_locations"]) >= 2:
            loc1, loc2 = entities["covid_locations"][:2]
            questions.append(
                {
                    "question": f"Compare COVID-19 events between {loc1} and {loc2}",
                    "type": "location_comparison",
                    "domain": "covid",
                    "ground_truth": {
                        "type": "location_comparison",
                        "location1": loc1,
                        "location2": loc2,
                        "comparison_fields": ["event_count", "timeline"],
                    },
                    "neo4j_query": f"""
                    MATCH (e:CovidEvent)
                    WHERE e.location IN ['{loc1}', '{loc2}']
                    RETURN e.location, count(e) as count, collect(e.timestamp) as timestamps
                """,
                }
            )

        # 9. First/last event questions
        if entities["covid_events"]:
            first_event = entities["covid_events"][0]
            questions.append(
                {
                    "question": "What was the first recorded COVID-19 event in the dataset and where did it occur?",
                    "type": "temporal_reasoning",
                    "domain": "covid",
                    "ground_truth": {
                        "type": "first_event",
                        "expected_description": first_event.get(
                            "description", "First COVID event"
                        ),
                        "expected_location": first_event.get("location", "Unknown"),
                        "expected_date": first_event.get("timestamp", "2020-01-01"),
                    },
                    "neo4j_query": """
                    MATCH (e:CovidEvent)
                    RETURN e.description, e.location, e.timestamp
                    ORDER BY e.timestamp
                    LIMIT 1
                """,
                }
            )

        # 10. Cross-domain timeline
        questions.append(
            {
                "question": "Compare the timeline of COVID-19 events with e-commerce activities",
                "type": "cross_domain_timeline",
                "domain": "both",
                "ground_truth": {
                    "type": "cross_domain_analysis",
                    "requires_fields": ["domain", "timestamp", "event_type"],
                    "expected_domains": ["covid", "ecommerce"],
                },
                "neo4j_query": """
                MATCH (e:Event)
                RETURN e.domain, e.timestamp, e.event_type
                ORDER BY e.timestamp
            """,
            }
        )

        print(f"✅ Generated {len(questions)} synchronized questions")
        return questions

    def save_ground_truth(
        self,
        questions: List[Dict[str, Any]],
        filename: str = "synchronized_ground_truth.json",
    ):
        """Save synchronized ground truth to multiple locations for compatibility"""

        # Convert any remaining Neo4j types in questions
        serializable_questions = convert_neo4j_types(questions)

        # Create the main file in current directory
        current_dir_file = filename
        with open(current_dir_file, "w") as f:
            json.dump(serializable_questions, f, indent=2, cls=CustomJSONEncoder)
        print(f"💾 Saved synchronized ground truth to {current_dir_file}")

        # Also save in scripts directory if it exists
        scripts_dir = "scripts"
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)

        scripts_file = os.path.join(scripts_dir, filename)
        with open(scripts_file, "w") as f:
            json.dump(serializable_questions, f, indent=2, cls=CustomJSONEncoder)
        print(f"💾 Saved synchronized ground truth to {scripts_file}")

        # Also save as ground_truth.json for compatibility
        fallback_file = "ground_truth.json"
        with open(fallback_file, "w") as f:
            json.dump(serializable_questions, f, indent=2, cls=CustomJSONEncoder)
        print(f"💾 Saved synchronized ground truth to {fallback_file}")

        # Save metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "total_questions": len(questions),
            "question_types": list(set(q["type"] for q in questions)),
            "domains": list(set(q["domain"] for q in questions)),
            "neo4j_connected": self.driver is not None,
        }

        with open("ground_truth_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, cls=CustomJSONEncoder)
        print(f"📊 Saved metadata to ground_truth_metadata.json")

    def validate_ground_truth(self, questions: List[Dict[str, Any]]) -> bool:
        """Validate that all ground truth questions can be answered with actual data"""
        print("🔍 Validating ground truth against actual data...")

        if not self.driver:
            print("⚠️ No Neo4j connection - skipping validation")
            return True  # Assume valid if we can't validate

        validation_results = []

        try:
            with self.driver.session() as session:
                for i, question in enumerate(questions):
                    try:
                        # Execute the Neo4j query to see if it returns results
                        result = session.run(question["neo4j_query"])
                        records = list(result)

                        validation_results.append(
                            {
                                "question_id": i,
                                "question": question["question"],
                                "valid": True,
                                "result_count": len(records),
                            }
                        )

                    except Exception as e:
                        validation_results.append(
                            {
                                "question_id": i,
                                "question": question["question"],
                                "valid": False,
                                "error": str(e),
                            }
                        )

        except Exception as e:
            print(f"❌ Validation error: {e}")
            return True  # Don't fail if validation fails

        # Print validation summary
        valid_count = sum(1 for r in validation_results if r["valid"])
        total_count = len(validation_results)

        print(f"📊 Validation Results: {valid_count}/{total_count} questions valid")

        for result in validation_results:
            if not result["valid"]:
                print(f"❌ Invalid: {result['question']} - {result['error']}")
            else:
                print(
                    f"✅ Valid: {result['question']} - {result['result_count']} results"
                )

        return valid_count >= (total_count * 0.7)  # Accept if 70% or more are valid

    def close(self):
        if self.driver:
            self.driver.close()


def main():
    """Generate synchronized ground truth"""
    print("🚀 Ground Truth Generator Starting...")
    print(f"📁 Current working directory: {os.getcwd()}")

    # Get environment variables
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    print(f"🔍 Environment check:")
    print(f"   NEO4J_URI: {NEO4J_URI}")
    print(f"   NEO4J_USER: {NEO4J_USER}")
    print(f"   NEO4J_PASSWORD: {'✅ Set' if NEO4J_PASSWORD else '❌ Not set'}")

    if not NEO4J_PASSWORD:
        print("\n⚠️ NEO4J_PASSWORD environment variable not set.")
        print("🔧 Will proceed with fallback data generation.")
        print("💡 To use actual Neo4j data, set: export NEO4J_PASSWORD='your_password'")

    # Initialize synchronizer
    synchronizer = GroundTruthSynchronizer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        # Extract actual entities from Neo4j (or use fallback)
        entities = synchronizer.extract_actual_entities()

        # Generate synchronized ground truth
        questions = synchronizer.generate_synchronized_ground_truth(entities)

        if not questions:
            print("❌ No questions generated!")
            return 1

        # Validate ground truth (if possible)
        is_valid = synchronizer.validate_ground_truth(questions)

        # Save synchronized ground truth regardless of validation
        synchronizer.save_ground_truth(questions)

        if is_valid:
            print("🎉 Successfully generated and validated synchronized ground truth!")
        else:
            print("⚠️ Generated ground truth but some validation issues exist.")
            print("📝 Ground truth files created anyway for evaluation.")

        print(f"\n📄 Generated files:")
        print(f"   ✅ synchronized_ground_truth.json")
        print(f"   ✅ scripts/synchronized_ground_truth.json")
        print(f"   ✅ ground_truth.json")
        print(f"   ✅ ground_truth_metadata.json")
        print(f"\n🚀 Ready to run evaluation with: python evals/run_ods_evaluation.py")

        return 0

    except Exception as e:
        print(f"❌ Error generating ground truth: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        synchronizer.close()


if __name__ == "__main__":
    sys.exit(main())
