from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pyodbc
import random
from datetime import datetime

app = Flask(__name__)

# Azure SQL Database connection string
conn_str = "DRIVER={ODBC Driver 18 for SQL Server};" \
           "SERVER=tcp:health-monitoring.database.windows.net,1433;" \
           "DATABASE=metrics;" \
           "UID=farooq;" \
           "PWD=F4DD0EC0F4DD0Ec0!!;" \
           "Encrypt=yes;" \
           "TrustServerCertificate=no;" \
           "Connection Timeout=30;"

# Predefined LOINC codes (standard codes for medical measurements)
LOINC_CODES = {
    "Heart Rate": "8867-4",
    "SpO2": "20564-1",
    "Body Humidity": "N/A",  # No standard LOINC for this
    "UV Index": "N/A",  # No standard LOINC for this
    "Environmental Temperature": "8310-5",
    "Body Temperature": "8310-5",
    "Systolic BP": "8480-6",
    "Diastolic BP": "8462-4",
}

UNITS = {
    "Heart Rate": "bpm",
    "SpO2": "%",
    "Body Humidity": "%",
    "UV Index": "index",
    "Environmental Temperature": "°C",
    "Body Temperature": "°C",
    "Systolic BP": "mmHg",
    "Diastolic BP": "mmHg",
}

def insert_health_data():
    """Insert simulated health data into Azure SQL Database every 60 seconds."""
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        patient_id = "123"  # Fixed patient ID

        # Generating random values for health metrics
        metrics = {
            "Heart Rate": random.randint(60, 100),
            "SpO2": random.randint(95, 100),
            "Body Humidity": random.randint(30, 70),
            "UV Index": round(random.uniform(0, 10), 2),
            "Environmental Temperature": round(random.uniform(20.0, 35.0), 2),
            "Body Temperature": round(random.uniform(36.1, 37.2), 2),
            "Systolic BP": random.randint(90, 140),
            "Diastolic BP": random.randint(60, 90),
        }

        # Batch insert query for efficiency
        query = """INSERT INTO patient_observations 
                   (patient_id, metric_name, loinc_code, value, unit, effectiveDateTime, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""

        # Prepare data for each metric
        data_to_insert = [
            (patient_id, name, LOINC_CODES[name], value, UNITS[name], datetime.now(), "final")
            for name, value in metrics.items()
        ]

        # Execute batch insert
        cursor.executemany(query, data_to_insert)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ {len(data_to_insert)} rows inserted successfully at {datetime.now()}")

    except Exception as e:
        print("❌ Database error:", str(e))

# Run insert function every 60 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(insert_health_data, 'interval', seconds=60)
scheduler.start()

@app.route('/')
def home():
    return "Health Data Inserter Running with FHIR Standard!"

if __name__ == '__main__':
    app.run(debug=True)
