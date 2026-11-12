import requests
import os

from pathlib import Path
from enum import StrEnum
from typing import Any

def load_env_file(path: Path):
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

BASE_DIR = Path(__file__).resolve().parent
load_env_file(BASE_DIR / ".env")
FASTAPI_ENDPOINT_URL = f'''{os.environ.get("ENDPOINT_URL", "http://localhost")}:{os.environ.get("ENDPOINT_PORT", 8000)}'''

class CrudAction(StrEnum):
    CREATE = "POST"
    READ = "GET"
    UPDATE = "PATCH"
    DELETE = "DELETE"

def execute_crud_action(action: CrudAction, route: str, payload: dict[str, Any] | None = None):
    full_route = f"{FASTAPI_ENDPOINT_URL}{route}"
    print(f"{action} {full_route}")

    res = requests.request(method=action, url=full_route, json=payload)

    print(res.status_code)

    if not res.content:
        print("(no response body)")
    elif "application/json" in res.headers.get("Content-Type", ""):
        print(res.json())
    else:
        print(res.text)

    res.raise_for_status()
    return res

def GET_ENDPOINT(route: str):
    full_route = f"{FASTAPI_ENDPOINT_URL}{route}"
    print(f"GET {full_route}")
    
    res = requests.get(full_route)
    print(res.status_code)
    print(res.json())
    return res

# Uncomment the lines of res that you want to try

# Sample GET root
# res = execute_crud_action(CrudAction.READ, "/")

# Sample GET health-check
# res = execute_crud_action(CrudAction.READ, "/health-check")

# Sample GET /items where is_sold = True
# res = execute_crud_action(CrudAction.READ, "/items?is_sold=true")

# Sample GET /items/3
# res = execute_crud_action(CrudAction.READ, "/items/3")

# Sample GET /items/4 (does not exist)
# res = execute_crud_action(CrudAction.READ, "/items/4")

# Sample POST /items {"name": "Orange Americano", "price": 150, "is_sold": true}
# res = execute_crud_action(
#     action = CrudAction.CREATE,
#     route = "/items",
#     payload = {"name": "Orange Americano", "price": 150, "is_sold": True}
# )

# Sample GET /items/4 (should exist now)
# res = execute_crud_action(CrudAction.READ, "/items/4")

# res = execute_crud_action(
#     action = CrudAction.UPDATE,
#     route = "/items/4",
#     payload = {"name": "Iced Orange Americano", "price": 155}
# )

# Sample DELETE /items/4
# res = execute_crud_action(
#     action = CrudAction.DELETE,
#     route = "/items/4"
# )