import cv2
import os
import time
import ffmpeg
from pathlib import Path
from typing import Generator, Optional, Tuple, List
from abc import ABC, abstractmethod
import numpy as np
from datetime import datetime, timedelta
import subprocess
from src.logger import logger


class VideoSource(ABC):
    @abstractmethod
    def get_frames(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        pass


class WyzeSDCardSource(VideoSource):
    def __init__(self, mount_path: str, frame_skip: int = 30):
        self.mount_path = Path(mount_path)
        self.frame_skip = frame_skip
        self.processed_files = set()
        self.watch_interval = 10  # seconds between checking for new files
        
    def find_video_files(self) -> List[Path]:
        """Find video files in Wyze SD card structure"""
        video_extensions = ['.mp4', '.avi', '.mov']
        video_files = []
        
        if not self.mount_path.exists():
            logger.warning(f"Mount path {self.mount_path} does not exist")
            # Try to mount if not mounted
            self._try_mount_sd_card()
            return video_files
        
        # Wyze typically stores videos in record/YYYYMMDD/HH/ structure
        record_dir = self.mount_path / 'record'
        if record_dir.exists():
            for ext in video_extensions:
                video_files.extend(record_dir.rglob(f'*{ext}'))
        else:
            # Fallback to searching entire mount
            for ext in video_extensions:
                video_files.extend(self.mount_path.rglob(f'*{ext}'))
        
        # Sort by modification time (newest first)
        video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return video_files
    
    def _try_mount_sd_card(self):
        """Attempt to mount SD card if not mounted"""
        try:
            # Check if SD card device exists
            result = subprocess.run(['lsblk', '-o', 'NAME,MOUNTPOINT'], 
                                  capture_output=True, text=True)
            
            # Look for unmounted SD card (typically mmcblk or sd)
            for line in result.stdout.split('\n'):
                if ('mmcblk' in line or 'sd' in line) and self.mount_path.name not in line:
                    device = line.split()[0].strip('├─└')
                    if device:
                        logger.info(f"Attempting to mount {device} to {self.mount_path}")
                        subprocess.run(['sudo', 'mount', f'/dev/{device}', str(self.mount_path)])
                        break
        except Exception as e:
            logger.error(f"Failed to auto-mount SD card: {e}")
    
    def get_frames(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        while True:
            video_files = self.find_video_files()
            new_files = [f for f in video_files if f not in self.processed_files]
            
            if not new_files:
                logger.debug("No new video files found, waiting...")
                time.sleep(10)
                continue
            
            for video_file in new_files:
                logger.info(f"Processing video file: {video_file}")
                yield from self._process_video_file(video_file)
                self.processed_files.add(video_file)
    
    def _process_video_file(self, video_path: Path) -> Generator[Tuple[np.ndarray, float], None, None]:
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            logger.error(f"Failed to open video file: {video_path}")
            return
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % self.frame_skip == 0:
                timestamp = time.time()
                yield frame, timestamp
            
            frame_count += 1
        
        cap.release()
        logger.info(f"Finished processing {video_path}, extracted {frame_count // self.frame_skip} frames")


class WyzeRTSPSource(VideoSource):
    def __init__(self, rtsp_url: str, frame_rate: int = 1):
        self.rtsp_url = rtsp_url
        self.frame_rate = frame_rate
        self.reconnect_delay = 5
        
    def get_frames(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        while True:
            try:
                yield from self._stream_frames()
            except Exception as e:
                logger.error(f"RTSP stream error: {e}")
                logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)
    
    def _stream_frames(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            raise Exception(f"Failed to open RTSP stream: {self.rtsp_url}")
        
        logger.info(f"Connected to RTSP stream: {self.rtsp_url}")
        
        last_frame_time = 0
        frame_interval = 1.0 / self.frame_rate
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame from RTSP stream")
                break
            
            current_time = time.time()
            if current_time - last_frame_time >= frame_interval:
                yield frame, current_time
                last_frame_time = current_time
        
        cap.release()


class WyzeBridgeSource(VideoSource):
    """Source for Wyze Bridge Docker container streaming"""
    def __init__(self, bridge_url: str, camera_name: str, frame_rate: int = 1):
        self.bridge_url = bridge_url
        self.camera_name = camera_name
        self.frame_rate = frame_rate
        self.reconnect_delay = 5
        
        # Wyze Bridge typically provides streams at these endpoints
        self.stream_url = f"{bridge_url}/api/sse/{camera_name}"
        self.rtsp_url = f"rtsp://localhost:8554/{camera_name}"
        
    def get_frames(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        while True:
            try:
                # Try RTSP first
                yield from self._stream_rtsp()
            except Exception as e:
                logger.error(f"Wyze Bridge stream error: {e}")
                logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)
    
    def _stream_rtsp(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        """Stream from Wyze Bridge RTSP endpoint"""
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            raise Exception(f"Failed to open Wyze Bridge stream: {self.rtsp_url}")
        
        logger.info(f"Connected to Wyze Bridge for camera: {self.camera_name}")
        
        last_frame_time = 0
        frame_interval = 1.0 / self.frame_rate
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame from Wyze Bridge")
                break
            
            current_time = time.time()
            if current_time - last_frame_time >= frame_interval:
                yield frame, current_time
                last_frame_time = current_time
        
        cap.release()


class LocalVideoSource(VideoSource):
    def __init__(self, video_path: str, frame_skip: int = 30):
        self.video_path = video_path
        self.frame_skip = frame_skip
        
    def get_frames(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            logger.error(f"Failed to open video file: {self.video_path}")
            return
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % self.frame_skip == 0:
                timestamp = time.time()
                yield frame, timestamp
            
            frame_count += 1
        
        cap.release()


class VideoIngestionPipeline:
    def __init__(self, config):
        self.config = config
        self.source = self._create_source()
        self.resize_width = config.get('video.resize_width', 640)
        self.resize_height = config.get('video.resize_height', 480)
        
    def _create_source(self) -> VideoSource:
        source_type = self.config.get('camera.source', 'sd_card')
        
        if source_type == 'sd_card':
            mount_path = self.config.get('camera.sd_mount_path', '/mnt/wyze_sd')
            frame_skip = self.config.get('video.frame_skip', 30)
            logger.info(f"Using SD Card source at {mount_path}")
            return WyzeSDCardSource(mount_path, frame_skip)
        
        elif source_type == 'rtsp':
            rtsp_url = self.config.get('camera.rtsp_url')
            if not rtsp_url:
                # Try to get from environment
                import os
                rtsp_url = os.getenv('RTSP_URL')
            frame_rate = self.config.get('video.frame_rate', 1)
            logger.info(f"Using RTSP source: {rtsp_url}")
            return WyzeRTSPSource(rtsp_url, frame_rate)
        
        elif source_type == 'wyze_bridge':
            bridge_url = self.config.get('camera.bridge_url', 'http://localhost:8888')
            camera_name = self.config.get('camera.camera_name', 'wyze_cam')
            frame_rate = self.config.get('video.frame_rate', 1)
            logger.info(f"Using Wyze Bridge for camera: {camera_name}")
            return WyzeBridgeSource(bridge_url, camera_name, frame_rate)
        
        elif source_type == 'local':
            video_path = self.config.get('camera.local_video_path')
            frame_skip = self.config.get('video.frame_skip', 30)
            logger.info(f"Using local video: {video_path}")
            return LocalVideoSource(video_path, frame_skip)
        
        else:
            raise ValueError(f"Unknown video source type: {source_type}")
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        if frame.shape[:2] != (self.resize_height, self.resize_width):
            frame = cv2.resize(frame, (self.resize_width, self.resize_height))
        
        return frame
    
    def get_frames(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        for frame, timestamp in self.source.get_frames():
            preprocessed_frame = self.preprocess_frame(frame)
            yield preprocessed_frame, timestamp