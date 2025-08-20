#!/usr/bin/env python3
"""
Script to help search and evaluate Roboflow datasets for multi-class rodent detection
"""

import requests
import json
from typing import List, Dict
import pandas as pd

class RoboflowDatasetSearcher:
    def __init__(self):
        self.base_url = "https://universe.roboflow.com"
        self.search_terms = [
            "rodent", "rat", "mouse", "pest", "wildlife",
            "rattus", "norway rat", "roof rat", "brown rat", "black rat",
            "house mouse", "mice", "rodent species", "pest control"
        ]
        
    def search_datasets(self, term: str) -> List[Dict]:
        """
        Search for datasets on Roboflow Universe
        Note: This is a conceptual function - actual API may differ
        """
        # This would need actual Roboflow API implementation
        print(f"Searching for: {term}")
        # Placeholder for search results
        return []
    
    def evaluate_dataset(self, dataset_info: Dict) -> Dict:
        """
        Evaluate if a dataset meets our requirements
        """
        evaluation = {
            'name': dataset_info.get('name', ''),
            'suitable': False,
            'score': 0,
            'pros': [],
            'cons': []
        }
        
        # Check classes
        classes = dataset_info.get('classes', [])
        class_names_lower = [c.lower() for c in classes]
        
        # Check for multi-class rodent detection
        has_rat = any('rat' in c for c in class_names_lower)
        has_mouse = any('mouse' in c or 'mice' in c for c in class_names_lower)
        has_species = any(species in ' '.join(class_names_lower) for species in 
                          ['roof', 'norway', 'brown', 'black', 'house'])
        
        # Scoring
        if len(classes) > 1:
            evaluation['score'] += 30
            evaluation['pros'].append(f"Multi-class: {len(classes)} classes")
        else:
            evaluation['cons'].append("Single class only")
        
        if has_rat and has_mouse:
            evaluation['score'] += 40
            evaluation['pros'].append("Has both rat and mouse classes")
        
        if has_species:
            evaluation['score'] += 30
            evaluation['pros'].append("Species-specific labels")
        
        # Check dataset size
        num_images = dataset_info.get('images', 0)
        if num_images > 500:
            evaluation['score'] += 20
            evaluation['pros'].append(f"Good size: {num_images} images")
        elif num_images > 100:
            evaluation['score'] += 10
            evaluation['pros'].append(f"Adequate size: {num_images} images")
        else:
            evaluation['cons'].append(f"Small dataset: {num_images} images")
        
        # Mark as suitable if score > 60
        evaluation['suitable'] = evaluation['score'] >= 60
        
        return evaluation
    
    def print_search_queries(self):
        """
        Print formatted search queries for manual searching
        """
        print("=" * 60)
        print("ROBOFLOW UNIVERSE SEARCH QUERIES")
        print("=" * 60)
        print("\nTry these searches on https://universe.roboflow.com:\n")
        
        # Primary searches
        print("🔍 PRIMARY SEARCHES (Most Likely):")
        primary = [
            "rodent species",
            "rat mouse detection",
            "pest detection multi",
            "norway roof rat",
            "rodent classification"
        ]
        for query in primary:
            print(f"  • {query}")
        
        # Secondary searches
        print("\n🔍 SECONDARY SEARCHES:")
        secondary = [
            "urban wildlife",
            "pest control",
            "mouse rat",
            "rattus detection",
            "animal species classification"
        ]
        for query in secondary:
            print(f"  • {query}")
        
        # Filter suggestions
        print("\n📋 FILTERS TO APPLY:")
        print("  • Classes: 2+ (multiple classes)")
        print("  • Images: 100+ minimum")
        print("  • Format: Object Detection")
        print("  • Export: YOLOv8 compatible")
        
        print("\n" + "=" * 60)
        print("WHAT TO LOOK FOR IN CLASS NAMES")
        print("=" * 60)
        
        print("\n✅ GOOD SIGNS (Species-specific):")
        good_classes = [
            "roof_rat, norway_rat, mouse",
            "black_rat, brown_rat, house_mouse",
            "rattus_rattus, rattus_norvegicus, mus_musculus",
            "rat_species_1, rat_species_2, mouse"
        ]
        for classes in good_classes:
            print(f"  • {classes}")
        
        print("\n⚠️  ACCEPTABLE (Can work with):")
        acceptable = [
            "rat, mouse",
            "rodent_large, rodent_small",
            "pest_rat, pest_mouse"
        ]
        for classes in acceptable:
            print(f"  • {classes}")
        
        print("\n❌ NOT SUITABLE:")
        bad = [
            "rodent (single class)",
            "animal (too generic)",
            "pest (too generic)"
        ]
        for classes in bad:
            print(f"  • {classes}")
    
    def generate_dataset_requirements(self):
        """
        Generate a requirements file for dataset selection
        """
        requirements = {
            'minimum_requirements': {
                'num_classes': 2,
                'min_images_per_class': 100,
                'total_images': 300,
                'annotation_type': 'bounding_box',
                'format': ['YOLO', 'YOLOv8', 'COCO']
            },
            'ideal_requirements': {
                'num_classes': 3,
                'classes': ['roof_rat', 'norway_rat', 'mouse'],
                'min_images_per_class': 200,
                'total_images': 600,
                'has_validation_set': True,
                'has_test_set': True
            },
            'class_name_variations': {
                'roof_rat': ['roof rat', 'black rat', 'rattus rattus', 'ship rat'],
                'norway_rat': ['norway rat', 'brown rat', 'rattus norvegicus', 'sewer rat'],
                'mouse': ['house mouse', 'mus musculus', 'mice', 'common mouse']
            }
        }
        
        with open('dataset_requirements.json', 'w') as f:
            json.dump(requirements, f, indent=2)
        
        print("\nDataset requirements saved to: dataset_requirements.json")
        return requirements


def main():
    searcher = RoboflowDatasetSearcher()
    
    print("🔎 ROBOFLOW DATASET SEARCH HELPER")
    print("=" * 60)
    
    # Generate search queries
    searcher.print_search_queries()
    
    # Generate requirements file
    print("\n" + "=" * 60)
    print("GENERATING REQUIREMENTS FILE")
    print("=" * 60)
    requirements = searcher.generate_dataset_requirements()
    
    # Print evaluation criteria
    print("\n" + "=" * 60)
    print("HOW TO EVALUATE DATASETS")
    print("=" * 60)
    
    print("\n1. Check the classes:")
    print("   - Need at least 2 classes (rat, mouse)")
    print("   - Ideal: 3 classes (roof_rat, norway_rat, mouse)")
    
    print("\n2. Check image count:")
    print("   - Minimum: 100 per class")
    print("   - Ideal: 200+ per class")
    
    print("\n3. Check image quality:")
    print("   - Clear visibility of animals")
    print("   - Various angles and lighting")
    print("   - Both indoor/outdoor settings")
    
    print("\n4. Check annotations:")
    print("   - Bounding boxes (not just image labels)")
    print("   - Consistent labeling")
    print("   - YOLOv8 export available")
    
    print("\n" + "=" * 60)
    print("ALTERNATIVE: CREATE HYBRID DATASET")
    print("=" * 60)
    
    print("\nIf you can't find perfect dataset:")
    print("1. Find a 'rat vs mouse' dataset")
    print("2. Find a 'rat species' dataset")
    print("3. Combine them using our merge script")
    print("4. Re-label if necessary")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\n1. Go to https://universe.roboflow.com")
    print("2. Try the search queries above")
    print("3. Note down promising datasets")
    print("4. Check if they meet requirements")
    print("5. Download in YOLOv8 format")


if __name__ == '__main__':
    main()