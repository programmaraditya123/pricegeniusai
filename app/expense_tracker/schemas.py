from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


AccountType = Literal["PERSONAL", "FAMILY", "COUPLE", "FRIENDS_GROUP", "SHARED"]
AccountRole = Literal["OWNER", "ADMIN", "MEMBER"]
InvitationStatus = Literal["PENDING", "ACCEPTED", "REJECTED"]
NotificationType = Literal["BUDGET_ALERT", "INVITATION", "EXPENSE_ADDED", "MONTHLY_REPORT", "SYSTEM"]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    avatar_url: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    avatar_url: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryRead(BaseModel):
    id: int
    name: str
    is_default: bool

    model_config = ConfigDict(from_attributes=True)


class ExpenseBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    merchant: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category_id: int
    expense_date: date
    payment_method: str | None = None
    account_id: int | None = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    merchant: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category_id: int | None = None
    expense_date: date | None = None
    payment_method: str | None = None
    account_id: int | None = None


class ExpenseRead(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryRead

    model_config = ConfigDict(from_attributes=True)


class ExpenseSyncItem(ExpenseBase):
    id: int | None = None
    updated_at: datetime | None = None
    deleted: bool = False


class PaginatedExpenses(BaseModel):
    items: list[ExpenseRead]
    total: int
    page: int
    size: int


class BudgetBase(BaseModel):
    category_id: int
    monthly_limit: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    category_id: int | None = None
    monthly_limit: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    month: int | None = Field(default=None, ge=1, le=12)
    year: int | None = Field(default=None, ge=2000, le=2100)


class BudgetRead(BudgetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryRead

    model_config = ConfigDict(from_attributes=True)


class ExpenseAccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    account_type: AccountType


class ExpenseAccountCreate(ExpenseAccountBase):
    pass


class ExpenseAccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    account_type: AccountType | None = None


class ExpenseAccountRead(ExpenseAccountBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseAccountSyncItem(ExpenseAccountBase):
    id: int | None = None
    updated_at: datetime | None = None
    deleted: bool = False


class AccountMemberRead(BaseModel):
    id: int
    account_id: int
    user_id: int
    role: AccountRole
    joined_at: datetime
    user: UserRead

    model_config = ConfigDict(from_attributes=True)


class InviteMemberRequest(BaseModel):
    email: EmailStr


class InvitationRead(BaseModel):
    id: int
    account_id: int
    email: EmailStr
    invited_by: int
    status: InvitationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateMemberRoleRequest(BaseModel):
    role: Literal["ADMIN", "MEMBER"]


class MonthlySummary(BaseModel):
    month: int
    year: int
    total_spending: Decimal
    transaction_count: int
    average_expense: Decimal


class CategoryBreakdownItem(BaseModel):
    category: str
    total: Decimal
    transaction_count: int


class TopMerchantItem(BaseModel):
    merchant: str
    total: Decimal
    transaction_count: int


class SpendingTrendItem(BaseModel):
    period: date
    total: Decimal


class MemberContributionItem(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str | None
    total: Decimal
    transaction_count: int


class ParseExpenseRequest(BaseModel):
    text: str = Field(min_length=1)


class ParsedExpense(BaseModel):
    amount: Decimal
    merchant: str
    category: str


class MonthlyInsightRead(BaseModel):
    id: int
    user_id: int
    month: int
    year: int
    total_spending: Decimal
    top_category: str | None
    top_merchant: str | None
    spending_growth: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncPushRequest(BaseModel):
    expenses: list[ExpenseSyncItem] = Field(default_factory=list)
    accounts: list[ExpenseAccountSyncItem] = Field(default_factory=list)


class SyncConflict(BaseModel):
    entity: str
    local_id: int | None
    server_id: int
    reason: str
    server_updated_at: datetime


class SyncPushResponse(BaseModel):
    accepted: dict[str, list[int]]
    conflicts: list[SyncConflict]


class SyncPullResponse(BaseModel):
    expenses: list[ExpenseRead]
    accounts: list[ExpenseAccountRead]
    server_time: datetime


class NotificationRead(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: NotificationType
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSettingsBase(BaseModel):
    currency: str = Field(default="INR", max_length=10)
    timezone: str = Field(default="Asia/Kolkata", max_length=100)
    language: str = Field(default="en", max_length=20)
    notification_enabled: bool = True
    dark_mode: bool = False


class UserSettingsUpdate(BaseModel):
    currency: str | None = Field(default=None, max_length=10)
    timezone: str | None = Field(default=None, max_length=100)
    language: str | None = Field(default=None, max_length=20)
    notification_enabled: bool | None = None
    dark_mode: bool | None = None


class UserSettingsRead(UserSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetStatusItem(BaseModel):
    budget_id: int
    category: str
    monthly_limit: Decimal
    spent: Decimal
    percent_used: Decimal
    status: str


class DashboardResponse(BaseModel):
    monthly_spending: Decimal
    monthly_budget: Decimal
    remaining_budget: Decimal
    top_category: CategoryBreakdownItem | None
    top_merchant: TopMerchantItem | None
    recent_expenses: list[ExpenseRead]
    budget_status: list[BudgetStatusItem]


class AuditLogRead(BaseModel):
    id: int
    user_id: int | None
    action: str
    resource: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminMetricsResponse(BaseModel):
    users_count: int
    expenses_count: int
    active_accounts: int
    user_growth_30d: int
    expense_growth_30d: int
