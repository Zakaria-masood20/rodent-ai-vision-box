from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
from src.logger import logger

Base = declarative_base()


class DetectionRecord(Base):
    __tablename__ = 'detections'
    
    id = Column(Integer, primary_key=True)
    class_name = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    bbox_x1 = Column(Integer, nullable=False)
    bbox_y1 = Column(Integer, nullable=False)
    bbox_x2 = Column(Integer, nullable=False)
    bbox_y2 = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)
    detection_datetime = Column(DateTime, nullable=False)
    image_path = Column(String(255), nullable=False)
    alert_sent = Column(Boolean, default=False)
    alert_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.database_path = config.get('storage.database_path', 'data/detections.db')
        self.engine = self._create_engine()
        self.Session = sessionmaker(bind=self.engine)
        self._create_tables()
    
    def _create_engine(self):
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        connection_string = f'sqlite:///{db_path}'
        logger.info(f"Creating database engine: {connection_string}")
        
        return create_engine(connection_string, echo=False)
    
    def _create_tables(self):
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")
    
    def save_detection(self, detection, image_path: str, alert_sent: bool = False):
        session = self.Session()
        try:
            record = DetectionRecord(
                class_name=detection.class_name,
                confidence=detection.confidence,
                bbox_x1=detection.bbox[0],
                bbox_y1=detection.bbox[1],
                bbox_x2=detection.bbox[2],
                bbox_y2=detection.bbox[3],
                timestamp=detection.timestamp,
                detection_datetime=detection.datetime,
                image_path=image_path,
                alert_sent=alert_sent,
                alert_sent_at=datetime.now() if alert_sent else None
            )
            
            session.add(record)
            session.commit()
            logger.info(f"Detection saved to database: {detection.class_name}")
            
        except Exception as e:
            logger.error(f"Failed to save detection: {e}")
            session.rollback()
        finally:
            session.close()
    
    def update_alert_status(self, detection_id: int):
        session = self.Session()
        try:
            record = session.query(DetectionRecord).filter_by(id=detection_id).first()
            if record:
                record.alert_sent = True
                record.alert_sent_at = datetime.now()
                session.commit()
                logger.info(f"Alert status updated for detection {detection_id}")
            
        except Exception as e:
            logger.error(f"Failed to update alert status: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_recent_detections(self, hours: int = 24):
        session = self.Session()
        try:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            records = session.query(DetectionRecord).filter(
                DetectionRecord.timestamp >= cutoff_time
            ).order_by(DetectionRecord.timestamp.desc()).all()
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get recent detections: {e}")
            return []
        finally:
            session.close()
    
    def get_detection_statistics(self):
        session = self.Session()
        try:
            total_detections = session.query(DetectionRecord).count()
            
            detections_by_class = {}
            for class_name in ['roof_rat', 'norway_rat', 'mouse']:
                count = session.query(DetectionRecord).filter_by(
                    class_name=class_name
                ).count()
                detections_by_class[class_name] = count
            
            alerts_sent = session.query(DetectionRecord).filter_by(
                alert_sent=True
            ).count()
            
            last_24h = datetime.now().timestamp() - 86400
            recent_detections = session.query(DetectionRecord).filter(
                DetectionRecord.timestamp >= last_24h
            ).count()
            
            return {
                'total_detections': total_detections,
                'detections_by_class': detections_by_class,
                'alerts_sent': alerts_sent,
                'last_24h_detections': recent_detections
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
        finally:
            session.close()
    
    def cleanup_old_records(self, retention_days: int = 30):
        session = self.Session()
        try:
            cutoff_date = datetime.now().timestamp() - (retention_days * 86400)
            old_records = session.query(DetectionRecord).filter(
                DetectionRecord.timestamp < cutoff_date
            ).all()
            
            count = len(old_records)
            for record in old_records:
                if Path(record.image_path).exists():
                    Path(record.image_path).unlink()
                session.delete(record)
            
            session.commit()
            logger.info(f"Cleaned up {count} old detection records")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            session.rollback()
        finally:
            session.close()