from sqlalchemy import Column, Integer, Float, String, Date
from pydantic import BaseModel, Field
from db import Base

# ==============================================================================
# SQLAlchemy Models (tables)
# ==============================================================================

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, nullable=True)
    lp = Column(Float, nullable=True)
    v = Column(Float, nullable=True)
    gtt = Column(Float, nullable=True)
    gtn = Column(Float, nullable=True)
    ggn = Column(Float, nullable=True)
    ts = Column(Float, nullable=True)
    tp = Column(Float, nullable=True)
    t48 = Column(Float, nullable=True)
    t1 = Column(Float, nullable=True)
    t2 = Column(Float, nullable=True)
    p48 = Column(Float, nullable=True)
    p1 = Column(Float, nullable=True)
    p2 = Column(Float, nullable=True)
    pexh = Column(Float, nullable=True)
    tic = Column(Float, nullable=True)
    mf = Column(Float, nullable=True)
    decay_coeff_comp = Column(Float, nullable=True)
    decay_coeff_turbine = Column(Float, nullable=True)
    turbine_id = Column(Integer, nullable=True)


class TurbineMetadata(Base):
    __tablename__ = "turbine_metadata"

    turbine_id = Column(Integer, primary_key=True)
    location = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    install_date = Column(Date, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, index=True)
    turbine_id = Column(Integer, nullable=True)
    timestamp = Column(String, nullable=True)
    metric = Column(String, nullable=True)              # NEW
    alert_type = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    actual_value = Column(Float, nullable=True)         # NEW
    threshold_value = Column(Float, nullable=True)      # NEW
    description = Column(String, nullable=True)



# ==============================================================================
# Pydantic Models (schemas)
# ==============================================================================

class HealthSummary(BaseModel):
    turbine_id: int
    location: str
    avg_fuel_usage: float
    min_fuel_usage: float
    max_fuel_usage: float
    avg_comp_decay: float
    min_comp_decay: float
    max_comp_decay: float
    avg_turbine_decay: float
    min_turbine_decay: float
    max_turbine_decay: float
    total_alerts: int


class SensorMetrics(BaseModel):
    id: int
    timestamp: str
    lp: float
    v: float
    gtt: float
    gtn: float
    ggn: float
    ts: float
    tp: float
    t48: float
    t1: float
    t2: float
    p48: float
    p1: float
    p2: float
    pexh: float
    tic: float
    mf: float
    decay_coeff_comp: float
    decay_coeff_turbine: float
    turbine_id: int

    class Config:
        orm_mode = True

class AnomalyAlertRequest(BaseModel):
    turbine_id: int = Field(..., description="ID of the turbine")
    metric: str = Field(..., description="Name of the metric (e.g., T48, Pressure)")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Severity level (Warning, Critical, etc.)")
    actual_value: float = Field(..., description="Actual value measured")
    threshold_value: float = Field(..., description="Threshold that was exceeded")
    description: str = Field(..., description="Detailed description of the anomaly")

    class Config:
        schema_extra = {
            "example": {
                "turbine_id": 1,
                "metric": "T48",
                "alert_type": "Overheat",
                "severity": "Critical",
                "actual_value": 1050.5,
                "threshold_value": 1000.0,
                "description": "T48 temperature exceeds threshold."
            }
        }


class AnomalyAlertResponse(BaseModel):
    alert_id: int
    turbine_id: int
    metric: str
    alert_type: str
    severity: str
    actual_value: float
    threshold_value: float
    description: str
    message: str

    class Config:
        orm_mode = True
