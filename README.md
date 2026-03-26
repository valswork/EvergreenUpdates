# 🌲 EvergreenUpdates

A simple desktop tool enabled by AI that scans websites for news articles and compiles them into a CSV. Built for policy teams who need to monitor large numbers of stakeholder sites without manual checking.

## What It Does

Enter a list of URLs and the tool will scan each one for news articles, collecting the title, link, date published, date retrieved, and source URL into a single CSV file.

## Requirements

To use this tool you will need:
- Python 3.10 or newer
- A **Google API key** (see [Getting an API Key](#getting-an-api-key) below)
- A **PEM certificate file** (for secure connections to your organization's network, see [Contact](#contact) for support if you work for NRCan)

## Getting Started

### Option 1: Run the Executable (Recommended)
1. Download the latest `EvergreenUpdates.exe` from the [Releases](../../releases) page
2. Double-click to open
3. Enter your Google API key, the path to your `.pem` certificate, and your list of URLs (one per line)
4. Click Run - your CSV will be saved to the same folder as the executable

### Option 2: Run the Python Script
1. Clone this repository
2. Create and activate a virtual environment:

   Windows
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   macOS / Linux
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Run the script:
   ```bash
   python src/scraper.py
   ```

## Getting an API Key

This tool uses the Google API for article discovery. To get a free API key:
1. Go to [https://aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)
2. Sign in with your Google account
3. Click **Create API key**
4. Copy the key and paste it into the app when prompted

## Output

The tool produces a CSV file named **`news_results.csv`** by default — you can change this in the UI before running. It contains the following columns:

| Column | Description |
|---|---|
| title | Article headline |
| url | URL to the article |
| published_date | Date the article was published |
| retrieved_on | Date the tool found the article |
| source_url | The website URL you provided |

As with all AI generated content, please be aware that the results may be inaccurate. 

## Notes
- URLs should be entered one per line in the text box
- The tool works best with news and press release pages rather than homepages
- Your API key and certificate path are never saved or transmitted

## Contact
Valerie Gies @ valerie.gies@nrcan-rncan.gc.ca
