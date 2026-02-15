"""
Metrics helpers for reporting.
Calculate data quality KPIs and generate dashboard-style summaries.
"""

from collections import Counter
from datetime import datetime


def calculate_metrics(validation_errors, total_records):
    """Calculate comprehensive data quality metrics.
    
    Args:
        validation_errors: List of error dicts with keys: sku, issue_type, issue_description
        total_records: Total number of records in dataset
        
    Returns:
        dict: Metrics summary including scores and top issues
    """
    invalid_records = len(set(err["sku"] for err in validation_errors))
    valid_records = total_records - invalid_records
    data_integrity_score = (valid_records / total_records * 100) if total_records > 0 else 0
    
    # Count issue types
    issue_counter = Counter(err["issue_type"] for err in validation_errors)
    top_5_issues = issue_counter.most_common(5)
    
    return {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "data_integrity_score": round(data_integrity_score, 2),
        "total_errors": len(validation_errors),
        "top_5_issues": top_5_issues
    }


def print_dashboard(metrics):
    """Print a clean CLI dashboard-style metrics summary.
    
    Args:
        metrics: Dictionary from calculate_metrics()
    """
    print("\n" + "=" * 80)
    print("DATA QUALITY VALIDATION DASHBOARD")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Summary section
    print("\nSUMMARY STATISTICS")
    print("-" * 80)
    print(f"  Total Records:          {metrics['total_records']:>10,}")
    print(f"  Valid Records:          {metrics['valid_records']:>10,}  [OK]")
    print(f"  Invalid Records:        {metrics['invalid_records']:>10,}  [ERR]")
    print(f"  Total Errors Found:     {metrics['total_errors']:>10,}")
    
    # Data integrity score
    print("\nDATA INTEGRITY SCORE")
    print("-" * 80)
    score = metrics['data_integrity_score']
    score_bar = "#" * int(score / 5) + "-" * (20 - int(score / 5))
    
    if score >= 90:
        status = "[EXCELLENT]"
    elif score >= 75:
        status = "[GOOD]"
    elif score >= 50:
        status = "[FAIR]"
    else:
        status = "[POOR]"
    
    print(f"  Score: {score:>6.2f}%  {status}")
    print(f"  [{score_bar}]")
    
    # Top 5 issues
    print("\nTOP 5 ISSUE TYPES BY FREQUENCY")
    print("-" * 80)
    if metrics['top_5_issues']:
        for idx, (issue_type, count) in enumerate(metrics['top_5_issues'], 1):
            percentage = (count / metrics['total_errors'] * 100) if metrics['total_errors'] > 0 else 0
            bar = "#" * int(percentage / 5) + "-" * (10 - int(percentage / 5))
            print(f"  {idx}. {issue_type:<30} {count:>6} ({percentage:>5.1f}%)  [{bar}]")
    else:
        print("  No issues found!")
    
    # Validation summary
    print("\n" + "=" * 80)
    if metrics['invalid_records'] == 0:
        print("  [OK] All records passed validation!")
    else:
        print(f"  [WARN] {metrics['invalid_records']:,} records contain validation issues.")
    print("=" * 80 + "\n")


def generate_executive_summary(metrics):
    """Generate a human-readable executive summary paragraph.
    
    Produces a professional, rule-based summary of validation findings
    without requiring external APIs or LLMs.
    
    Args:
        metrics: Dictionary from calculate_metrics()
        
    Returns:
        str: Executive summary paragraph
    """
    total = metrics['total_records']
    valid = metrics['valid_records']
    invalid = metrics['invalid_records']
    score = metrics['data_integrity_score']
    errors = metrics['total_errors']
    top_issues = metrics['top_5_issues']
    
    # Calculate issue percentages
    invalid_pct = (invalid / total * 100) if total > 0 else 0
    
    # Determine health status
    if score >= 90:
        health_status = "excellent"
        health_verb = "demonstrates"
    elif score >= 75:
        health_status = "good"
        health_verb = "shows"
    elif score >= 50:
        health_status = "fair"
        health_verb = "indicates"
    else:
        health_status = "poor"
        health_verb = "reveals"
    
    # Build top issues summary
    if not top_issues:
        top_issues_text = "no validation errors were identified"
    else:
        top_3_issues = top_issues[:3]
        issue_names = []
        for issue_type, count in top_3_issues:
            pct = (count / errors * 100) if errors > 0 else 0
            # Convert snake_case to readable format
            readable_issue = issue_type.replace('_', ' ').title()
            issue_names.append(f"{readable_issue} ({int(pct)}%)")
        
        if len(issue_names) == 1:
            top_issues_text = f"driven by {issue_names[0]}"
        elif len(issue_names) == 2:
            top_issues_text = f"primarily driven by {issue_names[0]} and {issue_names[1]}"
        else:
            top_issues_text = f"primarily driven by {', '.join(issue_names[:-1])}, and {issue_names[-1]}"
    
    # Build summary based on data quality
    if invalid == 0:
        summary = (
            f"Analysis of {total:,} catalog records identified no data integrity issues. "
            f"All products passed validation with a perfect {score:.1f}% integrity score. "
            f"The catalog is production-ready without requiring remediation."
        )
    elif invalid_pct < 5:
        summary = (
            f"Analysis of {total:,} catalog records identified {invalid_pct:.1f}% data integrity issues "
            f"({invalid:,} records), {top_issues_text}. With a {health_status} integrity score "
            f"of {score:.1f}%, the catalog {health_verb} strong data quality suitable for production use "
            f"with minimal remediation required."
        )
    elif invalid_pct < 15:
        summary = (
            f"Analysis of {total:,} catalog records identified {invalid_pct:.1f}% data integrity issues "
            f"({invalid:,} records), {top_issues_text}. The {health_status} integrity score "
            f"of {score:.1f}% {health_verb} moderate data quality concerns. Recommended immediate action "
            f"includes deduplication efforts and category standardization to improve catalog quality."
        )
    else:
        summary = (
            f"Analysis of {total:,} catalog records identified significant data integrity issues "
            f"affecting {invalid_pct:.1f}% of records ({invalid:,} records), {top_issues_text}. "
            f"With a {health_status} integrity score of {score:.1f}%, urgent remediation is required. "
            f"Priority actions include resolving duplicate SKUs, standardizing missing fields, and "
            f"implementing upstream validation to prevent future data quality degradation."
        )
    
    return summary


def compute_basic_metrics(results):
    """Legacy function - kept for backward compatibility.
    
    Compute simple metrics from an iterable of (is_valid, message) tuples.
    """
    total = 0
    passed = 0
    failed = 0
    for r in results:
        total += 1
        if r and r[0]:
            passed += 1
        else:
            failed += 1
    return {"total": total, "passed": passed, "failed": failed}
