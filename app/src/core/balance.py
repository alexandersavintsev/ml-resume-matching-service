from dataclasses import dataclass


@dataclass
class Balance:
    credits: int = 0

    def can_spend(self, amount: int) -> bool:
        return self.credits >= amount

    def spend(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if not self.can_spend(amount):
            raise ValueError("Insufficient balance")
        self.credits -= amount

    def top_up(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.credits += amount
