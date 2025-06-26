"""
Made by Howie Lo
The purpose of this file is to just grab all the ids in the esta dataset. This code is really meant to be used once so there is a lack of documentation and such.
"""
import json
import lzma
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, List, Union
import threading
from collections import defaultdict

# Thread-safe list to collect all match IDs
all_match_ids = []
match_ids_lock = threading.Lock()

def find_match_ids(data: Union[dict, list]) -> List[Any]:
    """Recursively search for all occurrences of 'hltvUrl' in the given JSON structure."""
    """hltv should just be 1 parameter in the json file lol. Oh well -Howie"""
    match_ids: List[Any] = []
    
    def recursive_search(obj: Any) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "hltvUrl":
                    match_ids.append(value)
                else:
                    recursive_search(value)
        elif isinstance(obj, list):
            for item in obj:
                recursive_search(item)
    
    recursive_search(data)
    return match_ids

def process_file(file_path: Path) -> List[str]:
    """Process a single compressed file and extract match IDs."""
    try:
        print(f"Processing: {file_path.name}")
        
        # Step 1: Decompress the .xz file
        with lzma.open(file_path, "rt", encoding="utf-8") as file:
            decompressed_data: str = file.read()
        
        # Step 2: Load the JSON data
        json_data: Any = json.loads(decompressed_data)
        
        # Step 3: Find Match IDs
        match_ids: List[Any] = find_match_ids(json_data)
        
        print(f"Found {len(match_ids)} match IDs in {file_path.name}")
        return match_ids
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def process_files_in_directory(directory_path: str, max_workers: int = 4) -> List[str]:
    """Process all .xz files in the directory using multithreading."""
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Directory {directory_path} does not exist.")
        return []
    
    # Find all .xz files in the directory
    xz_files = list(directory.glob("*.xz"))
    
    if not xz_files:
        print(f"No .xz files found in {directory_path}")
        return []
    
    print(f"Found {len(xz_files)} .xz files to process")
    
    all_urls = []
    
    # Use ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files for processing
        future_to_file = {executor.submit(process_file, file_path): file_path 
                         for file_path in xz_files}
        
        # Collect results as they complete
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                match_ids = future.result()
                all_urls.extend(match_ids)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    return all_urls

def write_urls_to_file(urls: List[str], output_file: str = "extracted_urls.txt") -> None:
    """Write all URLs to a single file."""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for url in urls:
                f.write(f"{url}\n")
        print(f"Successfully wrote {len(urls)} URLs to {output_file}")
    except Exception as e:
        print(f"Error writing to file {output_file}: {e}")

def main() -> None:
    """Main function to process all files and extract URLs."""
    # directory_path: str = "compressed_files"
    directory_path: str = "../esta/data/lan/"

    print(f"Current working directory: {os.getcwd()}")
    print(f"Target directory: {os.path.abspath(directory_path)}")
    
    # Process all files in the directory
    print("Starting multithreaded processing...")
    all_urls = process_files_in_directory(directory_path, max_workers=8)
    
    if all_urls:
        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(all_urls))
        
        print(f"\nTotal URLs found: {len(all_urls)}")
        print(f"Unique URLs: {len(unique_urls)}")
        
        # Write to file
        write_urls_to_file(unique_urls, "all_match_urls.txt")
        
        print("\nFirst 10 URLs:")
        for i, url in enumerate(unique_urls[:10], 1):
            print(f"{i}. {url}")
            
    else:
        print("No URLs found in any files.")

if __name__ == "__main__":
    main()