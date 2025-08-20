# 📤 Roboflow CSV Upload Guide

## ✅ CSV Files Ready!

### Files Created:
1. **`roboflow_simple.csv`** - Simple format (RECOMMENDED)
   - 823 entries with image names and class labels
   - Format: `image,label`

2. **`roboflow_classes.csv`** - Detailed format
   - Same as above with headers: `filename,label`

3. **`roboflow_annotations.csv`** - With bounding boxes
   - Pre-generated boxes (center 80% of image)
   - Format: `filename,label,xmin,ymin,xmax,ymax`

## 📊 Dataset Summary:
- **Total Images:** 823
- **Roof Rat:** 226 images
- **Norway Rat:** 323 images
- **Mouse:** 274 images

## 🚀 Upload Instructions:

### Step 1: Create Roboflow Project
1. Go to https://app.roboflow.com
2. Click "Create New Project"
3. Select "Object Detection"
4. Name: "Rodent Species Detection"

### Step 2: Configure Classes
Add these exact class names:
- `roof_rat`
- `norway_rat`
- `mouse`

### Step 3: Upload Images + CSV

#### Method A: Web Upload (Easiest)
1. Click "Upload" in Roboflow
2. Select "Upload Folder"
3. Choose: `data/final_annotation_project/images/`
4. Wait for upload to complete
5. Click "Add Annotations" → "Upload Annotations"
6. Select: `data/final_annotation_project/roboflow_simple.csv`
7. Map columns:
   - `image` → Image Filename
   - `label` → Class Label

#### Method B: With Pre-labels (Bounding Boxes)
1. Upload images as above
2. Instead use: `roboflow_annotations.csv`
3. Map columns:
   - `filename` → Image Filename
   - `label` → Class Label
   - `xmin,ymin,xmax,ymax` → Bounding Box (normalized)

### Step 4: Review & Adjust
- CSV provides class labels (which species)
- You need to draw bounding boxes around each animal
- Use Roboflow's Label Assist for faster annotation

## 💡 Tips:
1. The CSV tells Roboflow which species each image contains
2. You still need to draw boxes around the animals
3. Use keyboard shortcuts:
   - `B` - Draw box
   - `1,2,3` - Select class
   - `Enter` - Next image

## 📁 File Locations:
```
data/final_annotation_project/
├── images/                  ← Upload this folder
├── roboflow_simple.csv      ← Upload this CSV
├── roboflow_classes.csv     ← Alternative CSV
└── roboflow_annotations.csv ← CSV with rough boxes
```

## ⚡ Quick Command:
If uploading via API:
```python
# pip install roboflow
from roboflow import Roboflow
import pandas as pd

rf = Roboflow(api_key="YOUR_KEY")
project = rf.workspace().project("rodent-detection")

# Read CSV
df = pd.read_csv('data/final_annotation_project/roboflow_simple.csv')

# Upload with labels
for _, row in df.iterrows():
    img_path = f"data/final_annotation_project/images/{row['image']}"
    project.upload(img_path, tag=row['label'])
```

## 🎯 Expected Result:
- 823 images uploaded with species labels
- Ready for bounding box annotation
- Use Label Assist for faster boxing
- Export in YOLOv8 format when done

---
**Files are in:** `data/final_annotation_project/`