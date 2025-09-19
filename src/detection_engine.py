import torch
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import cv2
from datetime import datetime
from ultralytics import YOLO
from src.logger import logger


class Detection:
    def __init__(self, class_name: str, confidence: float, bbox: Tuple[int, int, int, int], timestamp: float):
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.timestamp = timestamp
        self.datetime = datetime.fromtimestamp(timestamp)
    
    def to_dict(self) -> Dict:
        return {
            'class_name': self.class_name,
            'confidence': float(self.confidence),
            'bbox': self.bbox,
            'timestamp': self.timestamp,
            'datetime': self.datetime.isoformat()
        }


class RodentDetectionEngine:
    def __init__(self, config):
        self.config = config
        self.model_path = config.get('detection.model_path', 'models/best.pt')
        self.confidence_threshold = config.get('detection.confidence_threshold', 0.25)  # Lower for better detection
        self.nms_threshold = config.get('detection.nms_threshold', 0.45)
        self.target_classes = config.get('detection.classes', ['norway_rat', 'roof_rat'])
        self.device = self._get_device()
        self.use_onnx = self._should_use_onnx()
        self.model = self._load_model()
        
        # Model performance notes
        self.class_performance = {
            'norway_rat': 0.771,  # 77.1% mAP
            'roof_rat': 0.150     # 15.0% mAP - poor accuracy
        }
        
    def _get_device(self) -> str:
        if torch.cuda.is_available():
            logger.info("CUDA available, using GPU")
            return 'cuda'
        else:
            logger.info("CUDA not available, using CPU")
            return 'cpu'
    
    def _should_use_onnx(self) -> bool:
        """Check if ONNX model should be used based on config or environment"""
        import os
        use_onnx = os.getenv('USE_ONNX', 'false').lower() == 'true'
        
        # Check if ONNX model exists
        onnx_path = self.model_path.replace('.pt', '.onnx')
        if use_onnx and Path(onnx_path).exists():
            logger.info(f"ONNX model found at {onnx_path}, will use ONNX for inference")
            return True
        
        # On Raspberry Pi, prefer ONNX
        try:
            with open('/proc/device-tree/model', 'r') as f:
                if 'raspberry pi' in f.read().lower():
                    if Path(onnx_path).exists():
                        logger.info("Running on Raspberry Pi, using ONNX for better performance")
                        return True
        except:
            pass
        
        return False
    
    def _load_model(self):
        try:
            if self.use_onnx:
                # Use ONNX model for better performance on edge devices
                onnx_path = self.model_path.replace('.pt', '.onnx')
                logger.info(f"Loading ONNX model from {onnx_path}")
                model = YOLO(onnx_path, task='detect')
            elif Path(self.model_path).exists():
                logger.info(f"Loading custom YOLOv8 model from {self.model_path}")
                model = YOLO(self.model_path)
            else:
                logger.warning(f"Model not found at {self.model_path}, using pretrained YOLOv8n")
                model = YOLO('yolov8n.pt')
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(self, frame: np.ndarray, timestamp: float) -> List[Detection]:
        try:
            # Run YOLOv8 inference
            results = self.model(frame, conf=self.confidence_threshold, iou=self.nms_threshold, device=self.device)
            
            detections = []
            
            # Process YOLOv8 results
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        # Get class name
                        class_id = int(box.cls)
                        # Map class IDs to our trained model classes
                        class_names = {0: 'norway_rat', 1: 'roof_rat'}
                        class_name = class_names.get(class_id, 'unknown_rat')
                        confidence = float(box.conf)
                        
                        # Always include rat detections (both classes are rats)
                        # Get bbox coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        bbox = (int(x1), int(y1), int(x2), int(y2))
                        
                        detection = Detection(
                            class_name=class_name,
                            confidence=confidence,
                            bbox=bbox,
                            timestamp=timestamp
                        )
                        
                        detections.append(detection)
                        
                        # Add performance warning for roof rats
                        if class_name == 'roof_rat':
                            logger.info(f"Detected {class_name} with confidence {confidence:.2f} (Note: Low accuracy class)")
                        else:
                            logger.info(f"Detected {class_name} with confidence {confidence:.2f}")
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []
    
    def _is_rodent(self, class_name: str) -> bool:
        rodent_keywords = ['rat', 'mouse', 'rodent'] + self.target_classes
        return any(keyword in class_name.lower() for keyword in rodent_keywords)
    
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        annotated_frame = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            
            color = self._get_class_color(detection.class_name)
            
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            cv2.rectangle(
                annotated_frame,
                (x1, y1 - label_size[1] - 4),
                (x1 + label_size[0], y1),
                color,
                -1
            )
            
            cv2.putText(
                annotated_frame,
                label,
                (x1, y1 - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
        
        timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            annotated_frame,
            timestamp_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        return annotated_frame
    
    def _get_class_color(self, class_name: str) -> Tuple[int, int, int]:
        colors = {
            'roof_rat': (255, 0, 0),      # Red
            'norway_rat': (0, 0, 255),    # Blue
            'mouse': (0, 255, 0),         # Green
            'default': (255, 255, 0)      # Yellow
        }
        return colors.get(class_name, colors['default'])
    
    def save_detection_image(self, frame: np.ndarray, detections: List[Detection], save_path: Path) -> str:
        annotated_frame = self.draw_detections(frame, detections)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detection_{timestamp}.jpg"
        filepath = save_path / filename
        
        save_path.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(filepath), annotated_frame)
        
        logger.info(f"Saved detection image to {filepath}")
        return str(filepath)