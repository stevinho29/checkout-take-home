# SETUP
Run:

```bash
docker compose up -d
This starts both the payment gateway and the bank simulator.

The API is available at:

http://localhost:8081

Swagger documentation:
http://localhost:8081/docs

Swagger json documentation:
http://localhost:8081/openapi.json

```

# Architecture

The project follows a layered architecture inspired by DDD principles.

Given the limited scope of the challenge, I intentionally avoided implementing a complete Domain-Driven Design architecture in order to keep the solution simple and maintainable.

The application is split into:

- Presentation: FastAPI routes and DTOs
- Application: business use cases and orchestration
- Infrastructure: repository implementation and bank client
- Domain(inside application folder): entities, exceptions

# Assumptions

- The acquiring bank is considered the source of truth regarding payment authorization.
- The bank simulator is assumed to be reliable and compliant with its documented contract.
- Since persistence is explicitly out of scope, an in-memory repository is sufficient for this challenge.
- The gateway is responsible for validating requests before forwarding them to the acquiring bank.

# Trade-offs
To keep the implementation focused, I deliberately made the following trade-offs:

- Used an in-memory repository instead of a persistent database.
- Did not implement authentication or merchant authorization.
- Did not implement retries when the acquiring bank returns a 503.
- Kept the API synchronous since asynchronous processing was not part of the requirements.

# Improvements

This implementation intentionally focuses on the functional requirements of the challenge.

If this service were to evolve into production, several areas such as persistence, resiliency and observability would deserve further work.