import json
from pathlib import Path

BASE = Path(__file__).parent
TEST_FILE = BASE / "output" / "test_cases.json"
LOG_FILE = BASE / "logs.txt"

def main():
    data = []
    if TEST_FILE.exists():
        with TEST_FILE.open() as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    print(f"Loaded {len(data)} test case(s).")
    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write(f"Loaded {len(data)} test case(s).\n")


if __name__ == "__main__":
    main()

