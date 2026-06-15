from fastapi import APIRouter

from app.expense_tracker.routes import accounts, ai, auth, budgets, categories, expenses, reports, sync


router = APIRouter(prefix="/expense-tracker")
router.include_router(auth.router)
router.include_router(accounts.router)
router.include_router(categories.router)
router.include_router(expenses.router)
router.include_router(budgets.router)
router.include_router(reports.router)
router.include_router(ai.router)
router.include_router(sync.router)
