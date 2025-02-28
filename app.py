from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pyodbc
import random
from datetime import datetime, timedelta

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
    """Insert 60 rows of health data with timestamps spread over the past 60 seconds."""
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = """INSERT INTO health_metrics 
                   (heart_rate, spO2, body_humidity, uv_level, env_temperature, body_temperature, timestamp) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""

        data_batch = []  # Store multiple rows
        current_time = datetime.now()  # Exact execution time

        for i in range(60):  
            # Generate timestamps (first row = 60 sec ago, last row = now)
            timestamp = current_time - timedelta(seconds=(60 - i))
            heart_rate = random.randint(60, 100)
            spO2 = random.randint(95, 100)
            body_humidity = random.randint(30, 70)
            uv_level = round(random.uniform(0, 10), 2)
            env_temperature = round(random.uniform(20.0, 35.0), 2)
            body_temperature = round(random.uniform(36.1, 37.2), 2)

            data_batch.append((heart_rate, spO2, body_humidity, uv_level, env_temperature, body_temperature, row_timestamp))

        cursor.executemany(query, data_batch)  # Bulk insert 60 rows

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ {len(data_batch)} rows inserted from {data_batch[0][-1]} to {data_batch[-1][-1]}")

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
