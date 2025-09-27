# Patient Management System using FastAPI

This project is built using [FastAPI](https://fastapi.tiangolo.com/), a modern, fast (high-performance) web framework for building APIs with Python.

## Features

- High performance API endpoints
- Easy integration with databases
- Automatic interactive API documentation (Swagger UI & ReDoc)
- Asynchronous request handling

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn

## Installation

```bash
pip install fastapi uvicorn
```

## Running the Application

```bash
uvicorn main:app --reload
```

Replace `main:app` with your entry point if different.

## Project Structure

```
.
├── main.py
├── patient.json
└── README.md
```
## API Endpoints

- **GET /** – Welcome message  
- **GET /patients** – Retrieve all patient records  
- **GET /patients/{patient_id}** – Retrieve a specific patient record by ID  
- **POST /create-patient** – Add a new patient record  
- **PUT /update/{patient_id}** – Update an existing patient record by ID  
- **DELETE /delete/{patient_id}** – Delete a patient record by ID  
- **GET /sort?sort_by={field}&order={asc|desc}** – Sort patient records by a specified field (age or blood type) and order (ascending or descending)  
- **GET /about** – About the API  


## Documentation

Once running, access interactive docs at:

- Swagger UI: `http://localhost:8000/docs`

## License

This project is licensed under the MIT License.