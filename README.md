# How to run

- Create a file `.env`
- Add API key to `.env` file. please refer `.example.env` for format.
- cd to project root

### Run with docker

- ```commandline
  docker build . -t weather
  docker run -p 8000:8000 weather 
  ```

### Run with docker compose

- ```commandline
  docker-compose build
  docker-compose up
  docker-compose down
  ```

Supported languages:

- English (en)
- German (de)
- Hindi (hi)

example request:
endpoint: `localhost:8000/app/`
```json lines
{
  "city": "delhi",
  "lang": "en"//default lang is en
}
```

Curl
```curl
curl --location --request POST 'http://localhost:8000/app/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "city": "Delhi",
    "lang": "en"
}'
```