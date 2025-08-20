# 🎯 Annotation Workflow for 823 Images

## ✅ Dataset Ready!

You now have **823 high-quality images** ready for annotation:
- **Roof Rat**: 226 images
- **Norway Rat**: 323 images  
- **Mouse**: 274 images

Split into:
- **Train**: 575 images (70%)
- **Validation**: 163 images (20%)
- **Test**: 85 images (10%)

## 🚀 Efficient Annotation Strategy

### Option 1: LabelImg (Local, Free) - RECOMMENDED
**Time estimate: 4-6 hours total**

Start LabelImg:
```bash
source venv/bin/activate
labelImg data/final_annotation_project/images data/final_annotation_project/classes.txt
```

**Speed Tips:**
1. Enable Auto-save mode (View → Auto Save)
2. Use keyboard shortcuts:
   - `W` - Draw box
   - `D` - Next image
   - `A` - Previous image
   - `Ctrl+S` - Save
3. Set a rhythm: Draw box → Select class → Next
4. Take a 5-minute break every 100 images

### Option 2: Roboflow (Online, Collaborative)
**Best for: Team annotation or if you want AI-assisted labeling**

1. Create account at https://roboflow.com
2. Create new project (Object Detection)
3. Upload images from `data/final_annotation_project/images/`
4. Use Roboflow's AI-assist to speed up annotation
5. Export in YOLOv8 format when done

### Option 3: CVAT (Professional)
**Best for: Large teams or complex annotations**

1. Install CVAT locally or use cloud version
2. Upload images and `cvat_manifest.json`
3. Use auto-annotation features
4. Export in YOLO format

## 📊 Annotation Plan

### Day 1 (2-3 hours)
- Annotate 400 images
- Focus on clear, well-lit images first
- Get familiar with species differences

### Day 2 (2-3 hours)  
- Annotate remaining 423 images
- Review and fix any mistakes from Day 1

## 🔍 Quick Species Guide

| Feature | Roof Rat | Norway Rat | Mouse |
|---------|----------|------------|-------|
| **Tail** | Longer than body | Shorter than body | Equal to body |
| **Ears** | Large | Small | Very large |
| **Snout** | Pointed | Blunt | Pointed |
| **Size** | Medium | Large | Small |
| **Build** | Slender | Bulky | Tiny |

## ⚡ Pro Tips for Speed

1. **Batch Similar Images**: Group by lighting/angle
2. **Use Templates**: Copy boxes from similar images
3. **Keyboard Only**: Minimize mouse usage
4. **Quality Check**: Review 10% randomly after completion
5. **Difficult Images**: Skip ambiguous ones (mark for review)

## 📈 Progress Tracking

Create a simple tracker:
```
□ Images 1-100     (30 min)
□ Images 101-200   (30 min)
□ Images 201-300   (30 min)
□ Images 301-400   (30 min)
□ Images 401-500   (30 min)
□ Images 501-600   (30 min)
□ Images 601-700   (30 min)
□ Images 701-823   (30 min)
```

## 🎯 After Annotation

### 1. Verify Annotations
```bash
# Check annotation statistics
python3 scripts/verify_annotations.py --path data/final_annotation_project
```

### 2. Create YOLOv8 Data Config
Create `data/final_annotation_project/data.yaml`:
```yaml
path: /Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/rodent_detection/data/final_annotation_project
train: train
val: val
test: test

nc: 3
names: ['roof_rat', 'norway_rat', 'mouse']
```

### 3. Train Your Model
```bash
# Install YOLOv8
pip install ultralytics

# Train model
python3 scripts/train_multiclass_yolov8.py \
    --data data/final_annotation_project/data.yaml \
    --model yolov8n.pt \
    --epochs 100 \
    --batch-size 16
```

## 💡 Annotation Best Practices

1. **Consistency is Key**: Same tightness for all boxes
2. **Include Entire Animal**: Don't cut off tails/ears
3. **One Box Per Animal**: Even if overlapping
4. **Skip Poor Quality**: Blurry or partial animals
5. **Document Uncertainties**: Note image numbers if unsure

## 🏁 Expected Outcome

After annotation, you'll have:
- 823 annotated images
- ~2000-3000 bounding boxes
- Ready-to-train YOLOv8 dataset
- Model accuracy potential: 85-95% mAP

## ⏱️ Time Investment

- **Annotation**: 4-6 hours
- **Training**: 2-3 hours
- **Total**: Less than 1 day of work

Ready to start? Launch LabelImg and begin with the first batch!