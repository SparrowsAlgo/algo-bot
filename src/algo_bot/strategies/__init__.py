"""Defines trading signal contracts and concrete strategy implementations."""

from algo_bot.strategies.base import StrategyBase
from algo_bot.strategies.simple_ma import SimpleMAStrategy

__all__ = ["StrategyBase", "SimpleMAStrategy"]
