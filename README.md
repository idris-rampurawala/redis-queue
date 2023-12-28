# Redis Queue

[![The MIT License](https://img.shields.io/badge/license-MIT-orange.svg?style=flat-square)](LICENSE)

  Redis Queue project is aimed at creating a queue based in redis and celery using redis data structures. We can control the task concurrency as per our need

  *Note*: This project is forked from one of my project [Flask Boilerplate](https://github.com/idris-rampurawala/flask-boilerplate) to quickly get started.



# Contributing
  We encourage you to contribute to this project! Please check out the [Contributing](CONTRIBUTING.md) guidelines about how to proceed.

# Getting Started

### Prerequisites

- Python 3.11.3 or higher
- Up and running Redis client

### Project setup
  ```sh
  # clone the repo
  $ git clone git@github.com:idris-rampurawala/redis-queue.git
  # move to the project folder
  $ cd redis-queue
  ```
  If you want to install redis via docker
  ```sh
  $ docker run -d --name="redis-queue" -p 6379:6379 redis
  ```

### Creating virtual environment

- Setup the correct python version using pyenv `pyenv install 3.11.3`
- Install `pipenv` a global python project `pip install pipenv`
- Create a `virtual environment` for this project
  ```sh
  # activating the pipenv environment
  $ pipenv shell
  # install all dependencies (include -d for installing dev dependencies)
  $ pipenv install -d
  ```
### Configuration

- There are 3 configurations `development`, `staging` and `production` in `config.py`. Default is `development`
- Create a `.env` file from `.env.example` and set appropriate environment variables before running the project

### Running app

- Run flask app `python run.py`
- Logs would be generated under `log` folder

### Running celery workers

- Run redis locally before running celery worker
- Celery worker can be started with following command
  ```sh
  # run following command in a separate terminal
  $ celery -A celery_worker.celery worker --loglevel='INFO'  
  # (append `--pool=solo` for windows)
  ```

# Test
  Test if this app has been installed correctly and it is working via following curl commands (or use in Postman)
- Check if the app is running via `status` API
  ```shell
  $ curl --location --request GET 'http://localhost:5000/status'
  ```
- Check if core app API and celery task is working via
  ```shell
  $ curl --location --request GET 'http://localhost:5000/api/v1/core/test'
  ```
- Check if authorization is working via (change `API Key` as per you `.env`)
  ```shell
  $ curl --location --request GET 'http://localhost:5000/api/v1/core/restricted' --header 'x-api-key: 436236939443955C11494D448451F'
  ```
- Push the task to queue
  ```sh
  curl --location 'http://127.0.0.1:5000/api/v1/core/requestor' \
    --header 'Content-Type: application/json' \
    --data '{
        "id": 1
    }'
  ```

# License
 This program is free software under MIT license. Please see the [LICENSE](LICENSE) file in our repository for the full text.