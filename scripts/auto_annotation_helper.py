#!/usr/bin/env python3
"""
Auto-annotation helper using pre-trained models and semi-automated labeling
This will generate initial annotations that you can review and correct
"""

import os
import cv2
import numpy as np
from pathlib import Path
import json
from PIL import Image
from typing import List, Dict, Tuple

class AutoAnnotator:
    def __init__(self, images_dir: str, output_dir: str):
        self.images_dir = Path(images_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Class definitions
        self.classes = {
            0: 'roof_rat',
            1: 'norway_rat', 
            2: 'mouse'
        }
        
        print("🤖 Auto-Annotation Helper")
        print("="*60)
    
    def use_pretrained_detector(self):
        """
        Use a pre-trained YOLO model to detect animals, then classify species
        """
        print("📦 This method requires ultralytics package")
        print("Install with: pip install ultralytics")
        return {}
    
    def classify_by_size(self, width: float, height: float) -> int:
        """
        Simple classification based on bounding box size
        This is a placeholder - you'll need to review and correct
        """
        area = width * height
        aspect_ratio = width / height if height > 0 else 1.0
        
        if area < 0.02:  # Very small
            return 2  # mouse
        elif area < 0.08:  # Medium
            if aspect_ratio > 1.2:  # More elongated
                return 0  # roof_rat
            else:
                return 1  # norway_rat
        else:  # Large
            return 1  # norway_rat
    
    def save_yolo_annotation(self, img_name: str, boxes: List[Dict]):
        """
        Save annotation in YOLO format
        """
        label_file = self.output_dir / f"{img_name}.txt"
        
        with open(label_file, 'w') as f:
            for box in boxes:
                line = f"{box['class_id']} {box['cx']:.6f} {box['cy']:.6f} {box['width']:.6f} {box['height']:.6f}\n"
                f.write(line)
    
    def generate_pseudo_labels(self):
        """
        Generate pseudo-labels based on folder structure
        This assumes images are already sorted by species
        """
        print("\n📝 Generating pseudo-labels from folder structure...")
        
        count = 0
        for species_name, class_id in [(v, k) for k, v in self.classes.items()]:
            # Check if images have species prefix
            species_images = list(self.images_dir.glob(f'{species_name}_*.jpg'))
            
            for img_path in species_images:
                # Create a full-image bounding box as starting point
                # You'll need to adjust these in LabelImg
                cx, cy, w, h = 0.5, 0.5, 0.8, 0.8  # Center box covering 80% of image
                
                boxes = [{
                    'class_id': class_id,
                    'cx': cx,
                    'cy': cy,
                    'width': w,
                    'height': h,
                    'confidence': 0.5
                }]
                
                self.save_yolo_annotation(img_path.stem, boxes)
                count += 1
                
                if count % 50 == 0:
                    print(f"  Generated {count} pseudo-labels...")
        
        print(f"✅ Generated {count} pseudo-labels")
        print("⚠️  These are rough estimates - you MUST review and adjust them!")
        
        return count


class RoboflowUploader:
    """
    Helper to upload images to Roboflow for easier annotation
    """
    
    @staticmethod
    def create_upload_script():
        """
        Create a script for uploading to Roboflow
        """
        script_content = """
# Roboflow Upload Instructions

## Option 1: Web Upload (Easiest)
1. Go to https://app.roboflow.com
2. Create new project (Object Detection)
3. Set classes: roof_rat, norway_rat, mouse
4. Drag and drop all images from data/final_annotation_project/images/
5. Use Roboflow's Label Assist for faster annotation

## Option 2: API Upload (Requires API Key)
```python
from roboflow import Roboflow

# Initialize with your API key
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace().project("rodent-detection")

# Upload images
import os
images_dir = "data/final_annotation_project/images"
for img_file in os.listdir(images_dir):
    if img_file.endswith('.jpg'):
        img_path = os.path.join(images_dir, img_file)
        project.upload(img_path)
```

## Option 3: Use Roboflow's Auto-Label
1. Upload 50-100 manually annotated images first
2. Train initial model in Roboflow
3. Use model to auto-label remaining images
4. Review and correct auto-labels
5. Export in YOLOv8 format
"""
        
        with open('ROBOFLOW_UPLOAD.md', 'w') as f:
            f.write(script_content)
        
        print("📄 Created ROBOFLOW_UPLOAD.md with instructions")


def create_labelimg_helper():
    """
    Create a helper script for faster LabelImg annotation
    """
    helper_content = """#!/usr/bin/env python3
'''
LabelImg Speed Helper - Keyboard shortcuts and tips
Run this alongside LabelImg for reference
'''

import time
import os

print("🎯 LabelImg Speed Annotation Helper")
print("="*60)
print()
print("KEYBOARD SHORTCUTS:")
print("  W         - Create rectangle box")
print("  D         - Next image")
print("  A         - Previous image") 
print("  Ctrl+S    - Save")
print("  Ctrl+D    - Copy current label to next image")
print("  Del       - Delete selected box")
print("  Space     - Flag image as verified")
print("  ↑↓        - Select different class")
print()
print("SPEED TIPS:")
print("1. Enable View → Auto Save Mode")
print("2. Use PascalVOC format for easier editing")
print("3. Group similar images together")
print("4. Use Ctrl+D to copy boxes between similar images")
print()
print("SPECIES QUICK REFERENCE:")
print("🐀 Roof Rat    - Tail > Body, Big ears, Pointed snout")
print("🐀 Norway Rat  - Tail < Body, Small ears, Blunt snout")
print("🐁 Mouse       - Tiny size, Huge ears, Very thin")
print()
print("Target: 10-15 seconds per image")
print("Take a break every 100 images!")
print()

# Timer
start = time.time()
input("Press Enter when you start annotating...")

try:
    while True:
        time.sleep(60)
        elapsed = int((time.time() - start) / 60)
        estimated_images = elapsed * 4  # ~15 seconds per image
        print(f"⏱️  {elapsed} minutes - Estimated {estimated_images} images done")
except KeyboardInterrupt:
    print("\\nAnnotation session ended!")
"""
    
    with open('labelimg_helper.py', 'w') as f:
        f.write(helper_content)
    
    print("📄 Created labelimg_helper.py")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-annotation helper')
    parser.add_argument('--images', type=str, 
                        default='data/final_annotation_project/images',
                        help='Images directory')
    parser.add_argument('--output', type=str,
                        default='data/final_annotation_project/labels_auto',
                        help='Output directory for annotations')
    parser.add_argument('--method', type=str, choices=['pseudo', 'pretrained', 'roboflow'],
                        default='pseudo',
                        help='Annotation method')
    
    args = parser.parse_args()
    
    if args.method == 'roboflow':
        RoboflowUploader.create_upload_script()
        print("\n✅ Created Roboflow upload instructions")
        print("Follow ROBOFLOW_UPLOAD.md to use Roboflow's annotation tools")
    else:
        annotator = AutoAnnotator(args.images, args.output)
        
        if args.method == 'pseudo':
            count = annotator.generate_pseudo_labels()
            print(f"\n✅ Generated {count} pseudo-labels")
            print("\n⚠️  IMPORTANT: These are just starting points!")
            print("You MUST review and adjust them in LabelImg:")
            print(f"\nlabelImg {args.images} data/final_annotation_project/classes.txt")
            print(f"\nThen set Save Dir to: {args.output}")
        
        elif args.method == 'pretrained':
            print("⚠️  Note: This will only work well if YOLOv8 can detect rodents")
            annotations = annotator.use_pretrained_detector()
            print(f"\n✅ Generated annotations for {len(annotations)} images")
    
    # Always create helper files
    create_labelimg_helper()
    
    print("\n" + "="*60)
    print("📋 NEXT STEPS:")
    print("="*60)
    print("1. Review auto-generated labels in LabelImg")
    print("2. Adjust bounding boxes to fit animals properly")
    print("3. Correct any misclassified species")
    print("4. Save final annotations")
    print("\nRemember: Auto-labels are just a starting point!")
    print("Human review is essential for accuracy.")


if __name__ == '__main__':
    main()