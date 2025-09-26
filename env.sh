#!/bin/sh

export KC_BOOTSTRAP_ADMIN_USERNAME=admin
export KC_BOOTSTRAP_ADMIN_PASSWORD=admin
export KEYCLOAK_REALM=demo-mcp
export KEYCLOAK_CLIENT_ID=mcp-secure
export KEYCLOAK_SECRET=6UJzbvU6H29BeiiEUx6f4lfqKFzMu9nD

export OPENAI_API_KEY=sk-Rt7ipOp_1dw2LePgJ6NZc1bii2PqH6tcQ1msGVkvryT3BlbkFJkQ9NVAHcahNbjxjs755swPpM-yysYANh3ZuePHSx4A
export AUDIENCE=aud-var
export LIFETIME_SECONDS=3600
export DBNAME=users
export REDIS_URL=redis://localhost:6379/0
export RABBIT=amqp://test:test@rabbit:5672
export POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/postgres
export SECRET=47e2a7e0b520f92877df56a98407e69be83614e7a98027d989d1f00e61cbc322