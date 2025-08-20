#!/bin/bash

echo "=== YOLOv5 Rodent Model Download ==="

MODEL_DIR="../models"
mkdir -p $MODEL_DIR

# Option 1: Download pre-trained YOLOv5s model (generic)
echo "Downloading YOLOv5s model..."
wget -O $MODEL_DIR/yolov5s.pt https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt

echo ""
echo "=== Model downloaded to $MODEL_DIR ==="
echo ""
echo "NOTE: This is a generic YOLOv5s model."
echo "For best results, you should train a custom model on rodent images."
echo ""
echo "To train a custom model:"
echo "1. Collect rodent images (Roof Rats, Norway Rats, Mice)"
echo "2. Label them using Roboflow or CVAT"
echo "3. Train using YOLOv5 training scripts"
echo "4. Replace the model in $MODEL_DIR"