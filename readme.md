# Classical Piano API

A small FastAPI app that manages composers and pieces.

## Endpoints

### GET /composers

Returns a list of composers

Example:

```json
[
  {
    "name": "Sergei Rachmaninoff",
    "composer_id": 1,
    "home_country": "Russia"
  },
  {
    "name": "Franz Liszt",
    "composer_id": 2,
    "home_country": "Hungary"
  }
]
```

### GET /pieces

Returns a list of pieces

- **Query Parameters**:
  - `composer_id` (int) - An optional ID of the composer to filter on

Example:

```json
[
  {
    "name": "Etude Tableaux Op. 39 No. 6",
    "alt_name": "Little Red Riding Hood",
    "difficulty": 9,
    "composer_id": 1
  },
  {
    "name": "Waltz Op. 18 No. 1 in E-Flat Major",
    "alt_name": "Grande valse brillante",
    "difficulty": 4,
    "composer_id": 4
  }
]
```

### POST /composers

Creates a new composer

- **Body**:

  - `name` (string) - Name of the composer
  - `composer_id` (int) - ID of the composer (consider making this auto incrementing so the user doesn't have to pass it in). Raise an HTTP 400 if a duplicate ID is passed in.
  - `home_country` (string) - Country the composer was born in

  Example body:

```json
{
  "name": "Sergei Rachmaninoff",
  "composer_id": 1,
  "home_country": "Russia"
}
```

### POST /pieces

Creates a new piece

- **Body**:
  - `name` (string) - Name of the piece
  - `alt_name` (string) - Optional alternate name of the piece
  - `difficulty` (int) - Difficulty rating of the piece (1-10) (consider restricting the difficulty input to only accept 1-10)
  - `composer_id` (int) - ID of the composer. Raise HTTP 400 exception if the composer ID doesn't exist.

Example body:

```json
{
  "name": "Etude Tableaux Op. 39 No. 6",
  "alt_name": "Little Red Riding Hood",
  "difficulty": 9,
  "composer_id": 1
}
```

### PUT /composers/{composer_id}

Updates a composer if they exist, otherwise they are created

- **Query parameters**:

  - `composer_id` (int) - ID of the composer

- **Body**:

  - `name` (string) - Name of the composer
  - `composer_id` (int) - ID of the composer (consider making this auto incrementing so the user doesn't have to pass it in). Raise an HTTP 400 if a duplicate ID is passed in.
  - `home_country` (string) - Country the composer was born in

  Example body:

```json
{
  "name": "Sergei Rachmaninoff",
  "composer_id": 1,
  "home_country": "Russia"
}
```

### PUT /pieces/{piece_name}

Updates a piece if it exists, otherwise it is created

- **Query parameters**:

  - `piece_name` (string) - Name of the piece

- **Body**:
  - `name` (string) - Name of the piece
  - `alt_name` (string) - Optional alternate name of the piece
  - `difficulty` (int) - Difficulty rating of the piece (1-10) (consider restricting the difficulty input to only accept 1-10)
  - `composer_id` (int) - ID of the composer. Raise HTTP 400 exception if the composer ID doesn't exist.

Example body:

```json
{
  "name": "Etude Tableaux Op. 39 No. 6",
  "alt_name": "Little Red Riding Hood",
  "difficulty": 9,
  "composer_id": 1
}
```

### DELETE /composers/{composer_id}

Deletes a composer

- **Query parameters**:
  - `composer_id` (int) - ID of the composer

### DELETE /pieces/{piece_name}

Deletes a piece

- **Query parameters**:
  - `piece_name` (string) - Name of the piece

## Installation/Running instructions

Run `db.py` to build database and inject existing json data into table.

Run `uvicorn main:app --reload` to run uvicorn back end server
