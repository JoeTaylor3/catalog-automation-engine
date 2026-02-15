"""
Validators package for catalog-automation-engine.

Provides a modular validation framework for product catalog data.
Each validator inherits from BaseValidator and returns structured error objects.
"""

from .base_validator import BaseValidator
from .price_validator import PriceValidator
from .sku_validator import SKUValidator
from .inventory_validator import InventoryValidator

__all__ = [
    "BaseValidator",
    "PriceValidator",
    "SKUValidator",
    "InventoryValidator",
]
