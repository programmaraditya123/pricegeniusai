from fastapi import APIRouter, Depends

from app.expense_tracker.deps import get_current_user
from app.expense_tracker.models import User
from app.expense_tracker.schemas import ParseExpenseRequest, ParsedExpense
from app.expense_tracker.services.ai import ExpenseParsingService


router = APIRouter(prefix="/ai", tags=["expense ai"])


@router.post("/parse-expense", response_model=ParsedExpense)
async def parse_expense(data: ParseExpenseRequest, _: User = Depends(get_current_user)):
    return await ExpenseParsingService().parse(data.text)

