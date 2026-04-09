"""Defines trading signal contracts and concrete strategy implementations."""

from algo_bot.strategies.base import StrategyBase
from algo_bot.strategies.decision import Decision
from algo_bot.strategies.simple_ma import SimpleMAStrategy

__all__ = ["Decision", "StrategyBase", "SimpleMAStrategy"]
