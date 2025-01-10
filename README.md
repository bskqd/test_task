# How to run

1. Clone the repo: `git clone https://github.com/bskqd/test_task.git`
2. Go into project directory: `cd test_task`
3. Create `.env` file with variables provided in [.env.example](.env.example)
4. Make sure that ports `8000`, `9000`, `9001`, `5433` aren't already occupied by other processes on your PC
5. Run docker compose: `docker-compose up -d --build`
6. Run migrations: `docker exec test_task_app alembic upgrade head`

# API documentation

After starting the service, API documentation will be available via: `http://127.0.0.1:8000/docs`

# Tests

To run tests follow this [README.md](./tests/README.md)