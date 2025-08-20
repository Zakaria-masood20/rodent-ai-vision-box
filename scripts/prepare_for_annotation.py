#!/usr/bin/env python3
"""
Prepare scraped images for annotation
Organizes images, removes duplicates, and creates annotation project
"""

import os
import shutil
import random
from pathlib import Path
from PIL import Image
import hashlib
import json
from typing import Dict, List
import cv2
import numpy as np


class AnnotationPreparer:
    def __init__(self, scraped_dir: str, output_dir: str):
        self.scraped_dir = Path(scraped_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create annotation directory structure
        self.images_dir = self.output_dir / 'images'
        self.images_dir.mkdir(exist_ok=True)
        
        # Class definitions
        self.classes = {
            0: 'roof_rat',
            1: 'norway_rat',
            2: 'mouse'
        }
    
    def filter_and_organize_images(self):
        """
        Filter images by quality and organize for annotation
        """
        print("Filtering and organizing images...")
        
        stats = {
            'total': 0,
            'accepted': 0,
            'rejected_size': 0,
            'rejected_quality': 0,
            'rejected_duplicate': 0
        }
        
        processed_hashes = set()
        accepted_images = []
        
        for species in ['roof_rat', 'norway_rat', 'mouse']:
            species_dir = self.scraped_dir / species
            if not species_dir.exists():
                continue
            
            class_id = list(self.classes.keys())[list(self.classes.values()).index(species)]
            
            for img_path in species_dir.glob('*.jpg'):
                stats['total'] += 1
                
                # Check for duplicates
                with open(img_path, 'rb') as f:
                    img_hash = hashlib.md5(f.read()).hexdigest()
                
                if img_hash in processed_hashes:
                    stats['rejected_duplicate'] += 1
                    continue
                
                try:
                    # Open and check image
                    img = Image.open(img_path)
                    
                    # Check minimum size
                    if img.width < 200 or img.height < 200:
                        stats['rejected_size'] += 1
                        continue
                    
                    # Check image quality (basic check)
                    img_array = np.array(img)
                    if len(img_array.shape) < 2:
                        stats['rejected_quality'] += 1
                        continue
                    
                    # Calculate basic quality metrics
                    if len(img_array.shape) == 3:
                        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                    else:
                        gray = img_array
                    
                    # Check for blur (Laplacian variance)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    if laplacian_var < 50:  # Too blurry
                        stats['rejected_quality'] += 1
                        continue
                    
                    # Image accepted
                    new_filename = f"{species}_{len(accepted_images):05d}.jpg"
                    new_path = self.images_dir / new_filename
                    
                    # Resize if too large (for faster annotation)
                    if img.width > 1920 or img.height > 1920:
                        img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
                    
                    # Save processed image
                    img.save(new_path, 'JPEG', quality=95)
                    
                    accepted_images.append({
                        'filename': new_filename,
                        'species': species,
                        'class_id': class_id,
                        'original_path': str(img_path),
                        'width': img.width,
                        'height': img.height
                    })
                    
                    processed_hashes.add(img_hash)
                    stats['accepted'] += 1
                    
                    if stats['accepted'] % 50 == 0:
                        print(f"Processed {stats['accepted']} images...")
                    
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
                    stats['rejected_quality'] += 1
        
        # Save image list
        with open(self.output_dir / 'image_list.json', 'w') as f:
            json.dump(accepted_images, f, indent=2)
        
        # Print statistics
        print("\n" + "="*50)
        print("FILTERING STATISTICS")
        print("="*50)
        print(f"Total images processed: {stats['total']}")
        print(f"Accepted: {stats['accepted']}")
        print(f"Rejected (too small): {stats['rejected_size']}")
        print(f"Rejected (quality): {stats['rejected_quality']}")
        print(f"Rejected (duplicate): {stats['rejected_duplicate']}")
        
        return accepted_images
    
    def split_dataset(self, images: List[Dict], train_ratio: float = 0.7, val_ratio: float = 0.2):
        """
        Split images into train/val/test sets
        """
        print("\nSplitting dataset...")
        
        # Group by species
        species_images = {}
        for img in images:
            species = img['species']
            if species not in species_images:
                species_images[species] = []
            species_images[species].append(img)
        
        # Split each species proportionally
        splits = {'train': [], 'val': [], 'test': []}
        
        for species, imgs in species_images.items():
            random.shuffle(imgs)
            
            n = len(imgs)
            n_train = int(n * train_ratio)
            n_val = int(n * val_ratio)
            
            splits['train'].extend(imgs[:n_train])
            splits['val'].extend(imgs[n_train:n_train + n_val])
            splits['test'].extend(imgs[n_train + n_val:])
        
        # Create split directories
        for split_name, split_images in splits.items():
            split_dir = self.output_dir / split_name
            split_dir.mkdir(exist_ok=True)
            
            # Create symlinks or copy images
            for img in split_images:
                src = self.images_dir / img['filename']
                dst = split_dir / img['filename']
                if src.exists():
                    shutil.copy2(src, dst)
        
        # Print split statistics
        print("\nDataset splits:")
        for split_name, split_images in splits.items():
            print(f"{split_name}: {len(split_images)} images")
            
            # Count per class
            class_counts = {}
            for img in split_images:
                species = img['species']
                class_counts[species] = class_counts.get(species, 0) + 1
            
            for species, count in class_counts.items():
                print(f"  - {species}: {count}")
        
        return splits
    
    def create_labelimg_project(self):
        """
        Create configuration for LabelImg annotation tool
        """
        print("\nCreating LabelImg project...")
        
        # Create classes file
        classes_file = self.output_dir / 'classes.txt'
        with open(classes_file, 'w') as f:
            for class_name in self.classes.values():
                f.write(f"{class_name}\n")
        
        # Create predefined_classes file for LabelImg
        predefined_file = self.output_dir / 'predefined_classes.txt'
        with open(predefined_file, 'w') as f:
            for class_name in self.classes.values():
                f.write(f"{class_name}\n")
        
        print(f"Classes file created: {classes_file}")
        print(f"Predefined classes file: {predefined_file}")
    
    def create_cvat_manifest(self, images: List[Dict]):
        """
        Create manifest file for CVAT annotation tool
        """
        print("\nCreating CVAT manifest...")
        
        manifest = {
            'version': '1.0',
            'type': 'images',
            'spec': {
                'name': 'Rodent Species Detection',
                'labels': [
                    {'name': 'roof_rat', 'attributes': []},
                    {'name': 'norway_rat', 'attributes': []},
                    {'name': 'mouse', 'attributes': []}
                ]
            },
            'images': []
        }
        
        for img in images:
            manifest['images'].append({
                'name': img['filename'],
                'width': img['width'],
                'height': img['height']
            })
        
        manifest_file = self.output_dir / 'cvat_manifest.json'
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"CVAT manifest created: {manifest_file}")
    
    def create_annotation_guide(self):
        """
        Create annotation guidelines document
        """
        guide_content = """# Rodent Species Annotation Guide

## Classes

### 1. roof_rat (Rattus rattus)
**Characteristics:**
- Tail LONGER than head + body combined
- Large, prominent ears
- Pointed snout
- Slender, agile build
- Dark fur (usually black or dark brown)
- Body length: 16-24 cm

**Common locations:**
- Climbing on walls, pipes, trees
- Attics, roofs, upper floors
- Ships and ports

### 2. norway_rat (Rattus norvegicus)
**Characteristics:**
- Tail SHORTER than head + body combined
- Small ears
- Blunt snout
- Bulky, heavy build
- Brown or gray fur
- Body length: 20-25 cm

**Common locations:**
- Ground level, sewers
- Basements, burrows
- Near water sources

### 3. mouse (Mus musculus)
**Characteristics:**
- Much smaller size (7-10 cm body)
- Large ears relative to body size
- Pointed snout
- Thin tail (about same length as body)
- Light brown or gray fur

**Common locations:**
- Indoor spaces
- Small hiding spots
- Kitchen areas

## Annotation Guidelines

1. **Draw tight bounding boxes** around the entire animal
2. **Include the tail** in the bounding box
3. **Label based on visible features**, not location
4. **If unsure between rat species**, look at:
   - Tail length relative to body
   - Ear size
   - Body shape (slender vs bulky)
5. **Skip images** that are:
   - Too blurry to identify features
   - Showing only partial animal
   - Ambiguous species

## Quality Checks

- [ ] Each bounding box contains one animal
- [ ] Box is tight but includes whole animal
- [ ] Correct species based on features
- [ ] No duplicate boxes on same animal

## Tools

### Using LabelImg:
1. Open LabelImg
2. Open Dir -> Select 'images' folder
3. Change Save Dir -> Select 'labels' folder
4. View -> Auto Save mode
5. Press 'W' to draw box
6. Select correct class
7. Press 'D' for next image

### Using Roboflow:
1. Upload images to project
2. Set classes: roof_rat, norway_rat, mouse
3. Draw bounding boxes
4. Review annotations before export

### Using CVAT:
1. Create new task
2. Upload images and manifest
3. Annotate with bounding boxes
4. Export in YOLO format
"""
        
        guide_file = self.output_dir / 'ANNOTATION_GUIDE.md'
        with open(guide_file, 'w') as f:
            f.write(guide_content)
        
        print(f"Annotation guide created: {guide_file}")
    
    def prepare_all(self):
        """
        Run all preparation steps
        """
        print("="*60)
        print("PREPARING IMAGES FOR ANNOTATION")
        print("="*60)
        
        # Filter and organize images
        images = self.filter_and_organize_images()
        
        if not images:
            print("\nNo images found! Please run the scraping script first.")
            return
        
        # Split dataset
        self.split_dataset(images)
        
        # Create annotation configs
        self.create_labelimg_project()
        self.create_cvat_manifest(images)
        self.create_annotation_guide()
        
        print("\n" + "="*60)
        print("ANNOTATION PREPARATION COMPLETE")
        print("="*60)
        print(f"\nOutput directory: {self.output_dir.absolute()}")
        print("\nNext steps:")
        print("1. Review images in 'images' folder")
        print("2. Read ANNOTATION_GUIDE.md")
        print("3. Choose annotation tool:")
        print("   - LabelImg (local, simple)")
        print("   - Roboflow (online, collaborative)")
        print("   - CVAT (advanced, team features)")
        print("4. Start annotating with bounding boxes")
        print("5. Export annotations in YOLO format")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare scraped images for annotation')
    parser.add_argument('--scraped-dir', type=str, default='data/scraped_images',
                        help='Directory with scraped images')
    parser.add_argument('--output', type=str, default='data/annotation_project',
                        help='Output directory for annotation project')
    parser.add_argument('--train-ratio', type=float, default=0.7,
                        help='Training set ratio')
    parser.add_argument('--val-ratio', type=float, default=0.2,
                        help='Validation set ratio')
    
    args = parser.parse_args()
    
    preparer = AnnotationPreparer(args.scraped_dir, args.output)
    preparer.prepare_all()


if __name__ == '__main__':
    main()