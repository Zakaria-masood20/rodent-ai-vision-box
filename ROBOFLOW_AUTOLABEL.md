# 🚀 Fast Auto-Annotation with Roboflow (FREE)

## Why Roboflow?
- **FREE tier**: 10,000 images/month
- **Auto-Label**: AI-powered automatic annotation
- **Label Assist**: Suggests bounding boxes as you work
- **Smart Tools**: Copy annotations, bulk operations
- **Export**: Direct YOLOv8 format export

## Step-by-Step Guide (15 minutes setup, 1-2 hours annotation)

### 1. Create Account (2 min)
Go to https://app.roboflow.com and sign up (free)

### 2. Create Project (2 min)
- Click "Create New Project"
- Project Type: **Object Detection**
- Project Name: "Rodent Species Detection"

### 3. Configure Classes (1 min)
Add these exact class names:
- `roof_rat`
- `norway_rat`
- `mouse`

### 4. Upload Images (5 min)
- Click "Upload"
- Select ALL images from: `data/final_annotation_project/images/`
- Or drag and drop the entire folder
- Wait for upload (823 images)

### 5. Use Auto-Label (5 min)
Roboflow will offer to auto-label your images:
- Click "Auto-Label" 
- It will use AI to detect animals
- You just need to correct the species classification

### 6. Quick Annotation Strategy

#### Phase 1: Auto-Label Review (30 min)
- Roboflow's AI will detect most animals
- You just need to:
  1. Adjust boxes to fit properly
  2. Change class from generic to specific species
  3. Delete false positives

#### Phase 2: Manual Touchup (30-60 min)
- Fix missed detections
- Correct species misclassifications
- Use Label Assist for suggestions

### 7. Roboflow Shortcuts
- **Space**: Next image
- **Enter**: Save and next
- **B**: Draw box
- **1,2,3**: Select class (roof_rat, norway_rat, mouse)
- **Delete**: Remove box
- **Cmd/Ctrl+C/V**: Copy/paste annotations

### 8. Export Dataset
Once annotated:
1. Click "Generate" → "Generate New Version"
2. Preprocessing: Auto-Orient, Resize to 640x640
3. Augmentations: Optional (adds more training data)
4. Click "Generate"
5. Export → Download → YOLOv8 format

## 🎯 Time Comparison

| Method | Setup | Annotation | Total |
|--------|-------|------------|-------|
| Manual LabelImg | 5 min | 4-6 hours | 4-6 hours |
| Roboflow Auto | 15 min | 1-2 hours | 1.5-2.5 hours |

## 💡 Pro Tips

1. **Batch Operations**: Select multiple images with similar animals
2. **Template Mode**: Copy annotations from one image to similar ones
3. **Keyboard Only**: Much faster than clicking
4. **Review Mode**: Quickly scan through at the end

## 🆓 Free Tier Limits
- 10,000 source images/month
- 3 projects
- Unlimited exports
- All features included

## Alternative: Roboflow API Upload

If you prefer command line:
```bash
pip install roboflow

python3 << 'EOF'
from roboflow import Roboflow
import os

# Get your API key from: https://app.roboflow.com/settings/api
rf = Roboflow(api_key="YOUR_API_KEY_HERE")

# Create project
project = rf.workspace().project("rodent-detection")

# Upload images
images_dir = "data/final_annotation_project/images"
for img in os.listdir(images_dir):
    if img.endswith('.jpg'):
        project.upload(os.path.join(images_dir, img))
        print(f"Uploaded {img}")
EOF
```

## 🏁 Start Now!

1. Open https://app.roboflow.com
2. Upload your 823 images
3. Use Auto-Label
4. Export in YOLOv8 format
5. Train your model!

**Estimated time: 1.5-2 hours total** (vs 4-6 hours manual)