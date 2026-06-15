from abc import ABC, abstractmethod

from app.expense_tracker.config import get_settings


class EmailProvider(ABC):
    @abstractmethod
    async def send(self, to_email: str, subject: str, body: str) -> None:
        raise NotImplementedError


class NoopEmailProvider(EmailProvider):
    async def send(self, to_email: str, subject: str, body: str) -> None:
        return None


class EmailService:
    def __init__(self, provider: EmailProvider | None = None):
        self.provider = provider or self._provider_from_settings()
        self.settings = get_settings()

    async def send_account_invitation(self, to_email: str, account_name: str) -> None:
        await self.provider.send(to_email, f"Invitation to {account_name}", f"You were invited to {account_name}.")

    async def send_password_reset(self, to_email: str, token: str) -> None:
        reset_url = f"{self.settings.app_base_url}/reset-password?token={token}"
        await self.provider.send(to_email, "Reset your password", f"Use this secure link to reset your password: {reset_url}")

    async def send_monthly_report(self, to_email: str, body: str) -> None:
        await self.provider.send(to_email, "Your monthly expense report", body)

    def _provider_from_settings(self) -> EmailProvider:
        return NoopEmailProvider()

