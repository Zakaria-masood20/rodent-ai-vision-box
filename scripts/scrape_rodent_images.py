#!/usr/bin/env python3
"""
Web scraper for collecting rodent images from multiple sources
Includes iNaturalist, Flickr, and other scientific databases
"""

import os
import time
import requests
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import io

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RodentImageScraper:
    def __init__(self, output_dir: str = "data/scraped_images"):
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Species to search for
        self.species_info = {
            'roof_rat': {
                'scientific': 'Rattus rattus',
                'common': ['roof rat', 'black rat', 'ship rat'],
                'search_terms': ['roof rat', 'black rat', 'Rattus rattus', 'ship rat climbing']
            },
            'norway_rat': {
                'scientific': 'Rattus norvegicus',
                'common': ['norway rat', 'brown rat', 'sewer rat'],
                'search_terms': ['norway rat', 'brown rat', 'Rattus norvegicus', 'sewer rat']
            },
            'mouse': {
                'scientific': 'Mus musculus',
                'common': ['house mouse', 'common mouse'],
                'search_terms': ['house mouse', 'Mus musculus', 'common mouse', 'domestic mouse']
            }
        }
        
        # Create directories
        for species in self.species_info.keys():
            (self.output_dir / species).mkdir(parents=True, exist_ok=True)
        
        # Track downloaded images to avoid duplicates
        self.downloaded_hashes = set()
        self.metadata = []
    
    def scrape_inaturalist(self, species_key: str, max_images: int = 200):
        """
        Scrape images from iNaturalist API
        """
        logger.info(f"Scraping iNaturalist for {species_key}")
        
        species_data = self.species_info[species_key]
        scientific_name = species_data['scientific']
        
        base_url = "https://api.inaturalist.org/v1/observations"
        
        params = {
            'taxon_name': scientific_name,
            'quality_grade': 'research',
            'has[]': 'photos',
            'per_page': 200,
            'order': 'votes',
            'photos': 'true',
            'geo': 'true'  # Only geotagged observations
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            observations = data.get('results', [])
            logger.info(f"Found {len(observations)} observations for {species_key}")
            
            downloaded = 0
            for obs in observations[:max_images]:
                if downloaded >= max_images:
                    break
                    
                photos = obs.get('photos', [])
                if not photos:
                    continue
                
                for photo in photos[:1]:  # Take first photo from each observation
                    # Get large size image
                    photo_url = photo['url'].replace('square', 'large')
                    
                    metadata = {
                        'source': 'inaturalist',
                        'species': species_key,
                        'scientific_name': scientific_name,
                        'observation_id': obs.get('id'),
                        'quality_grade': obs.get('quality_grade'),
                        'place': obs.get('place_guess', ''),
                        'observed_on': obs.get('observed_on'),
                        'url': photo_url,
                        'license': photo.get('license_code', 'unknown')
                    }
                    
                    if self._download_image(photo_url, species_key, metadata):
                        downloaded += 1
                        if downloaded >= max_images:
                            break
            
            logger.info(f"Downloaded {downloaded} images from iNaturalist for {species_key}")
            
        except Exception as e:
            logger.error(f"Error scraping iNaturalist: {e}")
    
    def scrape_flickr(self, species_key: str, max_images: int = 100):
        """
        Scrape images from Flickr (requires API key)
        Note: You'll need to get a Flickr API key from https://www.flickr.com/services/apps/create/
        """
        logger.info(f"Scraping Flickr for {species_key}")
        
        # Flickr API configuration
        FLICKR_API_KEY = os.getenv('FLICKR_API_KEY', '')  # Set your API key as environment variable
        
        if not FLICKR_API_KEY:
            logger.warning("Flickr API key not found. Set FLICKR_API_KEY environment variable.")
            logger.info("Get your API key from: https://www.flickr.com/services/apps/create/")
            return
        
        base_url = "https://api.flickr.com/services/rest/"
        
        species_data = self.species_info[species_key]
        
        for search_term in species_data['search_terms'][:2]:  # Use first 2 search terms
            params = {
                'method': 'flickr.photos.search',
                'api_key': FLICKR_API_KEY,
                'text': search_term,
                'tags': 'rodent,animal,wildlife',
                'tag_mode': 'any',
                'content_type': '1',  # photos only
                'per_page': '50',
                'format': 'json',
                'nojsoncallback': '1',
                'license': '1,2,3,4,5,6,7,8,9,10',  # CC licenses
                'sort': 'relevance'
            }
            
            try:
                response = self.session.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data.get('stat') != 'ok':
                    logger.error(f"Flickr API error: {data}")
                    continue
                
                photos = data.get('photos', {}).get('photo', [])
                logger.info(f"Found {len(photos)} photos for '{search_term}'")
                
                downloaded = 0
                for photo in photos[:max_images // len(species_data['search_terms'])]:
                    # Construct photo URL
                    photo_url = f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}_b.jpg"
                    
                    metadata = {
                        'source': 'flickr',
                        'species': species_key,
                        'search_term': search_term,
                        'photo_id': photo['id'],
                        'title': photo.get('title', ''),
                        'url': photo_url
                    }
                    
                    if self._download_image(photo_url, species_key, metadata):
                        downloaded += 1
                
                logger.info(f"Downloaded {downloaded} images from Flickr for '{search_term}'")
                
            except Exception as e:
                logger.error(f"Error scraping Flickr: {e}")
    
    def scrape_gbif(self, species_key: str, max_images: int = 100):
        """
        Scrape images from GBIF (Global Biodiversity Information Facility)
        """
        logger.info(f"Scraping GBIF for {species_key}")
        
        species_data = self.species_info[species_key]
        scientific_name = species_data['scientific']
        
        # GBIF occurrence search
        base_url = "https://api.gbif.org/v1/occurrence/search"
        
        params = {
            'scientificName': scientific_name,
            'mediaType': 'StillImage',
            'limit': 100
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            logger.info(f"Found {len(results)} GBIF occurrences with images for {species_key}")
            
            downloaded = 0
            for occurrence in results[:max_images]:
                media = occurrence.get('media', [])
                if not media:
                    continue
                
                for medium in media[:1]:  # First image from each occurrence
                    image_url = medium.get('identifier')
                    if not image_url:
                        continue
                    
                    metadata = {
                        'source': 'gbif',
                        'species': species_key,
                        'scientific_name': scientific_name,
                        'occurrence_id': occurrence.get('key'),
                        'country': occurrence.get('country', ''),
                        'year': occurrence.get('year', ''),
                        'url': image_url,
                        'license': medium.get('license', 'unknown')
                    }
                    
                    if self._download_image(image_url, species_key, metadata):
                        downloaded += 1
                        if downloaded >= max_images:
                            break
            
            logger.info(f"Downloaded {downloaded} images from GBIF for {species_key}")
            
        except Exception as e:
            logger.error(f"Error scraping GBIF: {e}")
    
    def scrape_wikimedia(self, species_key: str, max_images: int = 50):
        """
        Scrape images from Wikimedia Commons
        """
        logger.info(f"Scraping Wikimedia Commons for {species_key}")
        
        species_data = self.species_info[species_key]
        scientific_name = species_data['scientific']
        
        base_url = "https://commons.wikimedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'{scientific_name} OR {species_data["common"][0]}',
            'srnamespace': '6',  # File namespace
            'srlimit': '50',
            'srinfo': 'totalhits',
            'srprop': 'size|wordcount|timestamp|snippet'
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get('query', {}).get('search', [])
            logger.info(f"Found {len(search_results)} Wikimedia results for {species_key}")
            
            downloaded = 0
            for result in search_results[:max_images]:
                title = result.get('title', '')
                if not title.startswith('File:'):
                    continue
                
                # Get image info
                info_params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': title,
                    'prop': 'imageinfo',
                    'iiprop': 'url|size|mime|extmetadata'
                }
                
                info_response = self.session.get(base_url, params=info_params, timeout=30)
                info_data = info_response.json()
                
                pages = info_data.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    imageinfo = page_info.get('imageinfo', [])
                    if not imageinfo:
                        continue
                    
                    image_url = imageinfo[0].get('url')
                    if not image_url:
                        continue
                    
                    metadata = {
                        'source': 'wikimedia',
                        'species': species_key,
                        'scientific_name': scientific_name,
                        'title': title,
                        'url': image_url
                    }
                    
                    if self._download_image(image_url, species_key, metadata):
                        downloaded += 1
                        if downloaded >= max_images:
                            break
            
            logger.info(f"Downloaded {downloaded} images from Wikimedia for {species_key}")
            
        except Exception as e:
            logger.error(f"Error scraping Wikimedia: {e}")
    
    def _download_image(self, url: str, species_key: str, metadata: Dict) -> bool:
        """
        Download and save an image with deduplication
        """
        try:
            # Download image
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                return False
            
            # Read image content
            image_content = response.content
            
            # Check for duplicates using hash
            image_hash = hashlib.md5(image_content).hexdigest()
            if image_hash in self.downloaded_hashes:
                logger.debug(f"Skipping duplicate image: {url}")
                return False
            
            # Validate image
            try:
                img = Image.open(io.BytesIO(image_content))
                # Check minimum size
                if img.width < 100 or img.height < 100:
                    logger.debug(f"Image too small: {img.width}x{img.height}")
                    return False
                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
            except Exception as e:
                logger.debug(f"Invalid image: {e}")
                return False
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            source = metadata.get('source', 'unknown')
            filename = f"{species_key}_{source}_{timestamp}_{image_hash[:8]}.jpg"
            filepath = self.output_dir / species_key / filename
            
            # Save image
            img.save(filepath, 'JPEG', quality=95)
            
            # Record metadata
            metadata['filename'] = filename
            metadata['filepath'] = str(filepath)
            metadata['hash'] = image_hash
            metadata['size'] = f"{img.width}x{img.height}"
            metadata['timestamp'] = timestamp
            self.metadata.append(metadata)
            
            # Add to downloaded hashes
            self.downloaded_hashes.add(image_hash)
            
            logger.debug(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            logger.debug(f"Failed to download {url}: {e}")
            return False
    
    def scrape_all(self, images_per_species: int = 200):
        """
        Scrape images from all sources for all species
        """
        logger.info("Starting comprehensive rodent image scraping...")
        
        for species_key in self.species_info.keys():
            logger.info(f"\n{'='*50}")
            logger.info(f"Scraping images for: {species_key}")
            logger.info(f"{'='*50}")
            
            # Distribute images across sources
            per_source = images_per_species // 4
            
            # Scrape from each source
            self.scrape_inaturalist(species_key, per_source * 2)  # iNaturalist usually has more
            self.scrape_flickr(species_key, per_source)
            self.scrape_gbif(species_key, per_source // 2)
            self.scrape_wikimedia(species_key, per_source // 2)
            
            # Progress update
            species_dir = self.output_dir / species_key
            image_count = len(list(species_dir.glob('*.jpg')))
            logger.info(f"Total images for {species_key}: {image_count}")
        
        # Save metadata
        self._save_metadata()
        
        # Print summary
        self._print_summary()
    
    def _save_metadata(self):
        """
        Save metadata to JSON file
        """
        metadata_file = self.output_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        logger.info(f"Metadata saved to: {metadata_file}")
    
    def _print_summary(self):
        """
        Print scraping summary
        """
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        
        total_images = 0
        for species_key in self.species_info.keys():
            species_dir = self.output_dir / species_key
            image_count = len(list(species_dir.glob('*.jpg')))
            print(f"{species_key:15} : {image_count:4} images")
            total_images += image_count
        
        print("-"*30)
        print(f"{'TOTAL':15} : {total_images:4} images")
        print(f"\nOutput directory: {self.output_dir.absolute()}")
        print(f"Metadata file: {self.output_dir / 'metadata.json'}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape rodent images from multiple sources')
    parser.add_argument('--output', type=str, default='data/scraped_images',
                        help='Output directory for images')
    parser.add_argument('--images-per-species', type=int, default=200,
                        help='Number of images to download per species')
    parser.add_argument('--species', type=str, choices=['roof_rat', 'norway_rat', 'mouse'],
                        help='Scrape only specific species')
    parser.add_argument('--source', type=str, 
                        choices=['inaturalist', 'flickr', 'gbif', 'wikimedia'],
                        help='Scrape from specific source only')
    
    args = parser.parse_args()
    
    scraper = RodentImageScraper(args.output)
    
    if args.species and args.source:
        # Scrape specific species from specific source
        if args.source == 'inaturalist':
            scraper.scrape_inaturalist(args.species, args.images_per_species)
        elif args.source == 'flickr':
            scraper.scrape_flickr(args.species, args.images_per_species)
        elif args.source == 'gbif':
            scraper.scrape_gbif(args.species, args.images_per_species)
        elif args.source == 'wikimedia':
            scraper.scrape_wikimedia(args.species, args.images_per_species)
    elif args.species:
        # Scrape specific species from all sources
        scraper.scrape_inaturalist(args.species, args.images_per_species // 2)
        scraper.scrape_flickr(args.species, args.images_per_species // 4)
        scraper.scrape_gbif(args.species, args.images_per_species // 4)
        scraper.scrape_wikimedia(args.species, args.images_per_species // 4)
    else:
        # Scrape all species from all sources
        scraper.scrape_all(args.images_per_species)
    
    scraper._save_metadata()
    scraper._print_summary()


if __name__ == '__main__':
    main()