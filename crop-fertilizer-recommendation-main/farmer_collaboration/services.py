"""
Service layer for Farmer Collaboration & Mandi Marketplace (Farmer Connect).
Implements global search, rule-based AI match engine, notification dispatch, and trust badges.
"""

from typing import List, Dict, Any
from .seed import DEMO_FARMERS, DEMO_MANDIS, DEMO_LISTINGS, DEMO_REQUIREMENTS, DEMO_POSTS, DEMO_ANNOUNCEMENTS

class CollaborationService:

    @staticmethod
    def global_search(query: str) -> Dict[str, List[Any]]:
        """
        Global search engine across Farmers, Marketplace Products, Requirements, Posts, Mandis, and Announcements.
        """
        if not query:
            return {"farmers": [], "listings": [], "requirements": [], "posts": [], "mandis": [], "announcements": []}
            
        q = query.strip().lower()
        
        farmers = [f for f in DEMO_FARMERS if q in f["name"].lower() or q in f["crops"].lower() or q in f["district"].lower()]
        listings = [l for l in DEMO_LISTINGS if q in l["title"].lower() or q in l["category"].lower() or q in l["location"].lower()]
        requirements = [r for r in DEMO_REQUIREMENTS if q in r["title"].lower() or q in r["category"].lower() or q in r["location"].lower()]
        posts = [p for p in DEMO_POSTS if q in p["title"].lower() or q in p["content"].lower() or q in p["category"].lower()]
        mandis = [m for m in DEMO_MANDIS if q in m["mandi_name"].lower() or q in m["district"].lower() or q in m["crops"].lower()]
        announcements = [a for a in DEMO_ANNOUNCEMENTS if q in a["title"].lower() or q in a["content"].lower() or q in a["crop_type"].lower()]
        
        return {
            "query": query,
            "farmers": farmers,
            "listings": listings,
            "requirements": requirements,
            "posts": posts,
            "mandis": mandis,
            "announcements": announcements,
            "total_results": len(farmers) + len(listings) + len(requirements) + len(posts) + len(mandis) + len(announcements)
        }

    @staticmethod
    def match_requirement_with_sellers(requirement: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rule-Based AI Recommendation & Matching Engine.
        Scoring Algorithm:
        - Category match: +40 points
        - Same District match: +30 points, Same State: +10 points
        - Sufficient Quantity: +15 points
        - High Rating (>= 4.8): +15 points
        """
        req_category = str(requirement.get("category", "")).lower()
        req_district = str(requirement.get("location", "")).lower()
        req_qty = float(requirement.get("quantity", 0))

        matches = []
        for item in DEMO_LISTINGS:
            score = 0
            # 1. Category match
            if req_category in item["category"].lower() or item["category"].lower() in req_category:
                score += 40
            # 2. Location Proximity
            if req_district and any(d in item["location"].lower() for d in req_district.split(',')):
                score += 30
            elif "odisha" in item["location"].lower():
                score += 10
            # 3. Quantity sufficiency
            if item.get("quantity", 0) >= req_qty:
                score += 15
            # 4. Seller Rating
            if item.get("rating", 0) >= 4.8:
                score += 15

            if score >= 40:
                match_item = dict(item)
                match_item["match_score"] = score
                matches.append(match_item)

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches
