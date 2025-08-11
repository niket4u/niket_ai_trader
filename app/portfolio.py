
from dataclasses import dataclass, field
from typing import Dict
from .config import settings

@dataclass
class Position:
    qty: float
    cost_basis: float
    ticker: str

@dataclass
class Portfolio:
    cash_spent: float = 0.0
    positions: Dict[str, Position] = field(default_factory=dict)
    realized_pnl_month: float = 0.0
    realized_pnl_day: float = 0.0

    def can_invest(self, amount: float) -> bool:
        return (self.cash_spent + amount) <= settings.investment_cap

    def apply_buy(self, ticker: str, qty: float, price: float):
        cost = qty * price
        self.cash_spent += cost
        p = self.positions.get(ticker)
        if p:
            p.qty += qty
            p.cost_basis += cost
        else:
            self.positions[ticker] = Position(qty=qty, cost_basis=cost, ticker=ticker)

    def apply_sell(self, ticker: str, qty: float, price: float):
        if ticker not in self.positions:
            return
        p = self.positions[ticker]
        qty = min(qty, p.qty)
        avg_price = p.cost_basis / p.qty if p.qty else 0.0
        realized = (price - avg_price) * qty
        self.realized_pnl_day += realized
        self.realized_pnl_month += realized
        p.qty -= qty
        p.cost_basis -= avg_price * qty
        if p.qty <= 1e-6:
            del self.positions[ticker]

    def breach_daily_loss(self) -> bool:
        return self.realized_pnl_day <= -abs(settings.daily_loss_limit)

    def breach_monthly_loss(self) -> bool:
        return self.realized_pnl_month <= -abs(settings.monthly_loss_limit)

    def reached_monthly_gain(self) -> bool:
        return self.realized_pnl_month >= settings.monthly_gain_target
