"""Execution layer: abstract broker API for orders and positions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List


class BrokerBase(ABC):
    """Abstract broker client interface."""

    @abstractmethod
    def submit_order(self, symbol: str, side: str, quantity: int, price: float) -> dict[str, Any]:
        """Submit an order and return an execution summary."""

    @abstractmethod
    def get_positions(self) -> List[dict]:
        """Return broker-side positions."""
