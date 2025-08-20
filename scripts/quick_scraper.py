#!/usr/bin/env python3
"""
Quick scraper focused on iNaturalist for faster results
"""

import os
import requests
import hashlib
from pathlib import Path
from PIL import Image
import io
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class QuickRodentScraper:
    def __init__(self, output_dir: str = "data/scraped_images"):
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RodentDatasetBuilder/1.0)'
        })
        
        self.species_info = {
            'roof_rat': 'Rattus rattus',
            'norway_rat': 'Rattus norvegicus', 
            'mouse': 'Mus musculus'
        }
        
        # Create directories
        for species in self.species_info.keys():
            (self.output_dir / species).mkdir(parents=True, exist_ok=True)
    
    def download_image(self, args):
        """Download a single image (for parallel processing)"""
        url, species, idx = args
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Validate image
                img = Image.open(io.BytesIO(response.content))
                if img.width >= 200 and img.height >= 200:
                    # Save image
                    filename = f"{species}_{idx:04d}.jpg"
                    filepath = self.output_dir / species / filename
                    
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    img.save(filepath, 'JPEG', quality=90)
                    return f"✓ {filename}"
        except Exception as e:
            return f"✗ Failed {species}_{idx:04d}: {str(e)[:30]}"
        return None
    
    def scrape_species(self, species: str, count: int = 50):
        """Scrape images for a specific species"""
        print(f"\n📷 Scraping {species} ({self.species_info[species]})...")
        
        # Get observations from iNaturalist
        url = "https://api.inaturalist.org/v1/observations"
        params = {
            'taxon_name': self.species_info[species],
            'quality_grade': 'research',
            'has[]': 'photos',
            'per_page': count * 2,  # Get extra in case some fail
            'order': 'votes'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            data = response.json()
            observations = data.get('results', [])
            
            # Collect image URLs
            image_urls = []
            for obs in observations:
                photos = obs.get('photos', [])
                if photos:
                    # Get medium size for faster download
                    photo_url = photos[0]['url'].replace('square', 'medium')
                    image_urls.append(photo_url)
            
            print(f"  Found {len(image_urls)} images, downloading up to {count}...")
            
            # Download images in parallel
            download_tasks = [(url, species, i) for i, url in enumerate(image_urls[:count])]
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.download_image, task) for task in download_tasks]
                
                downloaded = 0
                for future in as_completed(futures):
                    result = future.result()
                    if result and result.startswith('✓'):
                        downloaded += 1
                        if downloaded % 10 == 0:
                            print(f"  Downloaded {downloaded}/{count}...")
            
            print(f"  ✅ Downloaded {downloaded} images for {species}")
            return downloaded
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return 0
    
    def scrape_all(self, images_per_species: int = 50):
        """Scrape all species"""
        print("🚀 Quick Rodent Image Scraper")
        print("=" * 50)
        
        total = 0
        for species in self.species_info.keys():
            count = self.scrape_species(species, images_per_species)
            total += count
            time.sleep(2)  # Be nice to the API
        
        print("\n" + "=" * 50)
        print(f"✅ Total images downloaded: {total}")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        
        # Save metadata
        metadata = {
            'species': list(self.species_info.keys()),
            'source': 'iNaturalist',
            'total_images': total,
            'images_per_species': images_per_species
        }
        
        with open(self.output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Quick rodent image scraper')
    parser.add_argument('--count', type=int, default=50,
                        help='Images per species to download')
    args = parser.parse_args()
    
    scraper = QuickRodentScraper()
    scraper.scrape_all(args.count)