class ListingAgent:

    def generate_listing(self, folder):

        name = folder.name.replace("_", " ").title()

        return {
            "title": name,
            "description": f"Great condition {name}.",
            "price": 25,
            "category": "dress",
            "tags": ["fashion", "resale"]
        }
