This application runs in docker so there isnt any need to install any dependencies.

The only requirement is to have docker & docker-compose installed.

Run `docker-compose up --build` to start all the microservices.

# Unit tests

In the root directory of each microservice there is a tests folder containing the  unit tests for that service.

There are two ways to run the unit tests:
- Inside the docker-context and outside the docker-context.

- `docker exec -it <container_id> pytest`
  - This runs the tests inside the container. You can get the container_id by running `docker ps`
  - e.g. `docker exec -it f7d48c196b37 pytest -m workflow_create_route`
- `pytest -m workflow_create_route`
  - This runs the tests outside the container. You need to have all the dependencies installed in your local machine in a python environment.
  - e.g. `pytest -m workflow_create_route`
  - To install the microservices dependencies you can run `pip install .` & `pip install -e .[test]` in the root directory of each microservice.


# Microservice Swagger API Documentation
The FastAPI framework is whats known as "self-documenting".

This means that the API documentation is automatically generated based on the code and annotations in the application.
- tasks microservice: http://localhost:5000/docs
- metadata microservice: http://localhost:5003/docs

# PGAdmin
I've included a PgAdmin container that is pre-configured to use the postgres database in the conpose file.

After youve run some unit tests or used the API you can view the database in PGAdmin.

Available at: [http://localhost:8085/browser](http://localhost:8085/browser)
username: alexjslessor@gmail.com
password: admin


## SQL Queries for PGAdmin
```sql
SELECT * FROM public.workflow;
DELETE FROM public.workflow;
```