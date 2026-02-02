from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean,Text
from .db import Base

from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

class LapQueueItem(Base):
    __tablename__ = "lap_queue"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    payload_json = Column(String, nullable=False)

    status = Column(String, nullable=False, default="Queued")
    decision_id = Column(Integer, nullable=True)
    error_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decision"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)

    action = Column(String, nullable=False)

    lap_number = Column(Float, nullable=False)
    position = Column(Float, nullable=False)
    tyre_life = Column(Float, nullable=False)
    compound = Column(String, nullable=False)
    lap_time_sec = Column(Float, nullable=False)

    expected_pit = Column(Float)
    expected_stay = Column(Float)

    model_version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(Text, nullable=False)
    suggested_tyre = Column(String, nullable=True)

class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True)
    decision_id = Column(Integer, nullable=False)
    user_id = Column(String, nullable=False)

    action = Column(String, nullable=False)
    reward = Column(Float, nullable=False)

    lap_number = Column(Float, nullable=False)
    position = Column(Float, nullable=False)
    tyre_life = Column(Float, nullable=False)
    compound = Column(String, nullable=False)
    lap_time_sec = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class UserProfile(Base):
    __tablename__ = "user_profile"

    user_id = Column(String, primary_key=True)
    pit_bias = Column(Float, nullable=False, default=0.0)
    stay_bias = Column(Float, nullable=False, default=0.0)
    updates = Column(Integer, nullable=False, default=0)
    is_temporary = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, nullable=False, default=True)
    new_experiences_since_train = Column(Integer, nullable=False, default=0)
    retrain_threshold = Column(Integer, nullable=False, default=20)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModelVersion(Base):
    __tablename__ = "model_version"

    id = Column(Integer, primary_key=True)
    version = Column(String, nullable=False)
    path = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
