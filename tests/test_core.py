import unittest

from tastetrail.core import build_plan, validate_request


class FakeQloo:
    def search_entity(self, query, entity_type="urn:entity:place", take=12):
        return {"results": [{"entity_id": f"urn:{query}", "name": query.title()}]}

    def insights(self, interests, location_query, entity_type="urn:entity:place", take=12):
        return {"results": [{"entity_id": "urn:place:1", "name": "Example Place", "affinity": 0.91}]}


class CoreTests(unittest.TestCase):
    def test_validation_requires_location_and_interest(self):
        with self.assertRaises(ValueError):
            validate_request({"interests": ["food"]})
        with self.assertRaises(ValueError):
            validate_request({"location": "Jaipur", "interests": []})

    def test_plan_keeps_provenance_and_constraints(self):
        result = build_plan(
            {"location": "Jaipur", "interests": ["heritage"], "constraints": ["walkable"]},
            FakeQloo(),
        )
        self.assertEqual(result["location"], "Jaipur")
        self.assertEqual(result["constraints"], ["walkable"])
        self.assertEqual(result["recommendations"][0]["source"], "Qloo Insights API")


if __name__ == "__main__":
    unittest.main()

