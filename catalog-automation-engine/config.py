"""
Configuration for catalog-automation-engine.
Keep environment-specific configuration out of source control and load from env vars in production.
"""

from pathlib import Path

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "sample_catalog.csv"
DB_URI = "sqlite:///catalog.db"  # placeholder; override in production

# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================
# These values control validation rules across all validators.
# Adjust these settings to change validation behavior without modifying validator code.

# Price Validation
MIN_PRICE = 0.01  # Minimum acceptable price (must be > this value)
MAX_PRICE = 9999.99  # Maximum acceptable price (must be < this value)

# Inventory Validation
MIN_INVENTORY = 0  # Minimum acceptable inventory (must be >= this value)
LOW_STOCK_THRESHOLD = 5  # Inventory below this value triggers a warning

# SKU Validation
SKU_PATTERN = r"^SKU-\d{5}$"  # Regex pattern for valid SKU format

# ============================================================================
# REPORTING SETTINGS
# ============================================================================
REPORT_OUTPUT_DIR = ROOT / "output"
VALIDATION_REPORT_FILENAME = "validation_report.csv"

# ============================================================================
# DATABASE SETTINGS
# ============================================================================
DB_TABLE_NAME = "products"
