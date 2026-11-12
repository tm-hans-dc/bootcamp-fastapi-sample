from datetime import datetime
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
ITEM_NAMES_ONLY = set()
MAX_ID = 0


def load_env_file(path: Path):
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file(BASE_DIR / ".env")

ITEMS_PATH = Path(os.environ.get("DATASET_LOCATION", "items.json"))
if not ITEMS_PATH.is_absolute():
    ITEMS_PATH = BASE_DIR / ITEMS_PATH

# a function for making your data easily available to obtain
def load_items():
    global MAX_ID
    with ITEMS_PATH.open("r", encoding="utf-8") as file:
        stored_items = json.load(file)

    return_items = {int(item_id): item for item_id, item in stored_items.items()}
    for item in return_items.values():
        item.setdefault("is_sold", False)

    MAX_ID = max(return_items, default=0)
    ITEM_NAMES_ONLY.update(item["name"] for item in return_items.values())
    return return_items


def save_items():
    with ITEMS_PATH.open("w", encoding="utf-8") as file:
        json.dump({str(item_id): item for item_id, item in ITEMS.items()}, file, indent=4)


ITEMS = load_items()
print(f"ITEMS:\n{ITEMS}")
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "This is the root"}


@app.get("/health-check")
def get_health_check():
    return {"message": "server is up", "timestamp": datetime.now().isoformat()}

@app.get("/items", status_code=status.HTTP_200_OK)
def get_items(is_sold: bool | None = None):
    items = list(ITEMS.values())
    if is_sold is not None:
        items = [item for item in items if item.get("is_sold", False) is is_sold]

    return items

# Show that the most basic we can use a fastapi server for is to provided data from a data storage to a frontend
@app.get("/items/{item_id}", status_code=status.HTTP_200_OK)
def get_item(item_id: int):
    item = ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return {"id": int(item_id), "name": item["name"], "price": float(item["price"]), "is_sold": item["is_sold"], "status": "success"}


# Show how we implement adding new items
# Show that there are cases where we need to handle duplicates
class CafeItem(BaseModel):
    name: str | None = None
    price: float | None = None
    is_sold: bool = False

@app.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(payload: CafeItem):
    global MAX_ID
    if payload.name in ITEM_NAMES_ONLY:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Item {payload.name} already exists.")

    ITEM_NAMES_ONLY.add(payload.name)
    MAX_ID += 1
    new_item_id = MAX_ID
    new_item = {"item_id": new_item_id, **payload.model_dump()}
    ITEMS[new_item_id] = new_item
    print(f"added new item {new_item_id}")
    save_items()
    return new_item

@app.patch("/items/{item_id}", status_code=status.HTTP_200_OK)
def change_item(item_id: int, payload: CafeItem):
    if item_id not in ITEMS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found.")
    
    changes = payload.model_dump(exclude_unset=True)
    ITEMS[item_id].update(changes)
    print(f"updated item {item_id}")
    save_items()
    return ITEMS[item_id]

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"item {item_id} not found")
    del ITEMS[item_id]
    print(f"deleted item {item_id}")
    save_items()
