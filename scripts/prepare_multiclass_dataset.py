#!/usr/bin/env python3
"""
Script to prepare dataset for multi-class rodent classification
Converts single-class rat detection to multi-class (roof_rat, norway_rat, mouse)
"""

import os
import yaml
import shutil
from pathlib import Path
import cv2
import numpy as np
from typing import Dict, List, Tuple

class MultiClassDatasetPreparer:
    def __init__(self, source_path: str, output_path: str):
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        
        # Define class mappings
        self.class_names = ['roof_rat', 'norway_rat', 'mouse']
        self.class_ids = {name: idx for idx, name in enumerate(self.class_names)}
        
    def create_directory_structure(self):
        """Create YOLOv8 directory structure"""
        for split in ['train', 'valid', 'test']:
            (self.output_path / split / 'images').mkdir(parents=True, exist_ok=True)
            (self.output_path / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    def convert_polygon_to_bbox(self, polygon_coords: List[float]) -> Tuple[float, float, float, float]:
        """Convert polygon format to bounding box format"""
        # Polygon coords are pairs of x,y values
        x_coords = polygon_coords[::2]
        y_coords = polygon_coords[1::2]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # Convert to YOLO format (center_x, center_y, width, height)
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        width = x_max - x_min
        height = y_max - y_min
        
        return center_x, center_y, width, height
    
    def classify_by_size(self, width: float, height: float, image_path: str = None) -> int:
        """
        Classify rodent type based on bounding box size and aspect ratio
        This is a heuristic approach - replace with actual classification logic
        """
        area = width * height
        aspect_ratio = width / height if height > 0 else 1.0
        
        # Heuristic thresholds (adjust based on your data)
        if area < 0.02:  # Small size
            return self.class_ids['mouse']
        elif area < 0.08:  # Medium size
            if aspect_ratio > 1.2:  # More elongated
                return self.class_ids['roof_rat']
            else:
                return self.class_ids['norway_rat']
        else:  # Large size
            return self.class_ids['norway_rat']
    
    def process_labels(self):
        """Process and convert label files"""
        for split in ['train', 'valid', 'test']:
            label_dir = self.source_path / split / 'labels'
            if not label_dir.exists():
                continue
                
            for label_file in label_dir.glob('*.txt'):
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                new_labels = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    
                    # Original format: class_id followed by polygon coords
                    class_id = int(parts[0])
                    coords = [float(x) for x in parts[1:]]
                    
                    # Convert polygon to bbox
                    if len(coords) >= 4:
                        if len(coords) > 5:  # Polygon format
                            cx, cy, w, h = self.convert_polygon_to_bbox(coords)
                        else:  # Already bbox format
                            cx, cy, w, h = coords[1:5]
                        
                        # Classify species based on size (or other features)
                        species_id = self.classify_by_size(w, h)
                        
                        # Write in YOLO format
                        new_labels.append(f"{species_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
                
                # Save converted labels
                output_file = self.output_path / split / 'labels' / label_file.name
                with open(output_file, 'w') as f:
                    f.writelines(new_labels)
    
    def copy_images(self):
        """Copy image files to new structure"""
        for split in ['train', 'valid', 'test']:
            image_dir = self.source_path / split / 'images'
            if not image_dir.exists():
                continue
                
            for image_file in image_dir.glob('*'):
                if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    dest = self.output_path / split / 'images' / image_file.name
                    shutil.copy2(image_file, dest)
    
    def create_data_yaml(self):
        """Create data.yaml configuration file"""
        data_config = {
            'path': str(self.output_path.absolute()),
            'train': 'train/images',
            'val': 'valid/images',
            'test': 'test/images',
            'nc': len(self.class_names),
            'names': self.class_names,
            'description': 'Multi-class rodent detection dataset (roof_rat, norway_rat, mouse)'
        }
        
        with open(self.output_path / 'data.yaml', 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
    
    def prepare_dataset(self):
        """Main method to prepare the dataset"""
        print("Creating directory structure...")
        self.create_directory_structure()
        
        print("Copying images...")
        self.copy_images()
        
        print("Converting labels to multi-class format...")
        self.process_labels()
        
        print("Creating data.yaml...")
        self.create_data_yaml()
        
        print(f"Dataset prepared at: {self.output_path}")
        print(f"Classes: {self.class_names}")
        
        # Print statistics
        for split in ['train', 'valid', 'test']:
            image_count = len(list((self.output_path / split / 'images').glob('*')))
            label_count = len(list((self.output_path / split / 'labels').glob('*.txt')))
            print(f"{split}: {image_count} images, {label_count} labels")


class SpeciesClassifier:
    """
    Advanced classifier for species identification
    Can be enhanced with a CNN model for better accuracy
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        # Load pre-trained classifier if available
        self.model = None
        
    def extract_features(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict:
        """Extract features from rodent image for classification"""
        x, y, w, h = bbox
        roi = image[y:y+h, x:x+w]
        
        features = {
            'aspect_ratio': w / h if h > 0 else 1.0,
            'area_ratio': (w * h) / (image.shape[0] * image.shape[1]),
            'mean_color': np.mean(roi, axis=(0, 1)) if roi.size > 0 else [0, 0, 0],
            'std_color': np.std(roi, axis=(0, 1)) if roi.size > 0 else [0, 0, 0],
        }
        
        # Add shape features
        if roi.size > 0:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                features['contour_area'] = cv2.contourArea(largest_contour) / (w * h)
                features['perimeter'] = cv2.arcLength(largest_contour, True) / (2 * (w + h))
        
        return features
    
    def classify_species(self, features: Dict) -> str:
        """
        Classify rodent species based on extracted features
        This is a placeholder - implement with actual ML model
        """
        # Simple rule-based classification (replace with ML model)
        aspect_ratio = features.get('aspect_ratio', 1.0)
        area_ratio = features.get('area_ratio', 0.05)
        
        if area_ratio < 0.02:
            return 'mouse'
        elif aspect_ratio > 1.3 and area_ratio < 0.06:
            return 'roof_rat'
        else:
            return 'norway_rat'


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare multi-class rodent dataset')
    parser.add_argument('--source', type=str, required=True,
                        help='Path to source dataset (e.g., "rat detection.v3i.yolov8")')
    parser.add_argument('--output', type=str, required=True,
                        help='Path for output multi-class dataset')
    parser.add_argument('--manual-labeling', action='store_true',
                        help='Enable manual labeling mode for species classification')
    
    args = parser.parse_args()
    
    preparer = MultiClassDatasetPreparer(args.source, args.output)
    preparer.prepare_dataset()
    
    if args.manual_labeling:
        print("\n=== Manual Labeling Mode ===")
        print("To properly classify species, you need to:")
        print("1. Use a labeling tool like LabelImg or Roboflow")
        print("2. Review each image and update the class labels")
        print("3. Classes: 0=roof_rat, 1=norway_rat, 2=mouse")
        print("\nAlternatively, collect a pre-labeled multi-class dataset")


if __name__ == '__main__':
    main()