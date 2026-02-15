"""
Validator for SKU fields.
Ensures SKU matches pattern and detects duplicates (pattern configurable in config.py).
"""

import re
from collections import Counter
from .base_validator import BaseValidator

try:
    from config import SKU_PATTERN
except ImportError:
    # Fallback defaults if config cannot be imported
    SKU_PATTERN = r"^SKU-\d{5}$"


class SKUValidator(BaseValidator):
    """Validates SKU format and detects duplicates.
    
    SKU pattern is configured in config.py:
    - SKU_PATTERN: Regex pattern for valid SKU format
    """

    def __init__(self, sku_pattern=None):
        """Initialize validator with optional custom pattern.
        
        Args:
            sku_pattern: Override SKU_PATTERN from config
        """
        self.sku_pattern = sku_pattern if sku_pattern is not None else SKU_PATTERN

    def validate(self, dataframe):
        """Check SKU format and detect duplicates.
        
        Args:
            dataframe: pandas DataFrame with 'sku' column
            
        Returns:
            list: List of error dicts for invalid or duplicate SKUs
        """
        errors = []
        sku_column = dataframe["sku"].tolist()
        sku_counts = Counter(sku_column)

        # Track which SKUs we've already reported as duplicates
        reported_duplicates = set()

        for _, row in dataframe.iterrows():
            sku = row["sku"]

            # Check format
            if not re.match(self.sku_pattern, str(sku)):
                errors.append({
                    "sku": sku,
                    "issue_type": "invalid_sku_format",
                    "issue_description": f"SKU '{sku}' does not match pattern {self.sku_pattern}"
                })

            # Check duplicates
            if sku_counts[sku] > 1 and sku not in reported_duplicates:
                errors.append({
                    "sku": sku,
                    "issue_type": "duplicate_sku",
                    "issue_description": f"SKU '{sku}' appears {sku_counts[sku]} times in catalog"
                })
                reported_duplicates.add(sku)

        return errors

        return errors
