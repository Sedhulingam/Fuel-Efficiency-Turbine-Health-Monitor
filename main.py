import shutil
import pandas as pd
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import engine, get_db
from models import (
    Base, SensorReading, TurbineMetadata, Alert,
    HealthSummary, SensorMetrics, AnomalyAlertRequest, AnomalyAlertResponse
)

# Create tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Turbine Monitoring API",
    description="FastAPI service to monitor turbine health and anomalies",
    version="1.0.0"
)

# -----------------------------------------------------------------------------
# GET /health-summary
# -----------------------------------------------------------------------------
@app.get("/health-summary", response_model=list[HealthSummary])
def get_health_summary(db: Session = Depends(get_db)):
    summary_data = db.query(
        SensorReading.turbine_id,
        func.avg(SensorReading.mf).label('avg_mf'),
        func.min(SensorReading.mf).label('min_mf'),
        func.max(SensorReading.mf).label('max_mf'),
        func.avg(SensorReading.decay_coeff_comp).label('avg_comp_decay'),
        func.min(SensorReading.decay_coeff_comp).label('min_comp_decay'),
        func.max(SensorReading.decay_coeff_comp).label('max_comp_decay'),
        func.avg(SensorReading.decay_coeff_turbine).label('avg_turbine_decay'),
        func.min(SensorReading.decay_coeff_turbine).label('min_turbine_decay'),
        func.max(SensorReading.decay_coeff_turbine).label('max_turbine_decay'),
    ).group_by(SensorReading.turbine_id).all()

    alert_counts = db.query(
        Alert.turbine_id,
        func.count(Alert.alert_id).label('total_alerts')
    ).group_by(Alert.turbine_id).all()

    alert_dict = {row.turbine_id: row.total_alerts for row in alert_counts}
    response_list = []

    for row in summary_data:
        turbine_meta = db.query(TurbineMetadata).filter(
            TurbineMetadata.turbine_id == row.turbine_id
        ).first()
        location = turbine_meta.location if turbine_meta else "Unknown"

        response_list.append(
            HealthSummary(
                turbine_id=row.turbine_id,
                location=location,
                avg_fuel_usage=row.avg_mf,
                min_fuel_usage=row.min_mf,
                max_fuel_usage=row.max_mf,
                avg_comp_decay=row.avg_comp_decay,
                min_comp_decay=row.min_comp_decay,
                max_comp_decay=row.max_comp_decay,
                avg_turbine_decay=row.avg_turbine_decay,
                min_turbine_decay=row.min_turbine_decay,
                max_turbine_decay=row.max_turbine_decay,
                total_alerts=alert_dict.get(row.turbine_id, 0)
            )
        )
    return response_list

# -----------------------------------------------------------------------------
# GET /sensor-metrics/{turbine_id}
# -----------------------------------------------------------------------------
@app.get("/sensor-metrics/{turbine_id}", response_model=list[SensorMetrics])
def get_sensor_metrics(turbine_id: int, db: Session = Depends(get_db)):
    records = db.query(SensorReading).filter(
        SensorReading.turbine_id == turbine_id
    ).order_by(SensorReading.timestamp.desc()).limit(10).all()

    if not records:
        raise HTTPException(status_code=404, detail=f"No sensor data found for turbine ID {turbine_id}")
    return records

# -----------------------------------------------------------------------------
# POST /anomaly-alerts
# -----------------------------------------------------------------------------
@app.post("/anomaly-alerts", response_model=AnomalyAlertResponse)
def create_anomaly_alert(alert_data: AnomalyAlertRequest, db: Session = Depends(get_db)):
    new_alert = Alert(
        turbine_id=alert_data.turbine_id,
        timestamp=datetime.utcnow().isoformat(),
        metric=alert_data.metric,
        alert_type=alert_data.alert_type,
        severity=alert_data.severity,
        actual_value=alert_data.actual_value,
        threshold_value=alert_data.threshold_value,
        description=alert_data.description
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return AnomalyAlertResponse(
    alert_id=new_alert.alert_id,
    turbine_id=new_alert.turbine_id,
    metric=new_alert.metric,
    alert_type=new_alert.alert_type,
    severity=new_alert.severity,
    actual_value=new_alert.actual_value,
    threshold_value=new_alert.threshold_value,
    description=new_alert.description,
    message=f"Alert for turbine {alert_data.turbine_id} logged successfully."
)


# -----------------------------------------------------------------------------
# POST /uploadfile/
# -----------------------------------------------------------------------------
@app.post("/uploadfile/")
async def upload_csv(table: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Uploads a CSV file and inserts its data into the specified table.
    - table must be one of: 'turbine_metadata', 'sensor_readings', 'alerts'
    """
    try:
        df = pd.read_csv(file.file)
        # Convert date column to datetime objects
        if 'install_date' in df.columns:
            df['install_date'] = pd.to_datetime(df['install_date']).dt.date
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {e}")

    inserted_count = 0

    try:
        if table == "turbine_metadata":
            for _, row in df.iterrows():
                record = TurbineMetadata(
                    turbine_id=row["turbine_id"],
                    location=row["location"],
                    manufacturer=row["manufacturer"],
                    model=row["model"],
                    install_date=row["install_date"],
                )
                db.merge(record)  # This handles the upsert
                inserted_count += 1

        elif table == "sensor_readings":
            # The 'id' column should be removed for autoincrement to work
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
            
            # Using bulk_insert_mappings is still the best for this table
            db.bulk_insert_mappings(SensorReading, df.to_dict(orient="records"))
            inserted_count = len(df)
            
        elif table == "alerts":
            # The 'alert_id' column should be removed for autoincrement to work
            if 'alert_id' in df.columns:
                df = df.drop(columns=['alert_id'])
            db.bulk_insert_mappings(Alert, df.to_dict(orient="records"))
            inserted_count = len(df)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid table name. Use 'turbine_metadata', 'sensor_readings', or 'alerts'.")

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting data: {e}")
    finally:
        file.file.close()

    return {"message": f"Inserted/updated {inserted_count} rows into {table} table."}
