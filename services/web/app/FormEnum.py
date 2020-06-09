"""
    This is a helper class for Enumerated Types and wtforms.

    This needs proper documentation, but is not a priority right now.
"""

from enum import Enum


class FormEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice.name, str(choice)) for choice in cls]

    def __str__(self):
        return str(self.value)
