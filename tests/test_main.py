import json
from ai_requirements_pipeline.main import main

def test_main_runs():
    # basic smoke test: ensure main() runs without raising
    main()
