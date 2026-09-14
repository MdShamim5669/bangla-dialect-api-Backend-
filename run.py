import sys
import os
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print(f"Starting Bangla Dialect Translator Backend from {BASE_DIR}...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False, app_dir=str(BASE_DIR))
