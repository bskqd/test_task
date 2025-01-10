# How to run the tests

1. Make sure you are in the root project directory: `cd tests_task`
2. Run the tests with the following command: `docker-compose -f docker-compose-tests.yml down -v && docker-compose --env-file .env.tests -f docker-compose-tests.yml up -d --build`