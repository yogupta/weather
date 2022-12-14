# How to run
- Add API key to `env` file. please refer `.example.env` for format.
- cd to project root

### Run with docker
- ```commandline
  docker build . -t weather
  docker run -p 8000:8000 weather 
  ```
  
- 
### Run with docker compose
- ```commandline
  docker-compose up
  docker-compose down
  ```
  
- 