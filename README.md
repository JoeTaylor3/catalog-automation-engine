# Requirements Pipeline

This project contains a starter structure for a requirements validation pipeline.

Usage:

- Run the main script:

```powershell
python catalog-automation-engine\main.py
```

**CI / Tests**: GitHub Actions workflow added at `.github/workflows/python-package.yml`.

- Status badge (replace `{owner}` and `{repo}` and add to the top of this README):

  `![CI](https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/python-package.yml?branch=main)`

- To run tests locally in the created venv:

```powershell
Set-Location C:\Users\blond\ai_requirements_pipeline
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\pytest -q
```
