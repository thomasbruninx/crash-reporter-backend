# crash-reporter-backend

Crash Reporter offers a RESTful API for crash report management. It provides endpoints for report submission, retrieval, and management, collected on a per-project and per-instance basis. The backend is built with FastAPI and uses SQLite and MongoDB for data storage.

## Starting the development server

Initialize a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Run the development server:
```bash
uvicorn app.main:app --reload
```

## Deploying with Docker

Build the Docker image: 
```bash
docker build -t crash-reporter-backend .
```

## Create users

Run this command from the project root to create a user:
```bash
python scripts/create_user.py --username admin --password mysecretpassword
```

## API Endpoints

### Reports
- `POST /api/v1/report/`: Submit a crash report
- `PUT/PATCH /api/v1/report/{report_id}`: Update a crash report's details
- `GET /api/v1/report/query`: Retrieve crash reports by query parameters
- `GET /api/v1/report/{report_id}`: Retrieve a specific crash report
- `DELETE /api/v1/report/{report_id}`: Delete a specific crash report

### Projects
- `POST /api/v1/project/`: Create a new project
- `PUT/PATCH /api/v1/project/{project_id}`: Update a project's details
- `GET /api/v1/project/query`: Retrieve projects by query parameters
- `GET /api/v1/project/{project_id}`: Retrieve a specific project
- `DELETE /api/v1/project/{project_id}`: Delete a specific project

### Instances
- `POST /api/v1/instance/`: Create a new instance
- `PUT/PATCH /api/v1/instance/{instance_id}`: Update an instance's details
- `GET /api/v1/instance/query`: Retrieve instances by query parameters
- `GET /api/v1/instance/{instance_id}/`: Retrieve a specific instance
- `DELETE /api/v1/instance/{instance_id}/`: Delete a specific instance

### Login and user management
- `POST /api/v1/login`: Authenticate a user and obtain a JWT token
- `POST /api/v1/user`: Create a new user

## Client, SDK, and OpenAPI specification

A Go library is available in the `crash-reporter-go` repository. A reference client implementation is available in the `crash-reporter-client` repository.

You can also use the OpenAPI specification to generate client code for your preferred language or framework. The OpenAPI spec is available at `/openapi.json` when the backend server is running.