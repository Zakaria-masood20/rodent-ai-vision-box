#!/usr/bin/env python3
"""
Fast bulk downloader - gets 500+ images quickly
Combines existing images and downloads more efficiently
"""

import os
import shutil
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import hashlib
from PIL import Image
import io
import time

class FastBulkDownloader:
    def __init__(self):
        self.output_dir = Path("data/combined_dataset")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create species directories
        for species in ['roof_rat', 'norway_rat', 'mouse']:
            (self.output_dir / species).mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RodentDataset/1.0)'
        })
        
    def combine_existing_images(self):
        """Combine all existing downloaded images"""
        print("📂 Combining existing images...")
        
        existing_dirs = [
            "data/scraped_images",
            "data/bulk_scraped",
            "data/annotation_project/images"
        ]
        
        counts = {'roof_rat': 0, 'norway_rat': 0, 'mouse': 0}
        seen_hashes = set()
        
        for dir_path in existing_dirs:
            if not Path(dir_path).exists():
                continue
                
            # Check for species subdirectories
            for species in ['roof_rat', 'norway_rat', 'mouse']:
                species_dir = Path(dir_path) / species
                if species_dir.exists():
                    for img_path in species_dir.glob('*.jpg'):
                        # Check for duplicates
                        with open(img_path, 'rb') as f:
                            img_hash = hashlib.md5(f.read()).hexdigest()
                        
                        if img_hash not in seen_hashes:
                            new_name = f"{species}_{counts[species]:05d}.jpg"
                            shutil.copy2(img_path, self.output_dir / species / new_name)
                            counts[species] += 1
                            seen_hashes.add(img_hash)
                
                # Also check root directory for species-prefixed files
                for img_path in Path(dir_path).glob(f'{species}*.jpg'):
                    with open(img_path, 'rb') as f:
                        img_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if img_hash not in seen_hashes:
                        new_name = f"{species}_{counts[species]:05d}.jpg"
                        shutil.copy2(img_path, self.output_dir / species / new_name)
                        counts[species] += 1
                        seen_hashes.add(img_hash)
        
        print(f"✅ Combined existing images:")
        for species, count in counts.items():
            print(f"  {species}: {count} images")
        
        return counts, seen_hashes
    
    def download_more_images(self, species: str, current_count: int, target: int, seen_hashes: set):
        """Download additional images for a species"""
        needed = target - current_count
        if needed <= 0:
            return 0
        
        print(f"\n⬇️  Downloading {needed} more {species} images...")
        
        # Use multiple search terms for variety
        search_terms = {
            'roof_rat': ['Rattus rattus', 'black rat', 'roof rat'],
            'norway_rat': ['Rattus norvegicus', 'brown rat', 'norway rat'],
            'mouse': ['Mus musculus', 'house mouse', 'laboratory mouse']
        }
        
        urls = []
        
        # Get URLs from iNaturalist
        for term in search_terms.get(species, []):
            params = {
                'taxon_name': term,
                'quality_grade': 'research',
                'has[]': 'photos',
                'per_page': 200,
                'order_by': 'random'  # Random for variety
            }
            
            try:
                response = self.session.get(
                    "https://api.inaturalist.org/v1/observations",
                    params=params,
                    timeout=30
                )
                data = response.json()
                
                for obs in data.get('results', []):
                    photos = obs.get('photos', [])
                    if photos:
                        # Get medium size for speed
                        url = photos[0]['url'].replace('square', 'medium')
                        urls.append(url)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"  Error fetching URLs: {e}")
        
        # Download images in parallel
        def download_single(url_idx):
            url, idx = url_idx
            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    # Check hash
                    img_hash = hashlib.md5(resp.content).hexdigest()
                    if img_hash in seen_hashes:
                        return None
                    
                    # Validate image
                    img = Image.open(io.BytesIO(resp.content))
                    if img.width >= 150 and img.height >= 150:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Resize if too large
                        if img.width > 800 or img.height > 800:
                            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                        
                        filename = f"{species}_{current_count + idx:05d}.jpg"
                        filepath = self.output_dir / species / filename
                        img.save(filepath, 'JPEG', quality=85)
                        
                        seen_hashes.add(img_hash)
                        return filename
            except:
                pass
            return None
        
        # Download with thread pool
        downloaded = 0
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(download_single, (url, i)) 
                      for i, url in enumerate(urls[:needed*2])]
            
            for future in as_completed(futures):
                if future.result():
                    downloaded += 1
                    if downloaded >= needed:
                        break
                    if downloaded % 20 == 0:
                        print(f"  Downloaded {downloaded}/{needed}")
        
        print(f"  ✅ Downloaded {downloaded} new {species} images")
        return downloaded
    
    def get_dataset(self, target_per_species: int = 170):
        """Get complete dataset with target images per species"""
        print("🚀 Fast Bulk Dataset Builder")
        print("="*60)
        print(f"Target: {target_per_species} images per species")
        print(f"Total target: {target_per_species * 3} images")
        print("="*60)
        
        # Step 1: Combine existing images
        counts, seen_hashes = self.combine_existing_images()
        
        # Step 2: Download more if needed
        for species in ['roof_rat', 'norway_rat', 'mouse']:
            current = counts[species]
            if current < target_per_species:
                added = self.download_more_images(
                    species, current, target_per_species, seen_hashes
                )
                counts[species] += added
        
        # Step 3: Final summary
        print("\n" + "="*60)
        print("📊 FINAL DATASET")
        print("="*60)
        
        total = 0
        for species in ['roof_rat', 'norway_rat', 'mouse']:
            count = len(list((self.output_dir / species).glob('*.jpg')))
            print(f"{species:15} : {count:4} images")
            total += count
        
        print("-"*30)
        print(f"{'TOTAL':15} : {total:4} images")
        print(f"\n📁 Output: {self.output_dir.absolute()}")
        
        # Save metadata
        metadata = {
            'total_images': total,
            'species_counts': counts,
            'target_per_species': target_per_species
        }
        
        with open(self.output_dir / 'dataset_info.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return total >= 500


def main():
    downloader = FastBulkDownloader()
    
    # Try to get 170+ images per species (500+ total)
    success = downloader.get_dataset(target_per_species=170)
    
    if success:
        print("\n✅ Successfully built 500+ image dataset!")
        print("\nNext steps:")
        print("1. Run: python3 scripts/prepare_for_annotation.py --scraped-dir data/combined_dataset")
        print("2. Start annotating with LabelImg")
    else:
        print("\n⚠️  Couldn't reach 500 images, but got as many as possible")
        print("You may need to:")
        print("1. Find additional image sources")
        print("2. Use data augmentation during training")


if __name__ == '__main__':
    main()