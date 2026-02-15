# Catalog Automation Engine

**Enterprise-Grade Data Validation and Analytics Platform for Product Catalog Management**

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Architecture Overview](#architecture-overview)
3. [Validation Framework Design](#validation-framework-design)
4. [SQL Analytics Layer](#sql-analytics-layer)
5. [Sample Metrics Output](#sample-metrics-output)
6. [Installation & Setup](#installation--setup)
7. [Running the Pipeline](#running-the-pipeline)
8. [Configuration](#configuration)
9. [Future Enhancements](#future-enhancements)
10. [Project Structure](#project-structure)

---

## Problem Statement

**Challenge:**
Modern e-commerce and retail operations rely on accurate, high-quality product catalog data. However, catalogs often contain:
- **Data Quality Issues**: Duplicate SKUs, negative prices, invalid formats
- **Inventory Discrepancies**: Negative stock counts, missing critical fields
- **Lack of Visibility**: No centralized view of data health metrics
- **Manual Processes**: Labor-intensive validation and reporting workflows

**Solution:**
The **Catalog Automation Engine** provides an automated, scalable pipeline for:
- **Real-time validation** of catalog records against business rules
- **Structured error reporting** with actionable insights
- **Advanced analytics** on data quality and inventory patterns
- **Configuration-driven** rules enabling business teams to adjust thresholds without code changes

---

## Architecture Overview

The platform implements a **4-stage modular pipeline**:

```
┌─────────────────┐
│ DATA INGESTION  │  Load CSV → Pandas DataFrame
└────────┬────────┘
         │
┌────────▼────────┐
│   VALIDATION    │  Run validators → Aggregate errors
└────────┬────────┘
         │
┌────────▼────────┐
│   REPORTING     │  Generate CSV reports + metrics dashboard
└────────┬────────┘
         │
┌────────▼────────┐
│  DB ANALYTICS   │  SQLite queries → Category/inventory analysis
└─────────────────┘
```

### Layer 1: Data Ingestion
- **Input**: CSV files (`data/sample_catalog.csv`)
- **Processing**: Load into Pandas DataFrame with schema detection
- **Output**: Structured in-memory dataframe

### Layer 2: Validation
- **Modular validators** inherit from `BaseValidator` abstract class
- **Validators** process dataframe and return structured error dictionaries
- **Error Format**: `{sku, issue_type, issue_description}`
- **Supported Validators**:
  - `PriceValidator`: Price range validation (configurable min/max)
  - `SKUValidator`: Format validation + duplicate detection
  - `InventoryValidator`: Stock level checks + low-inventory warnings

### Layer 3: Reporting
- **CSV Report Generation**: Write all validation errors to `output/validation_report.csv`
- **Metrics Calculation**: Compute integrity scores, top issue types
- **CLI Dashboard**: Print operational summary with visual indicators

### Layer 4: Database Analytics
- **SQLite Integration**: Load validated data into persistent store
- **Dynamic Schema**: Auto-generate table from CSV structure
- **Analytics Queries**:
  - Duplicate SKU detection with occurrence counts
  - Category-based record aggregation
  - High-value product identification
  - Inventory analysis by category

---

## Validation Framework Design

### Validator Architecture

All validators extend the **`BaseValidator`** abstract class:

```python
from validators.base_validator import BaseValidator

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, dataframe):
        """Return: list of {sku, issue_type, issue_description} dicts"""
        pass
```

### Configuration-Driven Design

**Key Benefit**: Adjust validation rules via `config.py` without modifying validator code.

**config.py Settings:**
```python
MIN_PRICE = 0.01              # Minimum product price
MAX_PRICE = 9999.99           # Maximum product price
MIN_INVENTORY = 0             # Minimum stock level
LOW_STOCK_THRESHOLD = 5       # Items below this trigger warning
SKU_PATTERN = r"^SKU-\d{5}$"  # Valid SKU format
```

**Runtime Overrides:**
```python
# Use defaults from config
validator = PriceValidator()

# Custom thresholds for testing
strict = PriceValidator(min_price=10.0, max_price=1000.0)
```

### Validator Classes

#### PriceValidator
- Validates price is within acceptable range
- Reports:
  - `price_too_low`: Price ≤ MIN_PRICE
  - `price_too_high`: Price ≥ MAX_PRICE
  - `invalid_price_format`: Non-numeric values

#### SKUValidator
- Validates SKU format matches regex pattern
- Detects duplicate SKUs across catalog
- Reports:
  - `invalid_sku_format`: Format doesn't match pattern
  - `duplicate_sku`: SKU appears multiple times

#### InventoryValidator
- Validates inventory counts are non-negative
- Flags items below low-stock threshold
- Reports:
  - `negative_inventory`: Stock < MIN_INVENTORY
  - `low_stock_warning`: Stock < LOW_STOCK_THRESHOLD
  - `invalid_inventory_format`: Non-integer values

---

## SQL Analytics Layer

### Database Schema (Auto-Generated)

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT,
    product_name TEXT,
    category TEXT,
    price REAL,
    inventory_count INTEGER,
    supplier_id TEXT,
    last_updated TEXT
);
```

### Built-In Analytics Queries

#### Query 1: Duplicate SKU Detection
```python
db.detect_duplicate_skus()
# Returns: [{sku, occurrence_count}, ...]
```

**Use Case**: Identify data inconsistencies requiring manual review

#### Query 2: Category Distribution
```python
db.count_records_by_category()
# Returns: [{category, record_count}, ...]
```

**Use Case**: Understand catalog composition and category coverage

#### Query 3: High-Value Products
```python
db.find_high_price_products(threshold=5000)
# Returns: [{sku, product_name, price}, ...]
```

**Use Case**: Identify premium inventory requiring special handling

#### Query 4: Inventory by Category
```python
db.calculate_inventory_by_category()
# Returns: [{category, total_inventory}, ...]
```

**Use Case**: Aggregate stock levels for supply chain planning

#### Custom Queries
```python
db.execute_query(sql, params)
# Returns: [dict, ...] for any arbitrary SQL
```

---

## Sample Metrics Output

### Data Quality Dashboard

```
================================================================================
DATA QUALITY VALIDATION DASHBOARD
================================================================================
Generated: 2026-02-15 11:23:16
================================================================================

SUMMARY STATISTICS
--------------------------------------------------------------------------------
  Total Records:                 200
  Valid Records:                 183  [OK]
  Invalid Records:                17  [ERR]
  Total Errors Found:             19

DATA INTEGRITY SCORE
--------------------------------------------------------------------------------
  Score:  91.50%  [EXCELLENT]
  [##################--]

TOP 5 ISSUE TYPES BY FREQUENCY
--------------------------------------------------------------------------------
  1. duplicate_sku                       9 ( 47.4%)  [#########-]
  2. price_too_low                       6 ( 31.6%)  [######----]
  3. low_stock_warning                   2 ( 10.5%)  [##--------]
  4. negative_inventory                  2 ( 10.5%)  [##--------]

================================================================================
  [WARN] 17 records contain validation issues.
================================================================================
```

### Validation Report (CSV)
Located at: `output/validation_report.csv`

| sku | issue_type | issue_description |
|-----|------------|-------------------|
| SKU-00035 | price_too_low | Price -96.03 must be > 0.01 |
| SKU-00060 | price_too_low | Price -258.65 must be > 0.01 |
| SKU-00087 | duplicate_sku | SKU 'SKU-00087' appears 2 times in catalog |
| SKU-00149 | duplicate_sku | SKU 'SKU-00149' appears 3 times in catalog |

### Analytics Output
```
ANALYTICS QUERIES
1. Duplicate SKU Detection:      9 unique SKUs with duplicates
2. Category Distribution:        11 categories, Toys leads (23 records)
3. High-Price Products:          0 products > $5000
4. Inventory by Category:        Toys: 5,448 units (highest)
```

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip or conda

### Clone & Install

```bash
git clone <repository-url>
cd catalog-automation-engine

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Requirements

```
pandas>=1.0
SQLAlchemy>=1.4
```

---

## Running the Pipeline

### Full Pipeline Execution

```bash
python main.py
```

**Execution Flow:**
1. Load CSV data
2. Run all validators
3. Generate validation report
4. Display metrics dashboard
5. Load data into SQLite
6. Run SQL analytics queries
7. Print summary report

### Output Files
- `output/validation_report.csv` — Detailed validation errors
- `catalog.db` — SQLite database with products table

---

## Configuration

Edit `config.py` to adjust validation rules and settings:

```python
# Validation Thresholds
MIN_PRICE = 0.01              # Adjust minimum price acceptance
MAX_PRICE = 9999.99           # Adjust maximum price ceiling
MIN_INVENTORY = 0             # Minimum stock threshold
LOW_STOCK_THRESHOLD = 5       # Low-inventory warning trigger
SKU_PATTERN = r"^SKU-\d{5}$"  # SKU format validation

# Reporting
REPORT_OUTPUT_DIR = Path(__file__).parent / "output"
VALIDATION_REPORT_FILENAME = "validation_report.csv"

# Database
DB_TABLE_NAME = "products"
```

### Environment-Specific Configuration

For production environments, override via environment variables:

```bash
export MIN_PRICE=10.0
export MAX_PRICE=5000.0
export LOW_STOCK_THRESHOLD=10
python main.py
```

---

## Future Enhancements

### Phase 2: Real-Time Data Ingestion
- **API Connector**: Direct integration with e-commerce platforms (Shopify, WooCommerce)
- **Event Streaming**: Real-time validation of incoming product updates via Kafka/RabbitMQ
- **Incremental Processing**: Process only changed records instead of full catalog

### Phase 3: Interactive Dashboard UI
- **Web Dashboard**: React/Vue-based UI with real-time metrics
- **Drill-Down Analytics**: Interactive category/supplier analysis
- **Alert Management**: Configure thresholds and receive email/Slack notifications
- **Data Exploration**: Browse invalid records with one-click remediation

### Phase 4: AI/LLM Integration
- **Auto-Correction**: Use LLM to suggest fixes for data quality issues
- - **Anomaly Detection**: ML models to identify unusual pricing/inventory patterns
- **Intelligent Bucketing**: Auto-categorize products based on descriptions
- **Natural Language Queries**: Allow business users to query data in plain English

### Phase 5: Advanced Features
- **Historical Tracking**: Version control for catalog changes with audit logs
- **Predictive Analytics**: Forecast low-stock scenarios
- **Multi-Supplier Support**: Complex validation rules per supplier
- **GraphQL API**: Flexible query interface for external systems

---

## Project Structure

```
catalog-automation-engine/
│
├── main.py                      # Pipeline orchestration entry point
├── config.py                    # Centralized configuration & thresholds
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── data/
│   └── sample_catalog.csv       # Sample product data (200 records)
│
├── validators/
│   ├── __init__.py
│   ├── base_validator.py        # Abstract validator base class
│   ├── price_validator.py       # Price range validation
│   ├── sku_validator.py         # SKU format & duplicate detection
│   └── inventory_validator.py   # Stock level validation
│
├── reporting/
│   ├── report_generator.py      # CSV report generation
│   └── metrics.py               # Metrics calculation & dashboard
│
├── database/
│   └── db_manager.py            # SQLite manager & analytics queries
│
├── output/
│   └── validation_report.csv    # Generated validation report
│
└── catalog.db                   # SQLite database (auto-generated)
```

---

## Development

### Running Tests

```bash
python -m pytest tests/ -v
```

### Adding Custom Validators

1. Create new file in `validators/`:
```python
from .base_validator import BaseValidator

class CustomValidator(BaseValidator):
    def validate(self, dataframe):
        errors = []
        # Your validation logic here
        return errors
```

2. Update `validators/__init__.py`:
```python
from .custom_validator import CustomValidator
__all__ = [..., "CustomValidator"]
```

3. Use in pipeline:
```python
from validators import CustomValidator
validator = CustomValidator()
errors = validator.validate(df)
```

---

## License

Proprietary - Enterprise Use Only

---

## Support

For questions or issues:
- Create issue in repository
- Contact: data-engineering@company.com

---

**Last Updated**: February 15, 2026  
**Version**: 1.0.0
