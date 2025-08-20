import asyncio
import signal
import sys
import time
from pathlib import Path
from src.config_manager import ConfigManager
from src.logger import setup_logger
from src.video_ingestion import VideoIngestionPipeline
from src.detection_engine import RodentDetectionEngine
from src.alert_engine import AlertLogicEngine
from src.notification_service import NotificationService
from src.database import DatabaseManager


class RodentDetectionSystem:
    def __init__(self):
        self.config = ConfigManager()
        self.logger = setup_logger(self.config)
        self.running = False
        
        self.logger.info("Initializing Rodent Detection System")
        
        self.video_pipeline = VideoIngestionPipeline(self.config)
        self.detection_engine = RodentDetectionEngine(self.config)
        self.alert_engine = AlertLogicEngine(self.config)
        self.notification_service = NotificationService(self.config)
        self.database = DatabaseManager(self.config)
        
        self.images_path = Path(self.config.get('storage.images_path', 'data/images'))
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        
    async def process_frame(self, frame, timestamp):
        detections = self.detection_engine.detect(frame, timestamp)
        
        if detections:
            self.logger.info(f"Found {len(detections)} rodent(s) in frame")
            
            for detection in detections:
                image_path = self.detection_engine.save_detection_image(
                    frame, [detection], self.images_path
                )
                
                self.database.save_detection(detection, image_path)
                
                alert_event = await self.alert_engine.process_detection(
                    detection, image_path
                )
                
                if alert_event:
                    await self.send_alert(alert_event)
    
    async def send_alert(self, alert_event):
        self.logger.info(f"Sending alert for {alert_event.detection.class_name}")
        
        results = await self.notification_service.send_alert(alert_event)
        
        success = any(results.values())
        if success:
            self.alert_engine.mark_alert_sent(alert_event)
            self.database.update_alert_status(alert_event.detection.id)
            self.logger.info(f"Alert sent successfully: {results}")
        else:
            self.logger.error(f"Failed to send alert: {results}")
    
    async def alert_processor(self):
        while self.running:
            alert_event = await self.alert_engine.get_pending_alert()
            if alert_event:
                await self.send_alert(alert_event)
            else:
                await asyncio.sleep(0.1)
    
    async def maintenance_task(self):
        while self.running:
            await asyncio.sleep(3600)  # Run every hour
            
            try:
                retention_days = self.config.get('storage.retention_days', 30)
                self.database.cleanup_old_records(retention_days)
                self.alert_engine.cleanup_old_alerts(retention_days)
            except Exception as e:
                self.logger.error(f"Maintenance task failed: {e}")
    
    async def health_check(self):
        check_interval = self.config.get('system.health_check_interval', 300)
        
        while self.running:
            await asyncio.sleep(check_interval)
            
            stats = {
                'alert_stats': self.alert_engine.get_alert_statistics(),
                'db_stats': self.database.get_detection_statistics(),
                'notification_channels': self.notification_service.get_active_channels()
            }
            
            self.logger.info(f"Health check: {stats}")
    
    def run(self):
        self.running = True
        self.logger.info("Starting Rodent Detection System")
        
        startup_delay = self.config.get('system.startup_delay', 10)
        if startup_delay > 0:
            self.logger.info(f"Waiting {startup_delay} seconds before starting...")
            time.sleep(startup_delay)
        
        try:
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"System error: {e}", exc_info=True)
        finally:
            self.logger.info("Rodent Detection System stopped")
    
    async def _run_async(self):
        tasks = [
            asyncio.create_task(self._frame_processor()),
            asyncio.create_task(self.alert_processor()),
            asyncio.create_task(self.maintenance_task()),
            asyncio.create_task(self.health_check())
        ]
        
        await asyncio.gather(*tasks)
    
    async def _frame_processor(self):
        self.logger.info("Starting frame processor")
        
        for frame, timestamp in self.video_pipeline.get_frames():
            if not self.running:
                break
            
            try:
                await self.process_frame(frame, timestamp)
            except Exception as e:
                self.logger.error(f"Error processing frame: {e}")
            
            await asyncio.sleep(0.01)


def main():
    system = RodentDetectionSystem()
    system.run()


if __name__ == "__main__":
    main()