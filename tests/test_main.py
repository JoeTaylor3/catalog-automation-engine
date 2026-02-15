import json
import os
import sys
import importlib.util
from pathlib import Path

import pytest


def load_pipeline_main():
    # dynamically load the catalog-automation-engine main script
    module_path = Path(__file__).parent.parent / "catalog-automation-engine" / "main.py"
    # ensure the package directory is on sys.path so relative imports succeed
    pkg_dir = module_path.parent
    if str(pkg_dir) not in sys.path:
        sys.path.insert(0, str(pkg_dir))

    spec = importlib.util.spec_from_file_location("pipeline_main", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


@pytest.fixture(autouse=True)
def setup_env(monkeypatch, tmp_path):
    # Run everything in an isolated temporary directory
    monkeypatch.chdir(tmp_path)
    # patch the AI summary call to avoid external API traffic
    import ai.llm_summary

    monkeypatch.setattr(ai.llm_summary, "generate_ai_summary", lambda m, s, v: "DUMMY AI SUMMARY")
    return tmp_path


def test_main_runs_and_writes_summary(tmp_path):
    main_func = load_pipeline_main()
    # ensure it executes without errors
    main_func()

    # verify the AI summary file was created in the temp output folder
    out_file = tmp_path / "output" / "executive_summary.txt"
    assert out_file.exists(), "AI summary file was not created"
    content = out_file.read_text(encoding="utf-8")
    assert "DUMMY AI SUMMARY" in content
