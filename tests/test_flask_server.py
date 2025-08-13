#!/usr/bin/env python
"""
Test script to demonstrate the Flask server functionality.
This creates a sample HTML folder structure with mock data for testing.
"""

import os
import json
import shutil
from datetime import datetime, timedelta
import random

def create_test_data(base_folder='test_html'):
    """Create test data structure for Flask server testing."""
    
    # Clean up if exists
    if os.path.exists(base_folder):
        shutil.rmtree(base_folder)
    
    os.makedirs(base_folder)
    
    # Analysis types for variety
    analysis_types = ['XPCS', 'SAXS', 'XPCS-SAXS', 'Dynamic']
    
    # Create 10 sample result folders
    for i in range(10):
        # Create folder name
        folder_name = f"sample_{i+1:03d}_results"
        folder_path = os.path.join(base_folder, folder_name)
        os.makedirs(folder_path)
        
        # Create metadata
        start_time = datetime.now() - timedelta(days=random.randint(1, 30), 
                                               hours=random.randint(0, 23))
        plot_time = start_time + timedelta(minutes=random.randint(5, 60))
        
        metadata = {
            "analysis_type": random.choice(analysis_types),
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "plot_time": plot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "sample_name": f"Sample_{i+1}",
            "temperature": round(20 + random.random() * 10, 2),
            "exposure_time": round(0.1 + random.random() * 0.9, 3),
            "detector": "Eiger 500K",
            "beamline": "8-ID-I",
            "energy": 7.35,
            "distance": 3.6,
            "pixel_size": 0.075,
            "beam_center": {"x": 487, "y": 512},
            "mask_file": "mask.h5",
            "data_file": f"sample_{i+1}.h5",
            "q_values": {
                "q_min": 0.001,
                "q_max": 0.1,
                "q_points": 100
            }
        }
        
        # Save metadata
        with open(os.path.join(folder_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create placeholder image files
        # In real usage, these would be actual PNG images
        placeholder_files = [
            'saxs_mask.png',
            'stability.png',
            'g2_q001.png',
            'g2_q002.png',
            'g2_q003.png',
            'c2_q001.png',
            'c2_q002.png'
        ]
        
        for filename in placeholder_files:
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'w') as f:
                f.write(f"Placeholder for {filename}")
        
        print(f"Created test data for {folder_name}")
    
    print(f"\nTest data created in '{base_folder}' folder")
    print("\nTo test the Flask server, run:")
    print(f"  python -m xpcs_webplot.flask_app --html-folder {base_folder}")
    print("\nThen open http://localhost:5000 in your browser")
    print("\nTo clean up test data:")
    print(f"  rm -rf {base_folder}")


if __name__ == '__main__':
    create_test_data()
