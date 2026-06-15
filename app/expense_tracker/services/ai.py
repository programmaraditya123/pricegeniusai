import re
from abc import ABC, abstractmethod
from decimal import Decimal

from fastapi import HTTPException, status

from app.expense_tracker.schemas import ParsedExpense
from app.expense_tracker.services.categorization import SmartCategorizationService


class ExpenseAIProvider(ABC):
    @abstractmethod
    async def parse_expense(self, text: str) -> ParsedExpense:
        raise NotImplementedError


class RegexExpenseAIProvider(ExpenseAIProvider):
    amount_patterns = [
        re.compile(r"(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE),
        re.compile(r"(?:kharcha|spent|paid|total)\s+(?:is|of|was)?\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE),
    ]
    merchant_pattern = re.compile(
        r"(?:at|from|to)\s+([A-Za-z][A-Za-z0-9 '&.-]+?)(?:\s+(?:total|kharcha|spent|paid|for|is|was)|$)",
        re.IGNORECASE,
    )

    def __init__(self):
        self.categorizer = SmartCategorizationService()

    async def parse_expense(self, text: str) -> ParsedExpense:
        amount = self._parse_amount(text)
        merchant = self._parse_merchant(text)
        category = self.categorizer.categorize(merchant)
        return ParsedExpense(amount=amount, merchant=merchant, category=category)

    def _parse_amount(self, text: str) -> Decimal:
        for pattern in self.amount_patterns:
            match = pattern.search(text)
            if match:
                return Decimal(match.group(1))
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not parse amount")

    def _parse_merchant(self, text: str) -> str:
        match = self.merchant_pattern.search(text)
        if not match:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not parse merchant")
        return " ".join(match.group(1).strip(" .").split()).title()


class ExpenseParsingService:
    def __init__(self, provider: ExpenseAIProvider | None = None):
        self.provider = provider or RegexExpenseAIProvider()

    async def parse(self, text: str) -> ParsedExpense:
        return await self.provider.parse_expense(text)

