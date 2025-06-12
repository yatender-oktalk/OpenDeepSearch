"""
Evaluate temporal reasoning accuracy for TKG queries
"""

import re
from typing import Dict, List, Set
from datetime import datetime


class TemporalAccuracyEvaluator:
    def __init__(self):
        self.temporal_patterns = {
            "date": r"\d{4}-\d{2}-\d{2}",
            "month_year": r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
            "quarter": r"Q[1-4]\s+\d{4}",
            "relative_time": r"(before|after|during|between|within)\s+\d+\s+(days?|months?|years?)",
            "event_types": r"(signup|login|upgrade|purchase|support|cancellation)",
        }

    def evaluate_response(
        self, query: str, response: str, expected_facts: Dict
    ) -> Dict:
        """Evaluate temporal accuracy of a response"""
        scores = {}

        # Extract temporal entities from response
        found_entities = self._extract_temporal_entities(response)

        # Check for expected events
        if "events" in expected_facts:
            event_score = self._score_events(response, expected_facts["events"])
            scores["event_accuracy"] = event_score

        # Check temporal ordering
        if "temporal_order" in expected_facts:
            order_score = self._check_temporal_ordering(
                response, expected_facts["temporal_order"]
            )
            scores["temporal_ordering"] = order_score

        # Check temporal relationships
        if "temporal_relations" in expected_facts:
            relation_score = self._check_temporal_relations(
                response, expected_facts["temporal_relations"]
            )
            scores["temporal_relations"] = relation_score

        # Overall temporal coverage
        scores["temporal_entity_count"] = len(found_entities)

        return scores

    def _extract_temporal_entities(self, text: str) -> Set[str]:
        """Extract all temporal entities from text"""
        entities = set()

        for pattern_name, pattern in self.temporal_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.update(matches)

        return entities

    def _score_events(self, response: str, expected_events: List[str]) -> float:
        """Score how many expected events are mentioned"""
        if not expected_events:
            return 1.0

        found_count = sum(
            1 for event in expected_events if event.lower() in response.lower()
        )

        return found_count / len(expected_events)

    def _check_temporal_ordering(
        self, response: str, expected_order: List[str]
    ) -> float:
        """Check if events appear in correct temporal order"""
        positions = []

        for event in expected_order:
            pos = response.lower().find(event.lower())
            if pos != -1:
                positions.append(pos)
            else:
                return 0.0  # Missing event breaks ordering

        # Check if positions are in ascending order
        is_ordered = all(
            positions[i] <= positions[i + 1] for i in range(len(positions) - 1)
        )

        return 1.0 if is_ordered else 0.0

    def _check_temporal_relations(
        self, response: str, expected_relations: List[Dict]
    ) -> float:
        """Check if temporal relationships are correctly expressed"""
        if not expected_relations:
            return 1.0

        correct_relations = 0

        for relation in expected_relations:
            # Check if the relationship is expressed in the response
            # e.g., {"event1": "signup", "relation": "before", "event2": "upgrade"}
            pattern = (
                f"{relation['event1']}.*{relation['relation']}.*{relation['event2']}"
            )
            if re.search(pattern, response, re.IGNORECASE):
                correct_relations += 1

        return correct_relations / len(expected_relations)


# Example usage function
def evaluate_temporal_response(query: str, response: str) -> Dict:
    """Quick function to evaluate temporal accuracy"""
    evaluator = TemporalAccuracyEvaluator()

    # Define expected facts based on query type
    expected_facts = {}

    if "CUST001" in query:
        expected_facts = {
            "events": ["signup", "upgrade", "purchase"],
            "temporal_order": ["signup", "upgrade", "purchase"],
            "temporal_relations": [
                {"event1": "signup", "relation": "before", "event2": "upgrade"}
            ],
        }
    elif "CUST003" in query and "cancellation" in query:
        expected_facts = {
            "events": ["signup", "support", "cancellation"],
            "temporal_order": ["signup", "support", "cancellation"],
        }

    return evaluator.evaluate_response(query, response, expected_facts)
