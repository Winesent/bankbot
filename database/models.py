from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    user_id: int
    username: str | None
    balance: float
    created_at: datetime

@dataclass
class Transaction:
    id: int
    from_user_id: int
    to_user_id: int
    amount: float
    created_at: datetime