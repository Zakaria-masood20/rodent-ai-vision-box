#!/usr/bin/env python3
"""
Create CSV files for Roboflow upload with class labels
"""

import os
import csv
from pathlib import Path
import json

def create_roboflow_csv():
    # Paths
    images_dir = Path("data/final_annotation_project/images")
    output_dir = Path("data/final_annotation_project")
    
    # Create main CSV with image-level labels (for classification)
    csv_path = output_dir / "roboflow_classes.csv"
    
    # Also create a CSV with bounding boxes from pseudo-labels
    csv_bbox_path = output_dir / "roboflow_annotations.csv"
    
    print("📝 Creating Roboflow CSV files...")
    
    # 1. Create classification CSV (image-level labels)
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'label'])  # Header
        
        count = {'roof_rat': 0, 'norway_rat': 0, 'mouse': 0}
        
        for img_path in sorted(images_dir.glob('*.jpg')):
            filename = img_path.name
            
            # Extract species from filename
            if filename.startswith('roof_rat'):
                label = 'roof_rat'
            elif filename.startswith('norway_rat'):
                label = 'norway_rat'
            elif filename.startswith('mouse'):
                label = 'mouse'
            else:
                # Try to infer from filename
                if 'roof' in filename.lower() or 'rattus_rattus' in filename.lower():
                    label = 'roof_rat'
                elif 'norway' in filename.lower() or 'rattus_norvegicus' in filename.lower():
                    label = 'norway_rat'
                elif 'mouse' in filename.lower() or 'mus' in filename.lower():
                    label = 'mouse'
                else:
                    label = 'unknown'
            
            writer.writerow([filename, label])
            if label in count:
                count[label] += 1
    
    print(f"✅ Created classification CSV: {csv_path}")
    print(f"   Images per class:")
    for species, cnt in count.items():
        print(f"   - {species}: {cnt}")
    
    # 2. Create annotation CSV with bounding boxes
    labels_dir = output_dir / "labels_auto"
    
    with open(csv_bbox_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Roboflow format for object detection
        writer.writerow(['filename', 'label', 'xmin', 'ymin', 'xmax', 'ymax'])
        
        bbox_count = 0
        
        for label_file in labels_dir.glob('*.txt'):
            img_name = label_file.stem + '.jpg'
            img_path = images_dir / img_name
            
            if not img_path.exists():
                continue
            
            # Get image dimensions (assuming 640x640 or we'll use normalized)
            # For Roboflow, we can use normalized coordinates (0-1)
            
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    cx, cy, w, h = map(float, parts[1:5])
                    
                    # Convert from YOLO format (center, width, height) to box format
                    xmin = cx - w/2
                    ymin = cy - h/2
                    xmax = cx + w/2
                    ymax = cy + h/2
                    
                    # Ensure bounds
                    xmin = max(0, min(1, xmin))
                    ymin = max(0, min(1, ymin))
                    xmax = max(0, min(1, xmax))
                    ymax = max(0, min(1, ymax))
                    
                    # Map class ID to label
                    labels = {0: 'roof_rat', 1: 'norway_rat', 2: 'mouse'}
                    label = labels.get(class_id, 'unknown')
                    
                    writer.writerow([img_name, label, xmin, ymin, xmax, ymax])
                    bbox_count += 1
    
    print(f"✅ Created annotation CSV: {csv_bbox_path}")
    print(f"   Total bounding boxes: {bbox_count}")
    
    # 3. Create a simple class definition file
    classes_json = output_dir / "roboflow_classes.json"
    classes_data = {
        "classes": [
            {"id": 0, "name": "roof_rat"},
            {"id": 1, "name": "norway_rat"},
            {"id": 2, "name": "mouse"}
        ],
        "info": {
            "description": "Rodent species detection dataset",
            "species": {
                "roof_rat": "Rattus rattus - Black rat, Ship rat",
                "norway_rat": "Rattus norvegicus - Brown rat, Sewer rat",
                "mouse": "Mus musculus - House mouse"
            }
        }
    }
    
    with open(classes_json, 'w') as f:
        json.dump(classes_data, f, indent=2)
    
    print(f"✅ Created class definitions: {classes_json}")
    
    # 4. Create upload instructions
    instructions = """
# 📤 Roboflow Upload Instructions

## Files Created:
1. **roboflow_classes.csv** - Image-level labels (for quick classification)
2. **roboflow_annotations.csv** - Bounding box annotations (pre-labels)
3. **roboflow_classes.json** - Class definitions

## Upload Methods:

### Method 1: Web Upload with CSV (Recommended)
1. Go to https://app.roboflow.com
2. Create new Object Detection project
3. Add classes: roof_rat, norway_rat, mouse
4. Click "Upload" → "Select Files"
5. Select all images from: data/final_annotation_project/images/
6. After upload, click "Import Annotations"
7. Upload: roboflow_annotations.csv
8. Select format: "CSV"
9. Map columns:
   - filename → Image Name
   - label → Class Name
   - xmin, ymin, xmax, ymax → Bounding Box

### Method 2: API Upload with Annotations
```python
from roboflow import Roboflow
import pandas as pd
import os

# Initialize
rf = Roboflow(api_key="YOUR_API_KEY")
workspace = rf.workspace()
project = workspace.project("rodent-detection")

# Read annotations
df = pd.read_csv('data/final_annotation_project/roboflow_annotations.csv')

# Upload images with annotations
images_dir = 'data/final_annotation_project/images'

for img_file in os.listdir(images_dir):
    if img_file.endswith('.jpg'):
        img_path = os.path.join(images_dir, img_file)
        
        # Get annotations for this image
        img_annotations = df[df['filename'] == img_file]
        
        # Format annotations for Roboflow
        annotations = []
        for _, row in img_annotations.iterrows():
            annotations.append({
                'x': row['xmin'] * 100,  # Convert to percentage
                'y': row['ymin'] * 100,
                'width': (row['xmax'] - row['xmin']) * 100,
                'height': (row['ymax'] - row['ymin']) * 100,
                'class': row['label']
            })
        
        # Upload with annotations
        project.upload(
            image_path=img_path,
            annotation=annotations if annotations else None
        )
```

### Method 3: Direct Drag & Drop
1. Simply drag all 823 images to Roboflow
2. Use Label Assist for auto-detection
3. Correct species classifications manually

## Tips:
- The CSV contains pre-labels based on filename patterns
- Bounding boxes are rough estimates (centered 80% boxes)
- You'll need to adjust boxes to fit actual animals
- Use Roboflow's Smart Polygon tool for precise labeling
"""
    
    instructions_path = output_dir / "ROBOFLOW_UPLOAD_GUIDE.txt"
    with open(instructions_path, 'w') as f:
        f.write(instructions)
    
    print(f"\n✅ Created upload guide: {instructions_path}")
    print("\n📋 Summary:")
    print(f"   - Total images: {len(list(images_dir.glob('*.jpg')))}")
    print(f"   - CSV files ready for Roboflow import")
    print(f"   - Pre-labels will save annotation time")
    print("\n🚀 Next: Upload to Roboflow and review/adjust annotations")


if __name__ == '__main__':
    create_roboflow_csv()