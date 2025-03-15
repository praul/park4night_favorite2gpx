# Park4Night Favorites Exporter

This tool exports your Park4Night favorites to GPX format, making them easily accessible in navigation apps and devices. It includes location details, prices, ratings, and descriptions in German.

## Features

- Export favorite places from any folder in your Park4Night account
- GPX files include:
  - Coordinates
  - Place names
  - German descriptions
  - Price information
  - Ratings
  - Links to original places
- Rate-limited requests to avoid server load
- Session management (save/load)

## Getting Your Session ID

To use this script, you need your Park4Night session ID. Here's how to get it:

1. Go to [park4night.com](https://park4night.com) and log in to your account
2. Open browser developer tools (F12 or right-click -> Inspect)
3. Go to the "Application" or "Storage" tab
4. Under "Cookies", select "https://park4night.com"
5. Find the cookie named "PHPSESSID"
6. Copy its value - this is your session ID

The script can save this ID locally so you don't need to retrieve it every time.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/park4night-export.git
   cd park4night-export
   ```

2. Make the run script executable:

   ```bash
   chmod +x run.sh
   ```

3. Run the script:
   ```bash
   ./run.sh
   ```

The script will automatically:

- Create a Python virtual environment
- Install required dependencies
- Create a gpx directory for output files
- Launch the parser

## Usage

1. Run the script:

   ```bash
   ./run.sh
   ```

2. When prompted, enter your session ID or use a previously saved one

3. Select a folder from your favorites

4. The script will create a GPX file in the `gpx` directory

## Output Format

The generated GPX files include:

- Waypoints with coordinates
- Place names
- Detailed descriptions including:
  - Original German description
  - Price information (if available)
  - Rating from Park4Night
  - Link to the original place page

Example output:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Park4Night Extractor">
    <metadata>
        <name>Folder Name</name>
        <time>2025-03-15T17:02:27.653486</time>
    </metadata>
    <wpt lat="49.3798" lon="11.3571">
        <name>Place Name</name>
        <desc>German description...

Preise:
Servicegebühren:
- Strom: 1,00€/6h
- Wasser: 1€/25l
Stellplatzgebühr: 10€

Bewertung: 4.5/5

Link: https://park4night.com/de/place/12345</desc>
    </wpt>
</gpx>
```

## Requirements

- Python 3.6+
- Bash shell (for the wrapper script)
- Internet connection
- Valid Park4Night account with favorites

All Python dependencies are automatically installed by the wrapper script.
