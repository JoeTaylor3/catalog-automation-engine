"""
Report generator utilities.
Contains functions to generate validation reports in CSV format and other formats.
"""

import csv
from pathlib import Path
from .metrics import calculate_metrics


def generate_csv_report(validation_errors, output_path="output/validation_report.csv"):
    """Generate a CSV validation report from validator errors.
    
    Args:
        validation_errors: List of error dicts with keys: sku, issue_type, issue_description
        output_path: Path to write CSV report (default: output/validation_report.csv)
        
    Returns:
        str: Path to generated report file
    """
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write CSV with error details
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["sku", "issue_type", "issue_description"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for error in validation_errors:
            writer.writerow({
                "sku": error.get("sku", ""),
                "issue_type": error.get("issue_type", ""),
                "issue_description": error.get("issue_description", "")
            })
    
    print(f"\n[OK] Validation report saved: {output_path}")
    return str(output_path)


def generate_metrics_report(validation_errors, total_records):
    """Generate comprehensive metrics report.
    
    Args:
        validation_errors: List of error dicts from validators
        total_records: Total number of records in dataset
        
    Returns:
        dict: Metrics summary
    """
    return calculate_metrics(validation_errors, total_records)
