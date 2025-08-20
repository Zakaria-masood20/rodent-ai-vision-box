#!/usr/bin/env python3
"""
Bulk scraper for 500+ rodent images from multiple sources
Optimized for speed with parallel downloads
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
from datetime import datetime
import random

class BulkRodentScraper:
    def __init__(self, output_dir: str = "data/bulk_scraped"):
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        
        # Rotate user agents to avoid blocking
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        self.species_info = {
            'roof_rat': {
                'scientific': 'Rattus rattus',
                'search_terms': ['Rattus rattus', 'roof rat', 'black rat', 'ship rat'],
                'inaturalist_taxon_id': 46264
            },
            'norway_rat': {
                'scientific': 'Rattus norvegicus',
                'search_terms': ['Rattus norvegicus', 'norway rat', 'brown rat', 'sewer rat'],
                'inaturalist_taxon_id': 46265
            },
            'mouse': {
                'scientific': 'Mus musculus',
                'search_terms': ['Mus musculus', 'house mouse', 'domestic mouse'],
                'inaturalist_taxon_id': 46273
            }
        }
        
        # Create directories
        for species in self.species_info.keys():
            (self.output_dir / species).mkdir(parents=True, exist_ok=True)
        
        self.downloaded_hashes = set()
        self.stats = {'downloaded': 0, 'failed': 0, 'duplicate': 0}
    
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def download_image_batch(self, args):
        """Download a single image (optimized for parallel processing)"""
        url, species, idx, size = args
        
        # Skip if we already have enough for this species
        species_dir = self.output_dir / species
        existing = len(list(species_dir.glob('*.jpg')))
        if existing >= 200:  # Max 200 per species
            return None
        
        try:
            headers = {'User-Agent': self.get_random_user_agent()}
            response = requests.get(url, timeout=8, headers=headers)
            
            if response.status_code == 200:
                # Quick hash check for duplicates
                img_hash = hashlib.md5(response.content).hexdigest()
                if img_hash in self.downloaded_hashes:
                    self.stats['duplicate'] += 1
                    return None
                
                # Validate image
                img = Image.open(io.BytesIO(response.content))
                
                # Size requirements based on parameter
                min_size = 150 if size == 'medium' else 200
                if img.width < min_size or img.height < min_size:
                    return None
                
                # Convert and save
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                filename = f"{species}_{idx:05d}_{img_hash[:8]}.jpg"
                filepath = species_dir / filename
                
                # Resize if too large (save space and processing time)
                if img.width > 1024 or img.height > 1024:
                    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                
                img.save(filepath, 'JPEG', quality=85)
                
                self.downloaded_hashes.add(img_hash)
                self.stats['downloaded'] += 1
                
                return f"✓ {filename}"
                
        except Exception as e:
            self.stats['failed'] += 1
            return None
    
    def scrape_inaturalist_bulk(self, species: str, target_count: int = 200):
        """Scrape from iNaturalist with pagination"""
        print(f"\n🔍 Scraping iNaturalist for {species} (target: {target_count} images)")
        
        taxon_id = self.species_info[species]['inaturalist_taxon_id']
        base_url = "https://api.inaturalist.org/v1/observations"
        
        all_urls = []
        page = 1
        per_page = 200
        
        while len(all_urls) < target_count * 2:  # Get extra URLs as some will fail
            params = {
                'taxon_id': taxon_id,
                'quality_grade': 'research',
                'has[]': 'photos',
                'per_page': per_page,
                'page': page,
                'order_by': 'votes',
                'photos': 'true'
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=30)
                data = response.json()
                observations = data.get('results', [])
                
                if not observations:
                    break
                
                for obs in observations:
                    photos = obs.get('photos', [])
                    for photo in photos[:2]:  # Get up to 2 photos per observation
                        # Use medium size for faster downloads
                        photo_url = photo['url'].replace('square', 'medium')
                        all_urls.append(photo_url)
                
                print(f"  Page {page}: Found {len(observations)} observations")
                page += 1
                
                if page > 10:  # Limit pages to avoid too many API calls
                    break
                    
                time.sleep(0.5)  # Be nice to the API
                
            except Exception as e:
                print(f"  Error on page {page}: {e}")
                break
        
        return all_urls[:target_count * 2]
    
    def scrape_gbif_bulk(self, species: str, target_count: int = 100):
        """Scrape from GBIF"""
        print(f"\n🔍 Scraping GBIF for {species}")
        
        scientific_name = self.species_info[species]['scientific']
        base_url = "https://api.gbif.org/v1/occurrence/search"
        
        all_urls = []
        offset = 0
        
        while len(all_urls) < target_count * 2:
            params = {
                'scientificName': scientific_name,
                'mediaType': 'StillImage',
                'limit': 300,
                'offset': offset
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=30)
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                for occurrence in results:
                    media = occurrence.get('media', [])
                    for medium in media[:1]:
                        image_url = medium.get('identifier')
                        if image_url and image_url.startswith('http'):
                            all_urls.append(image_url)
                
                offset += 300
                if offset > 1000:  # Limit to avoid too many requests
                    break
                    
            except Exception as e:
                print(f"  Error: {e}")
                break
        
        return all_urls
    
    def scrape_all_sources(self, images_per_species: int = 200):
        """Scrape from all sources in parallel"""
        print("\n🚀 Bulk Rodent Image Scraper")
        print("=" * 60)
        print(f"Target: {images_per_species} images per species")
        print(f"Total target: {images_per_species * 3} images")
        print("=" * 60)
        
        for species in self.species_info.keys():
            print(f"\n{'='*60}")
            print(f"📷 Processing {species.upper()}")
            print(f"{'='*60}")
            
            # Check existing images
            species_dir = self.output_dir / species
            existing = len(list(species_dir.glob('*.jpg')))
            if existing >= images_per_species:
                print(f"✅ Already have {existing} images for {species}")
                continue
            
            needed = images_per_species - existing
            print(f"📊 Have {existing}, need {needed} more")
            
            # Collect URLs from multiple sources
            all_urls = []
            
            # iNaturalist (primary source)
            inaturalist_urls = self.scrape_inaturalist_bulk(species, needed)
            all_urls.extend(inaturalist_urls)
            print(f"  Collected {len(inaturalist_urls)} iNaturalist URLs")
            
            # GBIF (secondary source)
            if len(all_urls) < needed * 1.5:
                gbif_urls = self.scrape_gbif_bulk(species, needed // 2)
                all_urls.extend(gbif_urls)
                print(f"  Collected {len(gbif_urls)} GBIF URLs")
            
            # Download in parallel
            print(f"\n⬇️  Downloading {len(all_urls)} images for {species}...")
            
            download_tasks = [
                (url, species, i, 'medium' if i < needed else 'large') 
                for i, url in enumerate(all_urls)
            ]
            
            # Use ThreadPoolExecutor for parallel downloads
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(self.download_image_batch, task) 
                          for task in download_tasks]
                
                completed = 0
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        completed += 1
                        if completed % 20 == 0:
                            current_count = len(list(species_dir.glob('*.jpg')))
                            print(f"  Progress: {current_count}/{images_per_species} images")
                        
                        # Stop if we have enough
                        if len(list(species_dir.glob('*.jpg'))) >= images_per_species:
                            break
            
            # Final count
            final_count = len(list(species_dir.glob('*.jpg')))
            print(f"✅ {species}: {final_count} total images")
        
        self.print_summary()
    
    def print_summary(self):
        """Print final summary"""
        print("\n" + "="*60)
        print("📊 SCRAPING SUMMARY")
        print("="*60)
        
        total = 0
        for species in self.species_info.keys():
            species_dir = self.output_dir / species
            count = len(list(species_dir.glob('*.jpg')))
            print(f"{species:15} : {count:4} images")
            total += count
        
        print("-"*30)
        print(f"{'TOTAL':15} : {total:4} images")
        print(f"\nStats:")
        print(f"  Downloaded: {self.stats['downloaded']}")
        print(f"  Duplicates skipped: {self.stats['duplicate']}")
        print(f"  Failed: {self.stats['failed']}")
        print(f"\n📁 Output: {self.output_dir.absolute()}")
        
        # Save metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'total_images': total,
            'species_counts': {
                species: len(list((self.output_dir / species).glob('*.jpg')))
                for species in self.species_info.keys()
            },
            'stats': self.stats
        }
        
        with open(self.output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk scrape 500+ rodent images')
    parser.add_argument('--images-per-species', type=int, default=200,
                        help='Target images per species (default: 200)')
    parser.add_argument('--output', type=str, default='data/bulk_scraped',
                        help='Output directory')
    
    args = parser.parse_args()
    
    scraper = BulkRodentScraper(args.output)
    scraper.scrape_all_sources(args.images_per_species)
    
    print("\n✅ Scraping complete!")
    print("Next step: Run prepare_for_annotation.py to filter and organize images")


if __name__ == '__main__':
    main()