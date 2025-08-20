import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
from collections import defaultdict
from src.detection_engine import Detection
from src.logger import logger


class AlertEvent:
    def __init__(self, detection: Detection, image_path: str):
        self.detection = detection
        self.image_path = image_path
        self.created_at = datetime.now()
        self.alert_sent = False
        self.alert_sent_at = None
    
    def to_dict(self) -> Dict:
        return {
            'detection': self.detection.to_dict(),
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat(),
            'alert_sent': self.alert_sent,
            'alert_sent_at': self.alert_sent_at.isoformat() if self.alert_sent_at else None
        }


class AlertLogicEngine:
    def __init__(self, config):
        self.config = config
        self.cooldown_minutes = config.get('alerts.cooldown_minutes', 10)
        self.enabled_channels = config.get('alerts.enabled_channels', ['sms'])
        
        self.last_alert_times = defaultdict(lambda: datetime.min)
        self.pending_alerts = asyncio.Queue()
        self.alert_history = []
        
    def should_send_alert(self, detection: Detection) -> bool:
        current_time = datetime.now()
        last_alert_time = self.last_alert_times[detection.class_name]
        time_since_last_alert = current_time - last_alert_time
        
        if time_since_last_alert >= timedelta(minutes=self.cooldown_minutes):
            logger.info(f"Alert cooldown passed for {detection.class_name}")
            return True
        else:
            remaining_cooldown = timedelta(minutes=self.cooldown_minutes) - time_since_last_alert
            logger.info(f"Alert cooldown active for {detection.class_name}, {remaining_cooldown.seconds}s remaining")
            return False
    
    def update_last_alert_time(self, detection: Detection):
        self.last_alert_times[detection.class_name] = datetime.now()
        logger.info(f"Updated last alert time for {detection.class_name}")
    
    async def process_detection(self, detection: Detection, image_path: str) -> Optional[AlertEvent]:
        if self.should_send_alert(detection):
            alert_event = AlertEvent(detection, image_path)
            await self.pending_alerts.put(alert_event)
            self.update_last_alert_time(detection)
            logger.info(f"Alert queued for {detection.class_name}")
            return alert_event
        return None
    
    async def get_pending_alert(self) -> Optional[AlertEvent]:
        try:
            return await asyncio.wait_for(self.pending_alerts.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
    
    def mark_alert_sent(self, alert_event: AlertEvent):
        alert_event.alert_sent = True
        alert_event.alert_sent_at = datetime.now()
        self.alert_history.append(alert_event)
        logger.info(f"Alert marked as sent for {alert_event.detection.class_name}")
    
    def get_alert_statistics(self) -> Dict:
        total_alerts = len(self.alert_history)
        alerts_by_class = defaultdict(int)
        
        for alert in self.alert_history:
            alerts_by_class[alert.detection.class_name] += 1
        
        last_24h_alerts = [
            alert for alert in self.alert_history
            if datetime.now() - alert.created_at <= timedelta(hours=24)
        ]
        
        return {
            'total_alerts': total_alerts,
            'alerts_by_class': dict(alerts_by_class),
            'last_24h_alerts': len(last_24h_alerts),
            'cooldown_status': self._get_cooldown_status()
        }
    
    def _get_cooldown_status(self) -> Dict[str, Dict]:
        current_time = datetime.now()
        status = {}
        
        for class_name, last_alert_time in self.last_alert_times.items():
            time_since_alert = current_time - last_alert_time
            cooldown_remaining = max(
                timedelta(0),
                timedelta(minutes=self.cooldown_minutes) - time_since_alert
            )
            
            status[class_name] = {
                'last_alert': last_alert_time.isoformat(),
                'cooldown_active': cooldown_remaining.total_seconds() > 0,
                'cooldown_remaining_seconds': int(cooldown_remaining.total_seconds())
            }
        
        return status
    
    def cleanup_old_alerts(self, retention_days: int = 30):
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        original_count = len(self.alert_history)
        
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.created_at > cutoff_date
        ]
        
        removed_count = original_count - len(self.alert_history)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old alerts")