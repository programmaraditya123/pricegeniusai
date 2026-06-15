class SmartCategorizationService:
    merchant_rules = {
        "dominos": "Food",
        "pizza hut": "Food",
        "swiggy": "Food",
        "zomato": "Food",
        "uber": "Travel",
        "ola": "Travel",
        "irctc": "Travel",
        "amazon": "Shopping",
        "flipkart": "Shopping",
        "vishal mega mart": "Shopping",
        "netflix": "Entertainment",
        "spotify": "Entertainment",
        "apollo": "Health",
    }

    def categorize(self, merchant: str) -> str:
        merchant_lower = merchant.lower()
        for keyword, category in self.merchant_rules.items():
            if keyword in merchant_lower:
                return category
        return "Shopping"

