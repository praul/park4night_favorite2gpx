import requests
import json
import re
import time
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

def create_gpx(places, folder_name, output_file='places.gpx'):
    """Create a GPX file from the collected places."""
    gpx_template = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Park4Night Extractor" xmlns="http://www.topografix.com/GPX/1/1">
    <metadata>
        <name>{folder_name}</name>
        <time>{timestamp}</time>
    </metadata>
    {waypoints}
</gpx>'''
    
    waypoint_template = '''    <wpt lat="{lat}" lon="{lon}">
        <name>{name}</name>
        <desc>{desc}</desc>
    </wpt>'''
    
    waypoints = []
    for place in places:
        if place['coordinates']:
            waypoints.append(waypoint_template.format(
                lat=place['coordinates']['lat'],
                lon=place['coordinates']['lng'],
                name=place['name'],
                desc=place['description'] or ''
            ))
    
    gpx_content = gpx_template.format(
        folder_name=folder_name,
        timestamp=datetime.utcnow().isoformat(),
        waypoints='\n'.join(waypoints)
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(gpx_content)
    
    print(f"\nGPX file created: {output_file}")

def get_session_id():
    """Get session ID from environment or user input."""
    load_dotenv()
    saved_session = os.getenv('PARK4NIGHT_SESSION')
    
    if saved_session:
        use_saved = input("Use saved session ID? (y/n): ").lower() == 'y'
        if use_saved:
            return saved_session
    
    session_id = input("Please enter your PHPSESSID: ")
    save = input("Save this session ID for future use? (y/n): ").lower() == 'y'
    
    if save:
        with open('.env', 'a') as f:
            f.write(f'\nPARK4NIGHT_SESSION={session_id}')
    
    return session_id

def get_place_details(place_id):
    """Extract details from a specific park4night place page."""
    url = f"https://park4night.com/de/place/{place_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract name
        name_element = soup.select_one('h1')
        name = name_element.text.strip() if name_element else None

        # Extract coordinates
        lat, lng = None, None
        try:
            location_li = soup.select_one('.place-info-location li')
            if location_li:
                spans = location_li.find_all('span')
                for span in spans:
                    coord_text = span.text.strip()
                    coord_match = re.match(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)', coord_text)
                    if coord_match:
                        lat, lng = coord_match.groups()
                        break
        except Exception as e:
            print(f"Warning: Could not extract coordinates for place {place_id}: {e}")

        # Extract German description and rating
        description = None
        german_desc = soup.select_one('.place-info-description p[lang="de"]')
        if german_desc:
            description = german_desc.text.strip()
            
        # Extract rating
        rating_div = soup.select_one('.place-feedback-average')
        rating = None
        if rating_div:
            rating_span = rating_div.select_one('.text-gray')
            if rating_span:
                rating = rating_span.text.strip()
        
        # Build URL
        url = f"https://park4night.com/de/place/{place_id}"
        
        # Extract details and format them nicely
        details_div = soup.select_one('.place-info-details')
        prices = None
        if details_div:
            # Split by identifiable sections and clean up
            details_text = details_div.text.strip()
            
            # Extract price information
            price_info = []
            if 'Preis der Dienstleistungen' in details_text:
                price_info.append('Servicegebühren:')
                if '/6h electricity' in details_text:
                    price_info.append('- Strom: 1,00€/6h')
                if '/25l water' in details_text:
                    price_info.append('- Wasser: 1€/25l')
            
            if 'Parkgebühren' in details_text:
                park_fee = re.search(r'Parkgebühren(\d+)€', details_text)
                if park_fee:
                    price_info.append(f'Stellplatzgebühr: {park_fee.group(1)}€')
            
            prices = '\n'.join(price_info) if price_info else "Keine Preisangaben"
        
        # Combine description with additional information
        full_description = []
        if description:
            full_description.append(description)
        if prices:
            full_description.append("\nPreise:")
            full_description.append(prices)
        if rating:
            full_description.append(f"\nBewertung: {rating}")
        full_description.append(f"\nLink: {url}")
        
        description = '\n'.join(full_description)
        
        return {
            'id': place_id,
            'name': name,
            'coordinates': {'lat': lat, 'lng': lng} if lat and lng else None,
            'description': description,
            'prices': prices
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching place {place_id}: {e}")
        return None

def get_bookmark_ids(session_id):
    """Get bookmarks from API and let user select a folder."""
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'de-DE,de;q=0.7',
        'axios-ajax': 'true',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://park4night.com/de/search?bookmarks=1',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36'
    }

    cookies = {
        'PHPSESSID': session_id,
        'cookie_consent_v2': '{"status":"accepted","acceptedCategories":["essentials","analytics"]}'
    }

    try:
        response = requests.get('https://park4night.com/api/user', headers=headers, cookies=cookies)
        response.raise_for_status()
        
        data = response.json()
        folders = data.get('bookmarksFolders', [])
        
        print("\nAvailable folders:")
        for i, folder in enumerate(folders, 1):
            print(f"{i}. {folder['name']} ({len(folder['bookmarks'])} bookmarks)")
        
        while True:
            try:
                choice = int(input("\nEnter folder number (1-{}): ".format(len(folders))))
                if 1 <= choice <= len(folders):
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        selected_folder = folders[choice - 1]
        bookmark_ids = selected_folder['bookmarks']
        print(f"\nFound {len(bookmark_ids)} bookmarks in folder '{selected_folder['name']}':")
        print("\nBookmark IDs:")
        print(', '.join(map(str, bookmark_ids)))
        
        return bookmark_ids, selected_folder['name']
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def process_bookmarks(bookmark_ids):
    """Process all bookmarks with rate limiting."""
    places = []
    total = len(bookmark_ids)
    
    print(f"\nProcessing {total} bookmarks...")
    for i, bookmark_id in enumerate(bookmark_ids, 1):
        print(f"Processing place {i}/{total}: {bookmark_id}")
        
        place = get_place_details(bookmark_id)
        if place:
            places.append(place)
        
        # Rate limiting: wait 1 second between requests
        if i < total:  # Don't wait after the last request
            time.sleep(1)
    
    return places

def sanitize_filename(name):
    """Convert a string to a valid filename."""
    filename = re.sub(r'[^\w\s-]', '', name)
    filename = re.sub(r'[-\s]+', '_', filename.strip())
    return filename.lower()

def main():
    print("Park4Night Bookmark Extractor")
    print("----------------------------")
    
    # Get session ID
    session_id = get_session_id()
    
    # Get bookmark IDs and folder name
    result = get_bookmark_ids(session_id)
    
    if result and isinstance(result, tuple):
        bookmark_ids, folder_name = result
        
        # Process all bookmarks
        places = process_bookmarks(bookmark_ids)
        
        if places:
            # Create gpx directory if it doesn't exist
            os.makedirs('gpx', exist_ok=True)
            
            # Create default filename from folder name
            default_filename = f"{sanitize_filename(folder_name)}.gpx"
            
            # Get output filename
            output_file = input(f"\nEnter GPX file name (default: {default_filename}): ").strip() or default_filename
            
            # Add .gpx extension if not present
            if not output_file.lower().endswith('.gpx'):
                output_file += '.gpx'
            
            # Add gpx directory to path
            output_file = os.path.join('gpx', output_file)
                
            create_gpx(places, folder_name, output_file)
            print("\nExtraction completed successfully!")
        else:
            print("\nNo places were successfully processed.")
    else:
        print("\nFailed to get bookmarks.")

if __name__ == "__main__":
    main()