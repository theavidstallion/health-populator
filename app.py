from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pyodbc
import random

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

def insert_health_data():
    """Insert simulated health data into Azure SQL Database every minute."""
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Generating random values for health metrics
        heart_rate = random.randint(60, 100)  # Normal adult heart rate
        spO2 = random.randint(95, 100)  # Normal oxygen saturation
        body_humidity = random.randint(30, 70)  # Hypothetical body humidity
        uv_level = round(random.uniform(0, 10), 2)  # UV index (0-10)
        env_temp = round(random.uniform(20.0, 35.0), 2)  # Room temperature
        body_temp = round(random.uniform(36.1, 37.2), 2)  # Body temperature

        # Insert into SQL database
        query = """INSERT INTO health_metrics 
                   (heart_rate, spO2, body_humidity, uv_level, env_temp, body_temp) 
                   VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (heart_rate, spO2, body_humidity, uv_level, env_temp, body_temp))

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data inserted successfully!")

    except Exception as e:
        print("❌ Database error:", str(e))

# Run insert function every 60 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(insert_health_data, 'interval', seconds=60)
scheduler.start()

@app.route('/')
def home():
    return "Health Data Inserter Running!"

if __name__ == '__main__':
    app.run(debug=True)
