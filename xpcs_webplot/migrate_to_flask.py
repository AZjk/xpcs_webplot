#!/usr/bin/env python
"""
Migration script to reorganize HTML files for Flask-based serving.

This script helps transition from the static HTML approach to the Flask-based
dynamic serving approach. It can optionally move sub-HTML files to a subfolder
for better organization.
"""

import os
import shutil
import argparse
import logging

logger = logging.getLogger(__name__)


def migrate_html_structure(html_folder='html', create_results_subfolder=False):
    """
    Migrate the HTML folder structure for Flask compatibility.
    
    Args:
        html_folder: Path to the HTML folder
        create_results_subfolder: If True, move result folders to a 'results' subfolder
    """
    if not os.path.exists(html_folder):
        logger.error(f"HTML folder '{html_folder}' does not exist")
        return False
    
    # Files to remove (old static index files)
    static_files_to_remove = ['index.html', 'preview.html', 'iframe.html', 
                              'jquery.minipreview.css', 'jquery.minipreview.js']
    
    # Remove old static files
    for filename in static_files_to_remove:
        filepath = os.path.join(html_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Removed old static file: {filename}")
    
    if create_results_subfolder:
        # Create results subfolder
        results_folder = os.path.join(html_folder, 'results')
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
            logger.info(f"Created results subfolder: {results_folder}")
        
        # Move all result directories to the results subfolder
        items = os.listdir(html_folder)
        moved_count = 0
        
        for item in items:
            item_path = os.path.join(html_folder, item)
            
            # Skip if not a directory or if it's the results folder itself
            if not os.path.isdir(item_path) or item == 'results':
                continue
            
            # Check if it's a result directory (contains metadata.json)
            if os.path.exists(os.path.join(item_path, 'metadata.json')):
                new_path = os.path.join(results_folder, item)
                shutil.move(item_path, new_path)
                logger.info(f"Moved {item} to results subfolder")
                moved_count += 1
        
        logger.info(f"Moved {moved_count} result directories to results subfolder")
        
        # Update Flask app config if results are in subfolder
        logger.info("Note: When running the Flask server with results in a subfolder,")
        logger.info("      use: xpcs_webplot_server --html-folder html/results")
    
    # Clean up any remaining HTML files in the root
    for item in os.listdir(html_folder):
        if item.endswith('.html') and item not in ['index.html']:
            filepath = os.path.join(html_folder, item)
            os.remove(filepath)
            logger.info(f"Removed old HTML file: {item}")
    
    logger.info("Migration completed successfully!")
    logger.info("\nTo run the Flask server:")
    if create_results_subfolder:
        logger.info(f"  xpcs_webplot_server --html-folder {html_folder}/results")
    else:
        logger.info(f"  xpcs_webplot_server --html-folder {html_folder}")
    
    return True


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description='Migrate XPCS WebPlot HTML structure for Flask compatibility')
    parser.add_argument('--html-folder', default='html',
                        help='Path to the HTML folder to migrate (default: html)')
    parser.add_argument('--create-subfolder', action='store_true',
                        help='Move result directories to a "results" subfolder')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Run migration
    success = migrate_html_structure(args.html_folder, args.create_subfolder)
    
    if not success:
        exit(1)


if __name__ == '__main__':
    main()
