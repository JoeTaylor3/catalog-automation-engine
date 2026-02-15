"""
Validator for product price values.
Ensures price is > MIN_PRICE and < MAX_PRICE (configurable in config.py).
"""

from .base_validator import BaseValidator

try:
    from config import MIN_PRICE, MAX_PRICE
except ImportError:
    # Fallback defaults if config cannot be imported
    MIN_PRICE = 0.01
    MAX_PRICE = 9999.99


class PriceValidator(BaseValidator):
    """Validates product prices within acceptable business range.
    
    Price thresholds are configured in config.py:
    - MIN_PRICE: Minimum acceptable price
    - MAX_PRICE: Maximum acceptable price
    """

    def __init__(self, min_price=None, max_price=None):
        """Initialize validator with optional custom thresholds.
        
        Args:
            min_price: Override MIN_PRICE from config
            max_price: Override MAX_PRICE from config
        """
        self.min_price = min_price if min_price is not None else MIN_PRICE
        self.max_price = max_price if max_price is not None else MAX_PRICE

    def validate(self, dataframe):
        """Check all prices in dataframe are within valid range.
        
        Args:
            dataframe: pandas DataFrame with 'sku' and 'price' columns
            
        Returns:
            list: List of error dicts for invalid prices
        """
        errors = []
        
        for _, row in dataframe.iterrows():
            sku = row["sku"]
            price = row["price"]
            
            try:
                price_value = float(price)
            except (ValueError, TypeError):
                errors.append({
                    "sku": sku,
                    "issue_type": "invalid_price_format",
                    "issue_description": f"Price '{price}' is not a valid number"
                })
                continue
            
            if price_value <= self.min_price:
                errors.append({
                    "sku": sku,
                    "issue_type": "price_too_low",
                    "issue_description": f"Price {price_value} must be > {self.min_price}"
                })
            elif price_value >= self.max_price:
                errors.append({
                    "sku": sku,
                    "issue_type": "price_too_high",
                    "issue_description": f"Price {price_value} must be < {self.max_price}"
                })
        
        return errors
