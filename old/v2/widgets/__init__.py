"""Widget modules for the Monzo app v2."""

from .base import ReactiveWidget
from .base import StateAwareWidget
from .dashboard import *
from .reactive_label import ReactiveLabel
from .reactive_label import StateLabel

__all__ = [
    "ReactiveLabel",
    "ReactiveWidget",
    "StateAwareWidget",
    "StateLabel",
]
