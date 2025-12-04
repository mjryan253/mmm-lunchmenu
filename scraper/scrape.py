import time
import schedule
import os
import sys
import logging
import re
import requests
from bs4 import BeautifulSoup
import pytz
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
URL = os.getenv("MENU_URL", "https://www.aacps.org/dining?filter=61292")
OUTPUT_PATH_HTML = os.getenv("OUTPUT_PATH", "/output/lunch_menu.html")
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "03:00")  # Default 3:00 AM
WEEKEND_FALLBACK = os.getenv("WEEKEND_FALLBACK", "true").lower() == "true"  # Show Monday's menu on weekends
TARGET_DAY_PATTERN = os.getenv("TARGET_DAY_PATTERN", r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)')
MENU_SECTION_PATTERN = os.getenv("MENU_SECTION_PATTERN", r'Lunch(.*?)(?=salad bar|$)')
MENU_SECTION_NAME = os.getenv("MENU_SECTION_NAME", "Lunch")

TZ = pytz.timezone(TIMEZONE)

def fetch_menu_content():
    """Fetch the menu content from the configured website using simple HTTP request."""
    try:
        logger.info(f"Fetching menu from: {URL}")
        
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Successfully fetched menu content ({len(response.content)} bytes)")
        return response.text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch menu content: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching menu: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_menu_content(html_content):
    """Parse the HTML content and extract menu information for the current day.
    On weekends (Saturday/Sunday), shows Monday's menu if WEEKEND_FALLBACK is enabled."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        current_time = datetime.now(TZ)
        day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
        
        # On weekends (Saturday=5, Sunday=6), show Monday's menu if enabled
        if WEEKEND_FALLBACK and day_of_week >= 5:  # Saturday or Sunday
            target_date_str = "Monday"
            logger.info("Weekend detected - showing Monday's menu")
        else:
            # E.g., "Tuesday"
            target_date_str = current_time.strftime('%A')
        
        # Get all text from the page
        text_content = soup.get_text()

        # Find the section for the target day's menu
        # We look for the date string, and capture everything until the next day of the week
        days = TARGET_DAY_PATTERN
        today_menu_match = re.search(fr'{target_date_str}(.*?)(?={days})', text_content, re.DOTALL | re.IGNORECASE)

        if not today_menu_match:
            # If the target day is the last day in the menu, the above regex will fail.
            # So, we try to match until the end of the string.
            today_menu_match = re.search(fr'{target_date_str}(.*)', text_content, re.DOTALL | re.IGNORECASE)

        if not today_menu_match:
            logger.warning(f"Could not find menu content for target date: {target_date_str}")
            return None
        
        today_menu = today_menu_match.group(1)
        
        menu_sections = []
        
        # Extract menu section using configured pattern
        section_match = re.search(MENU_SECTION_PATTERN, today_menu, re.DOTALL | re.IGNORECASE)
        if section_match:
            section_content = section_match.group(1).strip()
            menu_sections.append((MENU_SECTION_NAME, section_content))

        if not menu_sections:
            logger.warning("Could not extract any menu sections from today's content.")
            return None
            
        return menu_sections
        
    except Exception as e:
        logger.error(f"Error parsing menu content: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_html_output(menu_sections, timestamp):
    """Generate clean HTML output for the menu with MagicMirror aesthetic."""
    # Use string formatting with double braces to escape CSS braces
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lunch Menu</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Roboto Condensed', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 10px 15px;
            background-color: transparent;
            color: #fff;
            line-height: 1.5;
            font-size: 14px;
        }}
        .timestamp {{
            font-size: 11px;
            opacity: 0.5;
            text-align: center;
            margin-bottom: 12px;
            font-weight: 300;
            letter-spacing: 0.5px;
        }}
        .menu-section {{
            margin-bottom: 20px;
            padding: 0;
        }}
        .menu-section:last-child {{
            margin-bottom: 0;
        }}
        .menu-section h2 {{
            color: #fff;
            margin: 0 0 8px 0;
            font-size: 15px;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.9;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
            padding-bottom: 6px;
        }}
        .menu-content {{
            font-size: 13px;
            color: rgba(255, 255, 255, 0.85);
            line-height: 1.6;
            font-weight: 300;
        }}
        .menu-item {{
            margin-bottom: 6px;
            padding-left: 0;
        }}
        .menu-item:last-child {{
            margin-bottom: 0;
        }}
        .no-content {{
            text-align: center;
            color: rgba(255, 255, 255, 0.6);
            font-style: italic;
            padding: 20px;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="timestamp">Updated: {timestamp}</div>
    {content}
</body>
</html>"""
    
    if not menu_sections:
        content = '<div class="no-content">No menu information available at this time.</div>'
    else:
        content_parts = []
        for section_name, section_content in menu_sections:
            # Clean up the content and format it better
            # Remove excessive whitespace but preserve line breaks for readability
            cleaned_content = re.sub(r'\n\s*\n+', '\n', section_content)  # Remove multiple blank lines
            cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)  # Collapse multiple spaces
            cleaned_content = cleaned_content.strip()
            
            # Split into lines and format as menu items
            lines = [line.strip() for line in cleaned_content.split('\n') if line.strip()]
            menu_items_html = []
            for line in lines:
                # Format each line as a menu item
                # Escape HTML entities for safety
                escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                menu_items_html.append('<div class="menu-item">' + escaped_line + '</div>')
            
            items_html = ''.join(menu_items_html)
            content_parts.append(f'''
                <div class="menu-section">
                    <h2>{section_name}</h2>
                    <div class="menu-content">{items_html}</div>
                </div>
            ''')
        content = ''.join(content_parts)
    
    return html_template.format(timestamp=timestamp, content=content)

