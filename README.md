This application runs in docker so there isnt any need to install any dependencies.

The only requirement is to have docker & docker-compose installed.

Run `docker-compose up --build` to start all the microservices.

# Overview

There are 2 microservices in this repository and 1 python library in this project.
```
~/
├── api-lib                     -> shared python library for use in all microservices.
├── demo-mcp-realm.json         -> keycloak realm configuration file.
├── env.sh                      -> environment variables for local development.
├── metadata                    -> metadata microservice
├── pgadmin                     -> pgadmin configuration for local development.
├── pyproject.toml              -> poetry configuration file for running integration tests
├── scripts                     -> scripts for deploying services to kubernetes
├── tasks                       -> tasks microservice
└── test_e2e.py                 -> end to end integration tests
```
# Unit tests
In the root directory of each microservice there is a tests folder containing the  unit tests for that service.

There are two ways to run the unit tests:
- Inside the docker-context and outside the docker-context.
- `docker exec -it <container_name> pytest`
  - This runs the tests inside the container. You can get the container name by running `docker ps` and looking at the name column.
  - e.g. `docker exec -it tasks pytest -m workflow_create_route`
- `pytest -m workflow_create_route`
  - This runs the tests outside the container. You need to have all the dependencies installed in your local machine in a python environment.
  - e.g. `pytest -m workflow_create_route`
  - To install the microservices dependencies you can run `pip install .` & `pip install -e .[test]` in the root directory of each microservice.


# Microservice Swagger API Documentation
The FastAPI framework is whats known as "self-documenting".

This means that the API documentation is automatically generated based on the code and annotations in the application.
- tasks microservice: `http://localhost:5000/docs`
- metadata microservice: `http://localhost:5001/docs`
- keycloak: [http://localhost:8080](http://localhost:8080)
- pgadmin: [http://localhost:8085/browser](http://localhost:8085/browser)
  - username: alexjslessor@gmail.com
  - password: admin

# PGAdmin
I've included a PgAdmin container that is pre-configured to use the postgres database in the conpose file.

After youve run some unit tests or used the API you can view the database in PGAdmin.
- Available at: [http://localhost:8085/browser](http://localhost:8085/browser)
- username: alexjslessor@gmail.com
- password: admin


## SQL Queries for PGAdmin
```sql
SELECT * FROM public.workflow;
DELETE FROM public.workflow;
```

# Keycloak UI
The keycloak container is pre-configured to use the demo-mcp-realm.json file in the root of the repository.

To view the UI navigate to the following URL: [http://localhost:8080](http://localhost:8080)

- username: admin
- password: admin

*References for configuring keycloak.*
- https://www.keycloak.org/server/containers#_exposing_the_container_to_a_different_port
- https://www.keycloak.org/server/containers#_trying_keycloak_in_development_mode


# Useful Commands
- `docker-compose restart <container name>`: Restarts the a container named worker.
- `docker exec -it tasks pytest -m workflow_create_route`: Runs the unit tests with the marker "workflow_create_route" inside the tasks container.