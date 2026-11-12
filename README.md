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

## Calling the API with Python

[`client.py`](client.py) is a sample Python script that calls this FastAPI server programmatically. It demonstrates GET, POST, PATCH, and DELETE requests using the `requests` package. Keep the server running in one terminal, then open a second terminal in `sample/`.

```bash
python -m pip install requests
```

The request examples in `client.py` are commented out. Uncomment the example or examples you want to try, save the file, then run the script from `sample/`:

```bash
python client.py
```

For example, to use the simple GET helper to list sold cafe items, add:

```python
res = GET_ENDPOINT("/items?is_sold=true")
```

For the shared CRUD helper, choose the matching `CrudAction` (`READ`, `CREATE`, `UPDATE`, or `DELETE`), route, and—when sending a request body—payload. To demonstrate a successful create, read, update, and delete sequence, uncomment the POST, following GET, PATCH, and DELETE examples for item `4`. Leave the earlier example that reads the not-yet-created item commented out: an unsuccessful `execute_crud_action` call raises an HTTP error and stops the script.

POST and PATCH examples change the JSON data file used by the server. The script prints the HTTP status and response body; `execute_crud_action` also raises an error for unsuccessful HTTP responses.

The client uses Python 3.11 or later because it imports `StrEnum`. It reads optional `ENDPOINT_URL` and `ENDPOINT_PORT` values from `sample/.env`. Their defaults are `http://localhost` and `8000`, respectively:

```dotenv
ENDPOINT_URL=http://localhost
ENDPOINT_PORT=8000
```

Set `ENDPOINT_URL` to the scheme and host without a port, since the script appends `ENDPOINT_PORT` when building the server address.

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

## `GET /items`

Returns the cafe collection. The optional `is_sold` boolean query parameter filters the result; omit it to return all items.

```bash
curl -i http://localhost:8000/items
```

Filter for sold items:

```bash
curl -i 'http://localhost:8000/items?is_sold=true'
```

Success response: `200 OK`

```json
[
  {
    "item_id": 2,
    "name": "Ube Matcha Latte",
    "price": 250,
    "is_sold": true
  }
]
```

Use `is_sold=false` to return items that have not been sold. In the sample data, those are item IDs `0`, `1`, and `3`.

```bash
curl -i 'http://localhost:8000/items?is_sold=false'
```

FastAPI returns `422 Unprocessable Entity` if `is_sold` is not a boolean value such as `true` or `false`.

## `GET /items/{item_id}`

Returns one item by its integer ID.

Path parameter:

- `item_id` — integer item ID.

```bash
curl -i http://localhost:8000/items/3
```

Success response: `200 OK`

```json
{"id":3,"name":"Strawberry Matcha Latte","price":255.25,"is_sold":false,"status":"success"}
```

The `is_sold` field describes the cafe item. The separate `status` value in this response is response metadata.

Known errors:

- `404 Not Found` when the item ID does not exist.
- `422 Unprocessable Entity` when `item_id` cannot be parsed as an integer.

## `POST /items`

Creates an item, assigns the next ID, and saves the updated collection to the configured JSON file. The current `CafeItem` model makes its fields optional; normal examples should provide a name and price. If `is_sold` is omitted, the new item defaults to `false`.

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string or `null` | No | Item name. A name already present in the collection returns a conflict. |
| `price` | number or `null` | No | Item price. |
| `is_sold` | boolean | No | Whether the item has been sold. Defaults to `false`. |

```bash
curl -i -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Honey Oat Matcha","price":255.25,"is_sold":false}'
```

Success response: `201 Created`

```json
{"item_id":4,"name":"Honey Oat Matcha","price":255.25,"is_sold":false}
```

Known errors:

- `409 Conflict` when the submitted name already exists.
- `422 Unprocessable Entity` when a supplied field has an invalid type or the request body is not a valid JSON object for the model.

## `PATCH /items/{item_id}`

Updates the supplied fields on an existing item, then saves the collection to the configured JSON file. Omitted fields are left unchanged.

Path parameter:

- `item_id` — integer item ID.

Request body uses the same fields and types as `POST /items`. For a partial update, include only the fields to change; `is_sold` can be set to either `true` or `false`.

```bash
curl -i -X PATCH http://localhost:8000/items/3 \
  -H "Content-Type: application/json" \
  -d '{"is_sold":true}'
```

Success response: `200 OK`

```json
{"item_id":3,"name":"Strawberry Matcha Latte","price":255.25,"is_sold":true}
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
