# Fuel Efficiency & Turbine Health Monitor

This project is a complete data and API solution for monitoring turbine health and fuel efficiency. It includes an **ETL (Extract, Transform, Load) pipeline** for processing sensor data, an **SQLite database** for storage, and a **FastAPI service** to provide real-time metrics and alerts.

---

## Project Structure

The project is organized into the following key files and directories:

├── Capstone Project.ipynb     # Main ETL pipeline to process and load data
├── db.py                      # Database connection setup (for SQLAlchemy)
├── main.py                    # FastAPI application with API endpoints
├── models.py                  # Defines SQLAlchemy and Pydantic data models
├── turbine_data_renamed.csv   # Raw input data for sensor readings
├── turbine_metadata_upload.csv # Metadata for turbines
├── turbine_data.db            # SQLite database file (generated after running)
├── turbine_data_silver_level  # Processed data for adls /silver
└── README.md


## Getting Started

### Prerequisites

Make sure you have **Python 3.8 or higher** installed. Then, install the required libraries:

```bash
pip install pandas fastapi "uvicorn[standard]" "sqlalchemy" "pydantic[email]"

## Setup and Data Ingestion

### Run the Jupyter Notebook
Open and run all cells in the `Capstone Project.ipynb` notebook. This will perform the following steps:

- Create the `turbine_data.db` SQLite database file.
- Create the `sensor_readings` and `turbine_metadata` tables.
- Load the data from your CSV files into the database.

### Verify the Database
After the notebook finishes, the `turbine_data.db` file will be populated with your sensor and metadata.

---

## Running the API Service

### Start the Server
Open your terminal or command prompt in the project directory and run:

```bash
uvicorn main:app --reload
The --reload flag automatically restarts the server when you make code changes, which is useful for development.

###  Access the API
The service will be running at http://127.0.0.1:8000
You can test the endpoints using a tool like Postman, Swagger or by navigating to the interactive API documentation.

## API Endpoints

### API Documentation: http://127.0.0.1:8000/docs

#### GET /health-summary
Provides a summary of key health metrics for all turbines.

#### GET /sensor-metrics/{turbine_id}
Retrieves the latest sensor readings for a specific turbine.

#### POST /anomaly-alerts
Allows you to log a new anomaly or alert.

#### POST /uploadfile/
Uploads a CSV file to insert data into a specified table (turbine_metadata, sensor_readings, or alerts).