def job(max_retries=3):
    """Scrape the lunch menu and save as HTML"""
    tz_time = datetime.now(TZ)
    logger.info(f"Starting scrape job at {tz_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Ensure output directory exists and is writable
    output_dir = os.path.dirname(OUTPUT_PATH_HTML)
    try:
        os.makedirs(output_dir, exist_ok=True)
        # Try to set permissions on directory to ensure it's writable
        try:
            os.chmod(output_dir, 0o777)  # Make directory writable
        except Exception:
            pass  # Ignore if we can't change permissions
        logger.debug(f"Output directory verified: {output_dir}")
    except Exception as e:
        logger.warning(f"Could not create output directory {output_dir}: {e}")
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                logger.info(f"Retry attempt {attempt} of {max_retries}...")
                time.sleep(5)  # Brief delay before retry
            
            # Fetch menu content using simple HTTP request
            html_content = fetch_menu_content()
            if not html_content:
                raise Exception("Failed to fetch menu content")
            
            # Parse menu content
            logger.info("Parsing menu content...")
            menu_sections = parse_menu_content(html_content)
            
            if not menu_sections:
                logger.warning("Could not parse menu sections, but continuing...")
            
            # Generate HTML output
            current_time = datetime.now(TZ)
            timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            output_html = generate_html_output(menu_sections, timestamp)
            
            # Save HTML file
            logger.info(f"Saving HTML to {OUTPUT_PATH_HTML}...")
            
            # Remove existing file if it exists (might have wrong permissions)
            if os.path.exists(OUTPUT_PATH_HTML):
                try:
                    # Try to fix permissions first, then remove
                    try:
                        os.chmod(OUTPUT_PATH_HTML, 0o666)
                    except Exception:
                        pass
                    os.remove(OUTPUT_PATH_HTML)
                    logger.debug(f"Removed existing file {OUTPUT_PATH_HTML}")
                except Exception as e:
                    logger.warning(f"Could not remove existing file {OUTPUT_PATH_HTML}: {e}")
                    # Try to overwrite anyway
                    try:
                        os.chmod(OUTPUT_PATH_HTML, 0o666)
                    except Exception:
                        pass
            
            # Write the file
            try:
                with open(OUTPUT_PATH_HTML, 'w', encoding='utf-8') as f:
                    f.write(output_html)
                # Set permissions to be readable by all
                try:
                    os.chmod(OUTPUT_PATH_HTML, 0o666)
                except Exception:
                    pass
            except PermissionError as e:
                # If we still can't write, try creating a temp file and moving it
                logger.warning(f"Direct write failed, trying alternative method: {e}")
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, dir=output_dir) as tmp:
                    tmp.write(output_html)
                    tmp_path = tmp.name
                try:
                    os.replace(tmp_path, OUTPUT_PATH_HTML)
                except Exception as e2:
                    logger.error(f"Failed to move temp file: {e2}")
                    raise
            
            # Verify the HTML file was created
            if os.path.exists(OUTPUT_PATH_HTML):
                file_size = os.path.getsize(OUTPUT_PATH_HTML)
                if file_size > 0:
                    tz_time_end = datetime.now(TZ)
                    logger.info(f"HTML menu saved successfully to {OUTPUT_PATH_HTML} ({file_size} bytes)")
                    logger.info(f"Scrape job completed successfully at {tz_time_end.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    return  # Success, exit the retry loop
                else:
                    raise Exception(f"HTML file exists but is empty (0 bytes)")
            else:
                raise Exception(f"HTML file was not created at {OUTPUT_PATH_HTML}")
                
        except Exception as e:
            tz_time_error = datetime.now(TZ)
            logger.error(f"Error during scrape (attempt {attempt}/{max_retries}) at {tz_time_error.strftime('%Y-%m-%d %H:%M:%S %Z')}: {e}")
            if attempt < max_retries:
                logger.info("Will retry...")
                import traceback
                traceback.print_exc()
            else:
                logger.error("All retry attempts failed. Will try again at next scheduled time.")
                import traceback
                traceback.print_exc()
                return  # Give up after max retries

# Run immediately on boot
logger.info("=" * 60)
logger.info("BOOT: Running initial scrape on container startup...")
logger.info(f"Configuration:")
logger.info(f"  URL: {URL}")
logger.info(f"  Output: {OUTPUT_PATH_HTML}")
logger.info(f"  Timezone: {TIMEZONE}")
logger.info(f"  Schedule: {SCHEDULE_TIME}")
logger.info(f"  Weekend Fallback: {WEEKEND_FALLBACK}")
logger.info("=" * 60)
job()

# Schedule daily job
logger.info("=" * 60)
logger.info(f"Scheduling daily scrape at {SCHEDULE_TIME} {TIMEZONE}...")
schedule.every().day.at(SCHEDULE_TIME).do(job)
logger.info("=" * 60)

# Display current time and next scheduled run
now_tz = datetime.now(TZ)
logger.info(f"Current {TIMEZONE} time: {now_tz.strftime('%Y-%m-%d %H:%M:%S %Z')}")
logger.info("Scheduler active. Waiting for scheduled jobs...")
logger.info("=" * 60)

# Main loop - check every minute for scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(60)

