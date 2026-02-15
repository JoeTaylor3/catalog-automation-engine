"""
Validator for inventory fields.
Ensures inventory is non-negative and flags low stock (configurable in config.py).
"""

from .base_validator import BaseValidator

try:
    from config import MIN_INVENTORY, LOW_STOCK_THRESHOLD
except ImportError:
    # Fallback defaults if config cannot be imported
    MIN_INVENTORY = 0
    LOW_STOCK_THRESHOLD = 5


class InventoryValidator(BaseValidator):
    """Validates inventory levels.
    
    Inventory thresholds are configured in config.py:
    - MIN_INVENTORY: Minimum acceptable inventory level
    - LOW_STOCK_THRESHOLD: Inventory below this value triggers a warning
    """

    def __init__(self, min_inventory=None, low_stock_threshold=None):
        """Initialize validator with optional custom thresholds.
        
        Args:
            min_inventory: Override MIN_INVENTORY from config
            low_stock_threshold: Override LOW_STOCK_THRESHOLD from config
        """
        self.min_inventory = min_inventory if min_inventory is not None else MIN_INVENTORY
        self.low_stock_threshold = low_stock_threshold if low_stock_threshold is not None else LOW_STOCK_THRESHOLD

    def validate(self, dataframe):
        """Check all inventory values in dataframe.
        
        Args:
            dataframe: pandas DataFrame with 'sku' and 'inventory_count' columns
            
        Returns:
            list: List of error dicts for invalid or low inventory
        """
        errors = []

        for _, row in dataframe.iterrows():
            sku = row["sku"]
            inventory = row["inventory_count"]

            try:
                inventory_value = int(inventory)
            except (ValueError, TypeError):
                errors.append({
                    "sku": sku,
                    "issue_type": "invalid_inventory_format",
                    "issue_description": f"Inventory '{inventory}' is not a valid integer"
                })
                continue

            if inventory_value < self.min_inventory:
                errors.append({
                    "sku": sku,
                    "issue_type": "negative_inventory",
                    "issue_description": f"Inventory {inventory_value} cannot be negative"
                })
            elif inventory_value < self.low_stock_threshold:
                errors.append({
                    "sku": sku,
                    "issue_type": "low_stock_warning",
                    "issue_description": f"Inventory {inventory_value} is below threshold of {self.low_stock_threshold}"
                })

        return errors
