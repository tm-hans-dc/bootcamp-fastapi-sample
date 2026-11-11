---
name: cafe-items-api
description: Documents the endpoints in the sample FastAPI cafe items application.
---

# Cafe Items API

This document describes the routes implemented in [`main.py`](main.py). The examples assume the server is running at `http://localhost:8000`.

Start the sample server from the `sample/` directory:

```bash
uvicorn main:app --reload --port 8000
```

All routes are currently unauthenticated. JSON request bodies use the `Content-Type: application/json` header.

## `GET /`

Returns a short message from the root route.

```bash
curl -i http://localhost:8000/
```

Success response: `200 OK`

```json
{"message":"This is the root"}
```

## `GET /health-check`

Returns a health message and the server's current timestamp.

```bash
curl -i http://localhost:8000/health-check
```

Success response: `200 OK`

```json
{"message":"server is up","timestamp":"2026-11-11T13:00:00.000000"}
```

The timestamp value is generated at request time; the example value is illustrative.

## `GET /items/{item_id}`

Returns one item by its integer ID.

Path parameter:

- `item_id` — integer item ID.

```bash
curl -i http://localhost:8000/items/3
```

Success response: `200 OK`

```json
{"id":3,"name":"Strawberry Matcha Latte","price":255.25,"status":"success"}
```

Known errors:

- `404 Not Found` when the item ID does not exist.
- `422 Unprocessable Entity` when `item_id` cannot be parsed as an integer.

## `POST /items`

Creates an item, assigns the next ID, and saves the updated collection to the configured JSON file. The current `CafeItem` model makes both fields optional; normal examples should provide both.

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string or `null` | No | Item name. A name already present in the collection returns a conflict. |
| `price` | number or `null` | No | Item price. |

```bash
curl -i -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Honey Oat Matcha","price":255.25}'
```

Success response: `201 Created`

```json
{"item_id":4,"name":"Honey Oat Matcha","price":255.25}
```

Known errors:

- `409 Conflict` when the submitted name already exists.
- `422 Unprocessable Entity` when a supplied field has an invalid type or the request body is not a valid JSON object for the model.

## `PATCH /items/{item_id}`

Updates the supplied fields on an existing item, then saves the collection to the configured JSON file. Omitted fields are left unchanged.

Path parameter:

- `item_id` — integer item ID.

Request body uses the same fields and types as `POST /items`. For a partial update, include only the fields to change.

```bash
curl -i -X PATCH http://localhost:8000/items/3 \
  -H "Content-Type: application/json" \
  -d '{"price":260.5}'
```

Success response: `200 OK`

```json
{"item_id":3,"name":"Strawberry Matcha Latte","price":260.5}
```

Known errors:

- `404 Not Found` when the item ID does not exist.
- `422 Unprocessable Entity` when `item_id` is not an integer or a supplied field has an invalid type.

## `DELETE /items/{item_id}`

Deletes an existing item and saves the updated collection to the configured JSON file.

Path parameter:

- `item_id` — integer item ID.

```bash
curl -i -X DELETE http://localhost:8000/items/3
```

Success response: `204 No Content` with an empty response body.

Known errors:

- `404 Not Found` when the item ID does not exist.
- `422 Unprocessable Entity` when `item_id` cannot be parsed as an integer.

## JSON persistence

The application loads and saves the collection as a JSON object whose keys are item IDs represented as strings. The loader converts those keys to integers for the in-memory `ITEMS` dictionary. By default, the data file is `sample/items.json`; `DATASET_LOCATION` can select a different path. Relative paths are resolved from the directory containing `main.py`.

This whole-file JSON store is intended for a single-process teaching example. It demonstrates how create, update, delete, and read operations relate to persisted data. Concurrent requests or multiple server workers writing the file can overwrite one another; a production application should use a database with appropriate transaction and concurrency handling.
