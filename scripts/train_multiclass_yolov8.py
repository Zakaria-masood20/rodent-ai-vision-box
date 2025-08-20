#!/usr/bin/env python3
"""
YOLOv8 training script for multi-class rodent detection
Trains model to detect and classify: roof_rat, norway_rat, mouse
"""

import os
import yaml
import torch
from pathlib import Path
from ultralytics import YOLO
import argparse
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


class MultiClassRodentTrainer:
    def __init__(self, data_yaml: str, model_name: str = 'yolov8n.pt'):
        """
        Initialize trainer for multi-class rodent detection
        
        Args:
            data_yaml: Path to dataset configuration file
            model_name: YOLOv8 model variant (n/s/m/l/x)
        """
        self.data_yaml = Path(data_yaml)
        self.model_name = model_name
        self.output_dir = Path('runs/rodent_multiclass') / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create model
        if Path(model_name).exists():
            print(f"Loading existing model: {model_name}")
            self.model = YOLO(model_name)
        else:
            print(f"Loading pretrained YOLOv8 model: {model_name}")
            self.model = YOLO(model_name)
    
    def train(self, epochs: int = 100, batch_size: int = 16, imgsz: int = 640):
        """
        Train the YOLOv8 model for multi-class detection
        """
        # Training parameters optimized for rodent detection
        results = self.model.train(
            data=str(self.data_yaml),
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            project=str(self.output_dir.parent),
            name=self.output_dir.name,
            
            # Optimization parameters
            optimizer='AdamW',
            lr0=0.01,  # Initial learning rate
            lrf=0.01,  # Final learning rate factor
            momentum=0.937,
            weight_decay=0.0005,
            
            # Augmentation parameters (important for small dataset)
            hsv_h=0.015,  # Hue augmentation
            hsv_s=0.7,    # Saturation augmentation
            hsv_v=0.4,    # Value augmentation
            degrees=10.0,  # Rotation augmentation
            translate=0.1,  # Translation augmentation
            scale=0.5,     # Scale augmentation
            shear=0.0,     # Shear augmentation
            perspective=0.0,  # Perspective augmentation
            flipud=0.5,    # Vertical flip probability
            fliplr=0.5,    # Horizontal flip probability
            mosaic=1.0,    # Mosaic augmentation
            mixup=0.2,     # Mixup augmentation
            copy_paste=0.1,  # Copy-paste augmentation
            
            # Training settings
            patience=50,   # Early stopping patience
            save=True,
            save_period=10,  # Save checkpoint every N epochs
            cache=True,    # Cache images for faster training
            device='0' if torch.cuda.is_available() else 'cpu',
            workers=8,
            amp=True,      # Automatic mixed precision
            
            # Validation settings
            val=True,
            plots=True,
            
            # Class weights for imbalanced dataset
            # Adjust based on your class distribution
            cls_weight=[1.0, 1.2, 0.8],  # roof_rat, norway_rat, mouse
        )
        
        return results
    
    def evaluate(self, model_path: str = None):
        """
        Evaluate the trained model on test set
        """
        if model_path:
            model = YOLO(model_path)
        else:
            model = self.model
        
        # Run validation
        results = model.val(
            data=str(self.data_yaml),
            batch=16,
            imgsz=640,
            plots=True,
            save_json=True,
        )
        
        # Print per-class metrics
        print("\n=== Per-Class Performance ===")
        class_names = ['roof_rat', 'norway_rat', 'mouse']
        
        if hasattr(results, 'box'):
            metrics = results.box
            for i, class_name in enumerate(class_names):
                if i < len(metrics.ap50):
                    print(f"{class_name}:")
                    print(f"  AP50: {metrics.ap50[i]:.3f}")
                    print(f"  AP50-95: {metrics.ap[i]:.3f}")
        
        return results
    
    def predict_single_image(self, image_path: str, model_path: str = None):
        """
        Run prediction on a single image
        """
        if model_path:
            model = YOLO(model_path)
        else:
            model = self.model
        
        results = model(image_path, conf=0.5, iou=0.45)
        
        # Process results
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls)
                    conf = float(box.conf)
                    xyxy = box.xyxy[0].tolist()
                    
                    class_names = ['roof_rat', 'norway_rat', 'mouse']
                    class_name = class_names[cls] if cls < len(class_names) else f'class_{cls}'
                    
                    print(f"Detected: {class_name} (conf: {conf:.2f})")
                    print(f"  Box: {xyxy}")
        
        return results
    
    def export_model(self, format: str = 'onnx'):
        """
        Export trained model to different formats
        """
        print(f"Exporting model to {format} format...")
        
        # Find best model
        best_model = self.output_dir / 'weights' / 'best.pt'
        if not best_model.exists():
            print("No trained model found. Train the model first.")
            return None
        
        model = YOLO(str(best_model))
        
        # Export to specified format
        path = model.export(
            format=format,
            imgsz=640,
            half=False,
            dynamic=True if format == 'onnx' else False,
            simplify=True if format == 'onnx' else False,
        )
        
        print(f"Model exported to: {path}")
        return path


def create_config_update():
    """
    Create updated configuration for multi-class detection
    """
    config = {
        'detection': {
            'model_type': 'yolov8',
            'model_path': 'models/yolov8_rodent_multiclass.pt',
            'confidence_threshold': 0.5,
            'nms_threshold': 0.45,
            'classes': ['roof_rat', 'norway_rat', 'mouse'],
            'class_specific_thresholds': {
                'roof_rat': 0.55,
                'norway_rat': 0.50,
                'mouse': 0.45
            }
        },
        'training': {
            'batch_size': 16,
            'epochs': 100,
            'imgsz': 640,
            'patience': 50,
            'device': 'auto'
        }
    }
    
    config_path = Path('config/multiclass_config.yaml')
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Configuration saved to: {config_path}")
    return config_path


def main():
    parser = argparse.ArgumentParser(description='Train YOLOv8 for multi-class rodent detection')
    parser.add_argument('--data', type=str, required=True,
                        help='Path to data.yaml file')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                        help='YOLOv8 model variant or path to checkpoint')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='Batch size for training')
    parser.add_argument('--imgsz', type=int, default=640,
                        help='Image size for training')
    parser.add_argument('--evaluate-only', action='store_true',
                        help='Only evaluate existing model')
    parser.add_argument('--export', type=str, choices=['onnx', 'tensorrt', 'coreml'],
                        help='Export trained model to specified format')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = MultiClassRodentTrainer(args.data, args.model)
    
    if args.evaluate_only:
        # Evaluate existing model
        print("Evaluating model...")
        trainer.evaluate()
    else:
        # Train model
        print("Starting training...")
        print(f"Dataset: {args.data}")
        print(f"Model: {args.model}")
        print(f"Epochs: {args.epochs}")
        print(f"Batch size: {args.batch_size}")
        print(f"Image size: {args.imgsz}")
        
        results = trainer.train(
            epochs=args.epochs,
            batch_size=args.batch_size,
            imgsz=args.imgsz
        )
        
        print("\nTraining completed!")
        print(f"Results saved to: {trainer.output_dir}")
        
        # Evaluate after training
        print("\nEvaluating trained model...")
        trainer.evaluate()
        
        # Export if requested
        if args.export:
            trainer.export_model(args.export)
    
    # Create updated config
    create_config_update()


if __name__ == '__main__':
    main()