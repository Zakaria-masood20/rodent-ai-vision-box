import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from twilio.rest import Client
import requests
import base64
from src.alert_engine import AlertEvent
from src.logger import logger


class NotificationChannel(ABC):
    @abstractmethod
    async def send_alert(self, alert_event: AlertEvent) -> bool:
        pass


class SMSNotification(NotificationChannel):
    def __init__(self, config: Dict):
        self.account_sid = config.get('account_sid')
        self.auth_token = config.get('auth_token')
        self.from_number = config.get('from_number')
        self.to_numbers = config.get('to_numbers', [])
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            logger.warning("Twilio credentials not configured")
            self.client = None
    
    async def send_alert(self, alert_event: AlertEvent) -> bool:
        if not self.client:
            logger.error("SMS client not initialized")
            return False
        
        try:
            detection = alert_event.detection
            message_body = (
                f"🚨 RODENT ALERT! {detection.class_name.replace('_', ' ').title()} "
                f"detected at {detection.datetime.strftime('%I:%M %p')} "
                f"with {detection.confidence:.0%} confidence."
            )
            
            success = True
            for to_number in self.to_numbers:
                try:
                    message = self.client.messages.create(
                        body=message_body,
                        from_=self.from_number,
                        to=to_number
                    )
                    logger.info(f"SMS sent to {to_number}, SID: {message.sid}")
                except Exception as e:
                    logger.error(f"Failed to send SMS to {to_number}: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"SMS notification failed: {e}")
            return False


class EmailNotification(NotificationChannel):
    def __init__(self, config: Dict):
        self.smtp_server = config.get('smtp_server')
        self.smtp_port = config.get('smtp_port', 587)
        self.use_tls = config.get('use_tls', True)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email')
        self.to_emails = config.get('to_emails', [])
    
    async def send_alert(self, alert_event: AlertEvent) -> bool:
        try:
            detection = alert_event.detection
            
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"Rodent Alert: {detection.class_name.replace('_', ' ').title()} Detected"
            
            body = f"""
            <html>
                <body>
                    <h2>🚨 Rodent Detection Alert</h2>
                    <p><strong>Type:</strong> {detection.class_name.replace('_', ' ').title()}</p>
                    <p><strong>Time:</strong> {detection.datetime.strftime('%Y-%m-%d %I:%M:%S %p')}</p>
                    <p><strong>Confidence:</strong> {detection.confidence:.0%}</p>
                    <p><strong>Location:</strong> Camera Feed</p>
                    <hr>
                    <p>Please check the attached image for visual confirmation.</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            if Path(alert_event.image_path).exists():
                with open(alert_event.image_path, 'rb') as f:
                    img_data = f.read()
                image = MIMEImage(img_data)
                image.add_header('Content-Disposition', 'attachment', filename=Path(alert_event.image_path).name)
                msg.attach(image)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {', '.join(self.to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False


class PushNotification(NotificationChannel):
    def __init__(self, config: Dict):
        self.provider = config.get('provider', 'pushover')
        self.api_token = config.get('api_token')
        self.user_key = config.get('user_key')
    
    async def send_alert(self, alert_event: AlertEvent) -> bool:
        if self.provider == 'pushover':
            return await self._send_pushover(alert_event)
        else:
            logger.error(f"Unsupported push provider: {self.provider}")
            return False
    
    async def _send_pushover(self, alert_event: AlertEvent) -> bool:
        try:
            detection = alert_event.detection
            
            data = {
                'token': self.api_token,
                'user': self.user_key,
                'title': f"Rodent Alert: {detection.class_name.replace('_', ' ').title()}",
                'message': (
                    f"Detected at {detection.datetime.strftime('%I:%M %p')} "
                    f"with {detection.confidence:.0%} confidence."
                ),
                'priority': 1,
                'timestamp': int(detection.timestamp)
            }
            
            if Path(alert_event.image_path).exists():
                with open(alert_event.image_path, 'rb') as f:
                    files = {'attachment': f}
                    response = requests.post(
                        'https://api.pushover.net/1/messages.json',
                        data=data,
                        files=files
                    )
            else:
                response = requests.post(
                    'https://api.pushover.net/1/messages.json',
                    data=data
                )
            
            if response.status_code == 200:
                logger.info("Push notification sent successfully")
                return True
            else:
                logger.error(f"Push notification failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Push notification failed: {e}")
            return False


class EmailJSNotification(NotificationChannel):
    def __init__(self, config: Dict):
        self.service_id = config.get('service_id')
        self.template_id = config.get('template_id')
        self.public_key = config.get('public_key')
        self.private_key = config.get('private_key')
        self.to_email = config.get('to_email')
        self.from_name = config.get('from_name', 'Rodent Detection System')
        
        if not all([self.service_id, self.template_id, self.public_key]):
            logger.warning("EmailJS credentials not fully configured")
    
    async def send_alert(self, alert_event: AlertEvent) -> bool:
        if not all([self.service_id, self.template_id, self.public_key]):
            logger.error("EmailJS not properly configured")
            return False
        
        try:
            detection = alert_event.detection
            
            # Prepare image data if available
            image_data = None
            if Path(alert_event.image_path).exists():
                with open(alert_event.image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Prepare template parameters
            template_params = {
                'to_email': self.to_email,
                'from_name': self.from_name,
                'rodent_type': detection.class_name.replace('_', ' ').title(),
                'detection_time': detection.datetime.strftime('%Y-%m-%d %I:%M:%S %p'),
                'confidence': f"{detection.confidence:.0%}",
                'message': f"🚨 RODENT ALERT! {detection.class_name.replace('_', ' ').title()} detected at {detection.datetime.strftime('%I:%M %p')} with {detection.confidence:.0%} confidence.",
                'image_data': image_data if image_data else '',
                'image_name': Path(alert_event.image_path).name if image_data else ''
            }
            
            # Send via EmailJS API with browser-like headers
            headers = {
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            data = {
                'service_id': self.service_id,
                'template_id': self.template_id,
                'user_id': self.public_key,
                'template_params': template_params
            }
            
            # Add private key if available (for additional security)
            if self.private_key:
                data['accessToken'] = self.private_key
            
            response = requests.post(
                'https://api.emailjs.com/api/v1.0/email/send',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                logger.info(f"EmailJS notification sent successfully to {self.to_email}")
                return True
            else:
                logger.error(f"EmailJS notification failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"EmailJS notification failed: {e}")
            return False


class NotificationService:
    def __init__(self, config):
        self.config = config
        self.channels = self._initialize_channels()
        
    def _initialize_channels(self) -> Dict[str, NotificationChannel]:
        channels = {}
        enabled_channels = self.config.get('alerts.enabled_channels', [])
        
        if 'sms' in enabled_channels:
            sms_config = self.config.get('notifications.sms', {})
            if sms_config:
                channels['sms'] = SMSNotification(sms_config)
                logger.info("SMS notification channel initialized")
        
        if 'email' in enabled_channels:
            email_config = self.config.get('notifications.email', {})
            if email_config:
                channels['email'] = EmailNotification(email_config)
                logger.info("Email notification channel initialized")
        
        if 'emailjs' in enabled_channels:
            emailjs_config = self.config.get('notifications.emailjs', {})
            if emailjs_config:
                channels['emailjs'] = EmailJSNotification(emailjs_config)
                logger.info("EmailJS notification channel initialized")
        
        if 'push' in enabled_channels:
            push_config = self.config.get('notifications.push', {})
            if push_config:
                channels['push'] = PushNotification(push_config)
                logger.info("Push notification channel initialized")
        
        return channels
    
    async def send_alert(self, alert_event: AlertEvent) -> Dict[str, bool]:
        results = {}
        
        for channel_name, channel in self.channels.items():
            try:
                logger.info(f"Sending alert via {channel_name}")
                success = await channel.send_alert(alert_event)
                results[channel_name] = success
            except Exception as e:
                logger.error(f"Error sending alert via {channel_name}: {e}")
                results[channel_name] = False
        
        return results
    
    def get_active_channels(self) -> List[str]:
        return list(self.channels.keys())