"""
Entry point for the catalog-automation-engine.
This module orchestrates the complete data validation and analysis pipeline:
1. Data Ingestion - Load CSV into pandas
2. Validation - Run all validators
3. Database Analysis - Load into SQLite and run queries
4. Reporting - Generate metrics and reports

Run: python main.py
"""

import sys
from pathlib import Path

import pandas as pd

from config import DATA_PATH
from validators import PriceValidator, SKUValidator, InventoryValidator
from reporting.report_generator import generate_csv_report
from reporting.metrics import calculate_metrics, print_dashboard, generate_executive_summary
from database.db_manager import DBManager

# import our AI-based executive summary helper
from ai.llm_summary import generate_ai_summary


def section_header(title):
    # Print a formatted section header
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def stage_info(message):
    # Print stage info message
    print(f"\n>> {message}")


def main():
    # Execute the complete catalog validation and analysis pipeline
    
    # =========================================================================
    # STAGE 1: DATA INGESTION
    # =========================================================================
    section_header("STAGE 1: DATA INGESTION")
    
    try:
        if not DATA_PATH.exists():
            print(f"ERROR: Data file not found at {DATA_PATH}")
            sys.exit(1)
        
        stage_info(f"Loading CSV from {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
        print(f"   [OK] Loaded {len(df)} records with {len(df.columns)} columns")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
    except Exception as e:
        print(f"ERROR during data ingestion: {e}")
        sys.exit(1)
    
    # =========================================================================
    # STAGE 2: VALIDATION
    # =========================================================================
    section_header("STAGE 2: VALIDATION")
    
    all_errors = []
    
    try:
        stage_info("Running PriceValidator...")
        price_validator = PriceValidator()
        price_errors = price_validator.validate(df)
        all_errors.extend(price_errors)
        print(f"   [OK] Found {len(price_errors)} price validation errors")
        
        stage_info("Running SKUValidator...")
        sku_validator = SKUValidator()
        sku_errors = sku_validator.validate(df)
        all_errors.extend(sku_errors)
        print(f"   [OK] Found {len(sku_errors)} SKU validation errors")
        
        stage_info("Running InventoryValidator...")
        inv_validator = InventoryValidator()
        inv_errors = inv_validator.validate(df)
        all_errors.extend(inv_errors)
        print(f"   [OK] Found {len(inv_errors)} inventory validation errors")
        
        print(f"\n   Total validation errors: {len(all_errors)}")
    except Exception as e:
        print(f"ERROR during validation: {e}")
        sys.exit(1)
    
    # =========================================================================
    # STAGE 3: REPORTING (Validation Report)
    # =========================================================================
    section_header("STAGE 3: REPORTING - VALIDATION REPORT")
    
    try:
        stage_info("Generating validation report CSV...")
        report_path = generate_csv_report(all_errors)
        print(f"   [OK] Report saved to {report_path}")
        
        stage_info("Calculating data quality metrics...")
        metrics = calculate_metrics(all_errors, len(df))
        print_dashboard(metrics)
        
        stage_info("Generating executive summary...")
        executive_summary = generate_executive_summary(metrics)
        print("\nEXECUTIVE SUMMARY")
        print("-" * 80)
        print(executive_summary)
        print("-" * 80)
    except Exception as e:
        print(f"ERROR during reporting: {e}")
        sys.exit(1)
    
    # =========================================================================
    # STAGE 4: DATABASE ANALYSIS
    # =========================================================================
    section_header("STAGE 4: DATABASE ANALYSIS")
    
    try:
        # Initialize database
        db_path = Path(__file__).parent / "catalog.db" if __file__ else Path.cwd() / "catalog.db"
        stage_info(f"Initializing SQLite database at {db_path}")
        db = DBManager(db_path=str(db_path))
        
        # Load CSV into database
        stage_info("Loading CSV data into SQLite...")
        record_count = db.load_csv(str(DATA_PATH))
        print(f"   [OK] Loaded {record_count} records into database")
        
        # Run analytics queries
        print("\n" + "-" * 80)
        print("ANALYTICS QUERIES")
        print("-" * 80)
        
        # Query 1: Duplicate SKUs
        stage_info("Query 1: Detecting duplicate SKUs...")
        duplicates = db.detect_duplicate_skus()
        print(f"   Found {len(duplicates)} duplicate SKUs:")
        for dup in duplicates[:5]:
            print(f"     - {dup['sku']}: appears {dup['occurrence_count']} times")
        if len(duplicates) > 5:
            print(f"     ... and {len(duplicates) - 5} more")
        
        # Query 2: Records per category
        stage_info("Query 2: Counting records per category...")
        categories = db.count_records_by_category()
        print(f"   Found {len(categories)} categories:")
        for cat in categories[:5]:
            category_name = cat['category'] if cat['category'] else "[EMPTY]"
            print(f"     - {category_name}: {cat['record_count']} records")
        if len(categories) > 5:
            print(f"     ... and {len(categories) - 5} more")
        
        # Query 3: High-price products
        stage_info("Query 3: Finding products with price > $5000...")
        high_price = db.find_high_price_products(threshold=5000)
        print(f"   Found {len(high_price)} products with price > $5000")
        if high_price:
            for prod in high_price[:3]:
                print(f"     - {prod['sku']}: ${prod['price']:.2f}")
            if len(high_price) > 3:
                print(f"     ... and {len(high_price) - 3} more")
        else:
            print("   (None found in dataset)")
        
        # Query 4: Inventory by category
        stage_info("Query 4: Calculating total inventory by category...")
        inventory = db.calculate_inventory_by_category()
        print(f"   Category inventory summary:")
        for inv in inventory[:5]:
            category_name = inv['category'] if inv['category'] else "[EMPTY]"
            total = inv['total_inventory'] if inv['total_inventory'] else 0
            print(f"     - {category_name}: {total:,} units")
        if len(inventory) > 5:
            print(f"     ... and {len(inventory) - 5} more")
        
        db.disconnect()
        print(f"\n   [OK] Database analysis complete")

        # ---------------------------------------------------------------------
        # AI-generated executive summary (requires metrics & sql insights)
        # ---------------------------------------------------------------------
        # build validation summary from metrics (top issue types)
        validation_summary = {"top_issue_types": [issue for issue, _ in metrics.get("top_5_issues", [])]}
        sql_insights = {
            "duplicate_sku_count": len(duplicates),
            "high_price_anomalies": len(high_price),
            # count low stock warnings in validation errors
            "low_inventory_warnings": sum(1 for err in all_errors if err.get("issue_type") == "low_stock_warning"),
        }
        try:
            ai_summary = generate_ai_summary(metrics, sql_insights, validation_summary)
            print("\nAI EXECUTIVE SUMMARY")
            print("-" * 80)
            print(ai_summary)
            print("-" * 80)

            # save to file under project root `output` directory
            out_path = Path.cwd() / "output" / "executive_summary.txt"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(ai_summary + "\n")
            print(f"\n[OK] AI summary written to {out_path}")
        except Exception as e:
            print(f"WARNING: failed to generate AI summary: {e}")
    except Exception as e:
        print(f"ERROR during database analysis: {e}")
        sys.exit(1)
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    section_header("PIPELINE EXECUTION SUMMARY")
    
    print(f"\nData Records Processed:     {len(df):>10,}")
    print(f"Validation Errors Found:    {len(all_errors):>10,}")
    print(f"Valid Records:              {metrics['valid_records']:>10,}")
    print(f"Data Integrity Score:       {metrics['data_integrity_score']:>10.2f}%")
    print(f"\nValidation Report:          {report_path}")
    print(f"Database File:              {db_path}")
    print("\n" + "=" * 80)
    print("  PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

