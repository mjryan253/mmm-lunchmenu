# Quick Start Guide

Get MMM-LunchMenu up and running in 5 minutes!

## Prerequisites

- MagicMirror² installed and running
- Docker and Docker Compose (for scraper service)
- Python 3.11+ (if running scraper standalone)

## Installation Steps

### 1. Install the Module

```bash
cd ~/MagicMirror/modules
git clone https://github.com/mjryan253/mmm-lunchmenu.git MMM-LunchMenu
```

### 2. Set Up the Scraper

```bash
cd MMM-LunchMenu/scraper
cp docker-compose.example.yml docker-compose.yml
```

Edit `docker-compose.yml` and set your menu URL:
```yaml
environment:
  - MENU_URL=https://your-menu-website.com
```

### 3. Start the Scraper

```bash
docker-compose up -d
```

### 4. Create Output Directory

The module needs a place to read the menu file. Create the directory:

```bash
mkdir -p ~/MagicMirror/modules/MMM-LunchMenu/public
```

Update your `docker-compose.yml` to mount this directory:
```yaml
volumes:
  - ../public:/output
```

### 5. Add to MagicMirror Config

Edit `~/MagicMirror/config/config.js` and add:

```javascript
{
    module: 'MMM-LunchMenu',
    position: 'bottom_left',
    header: 'School Lunch',
    config: {
        menuUrl: '/modules/MMM-LunchMenu/public/lunch_menu.html',
        updateInterval: 3600000,
        width: '600px',
        height: '400px'
    }
}
```

### 6. Restart MagicMirror

```bash
pm2 restart mm  # or however you run MagicMirror
```

## Verify It's Working

1. Check scraper logs: `docker-compose logs -f`
2. Verify HTML file exists: `ls ~/MagicMirror/modules/MMM-LunchMenu/public/`
3. Check MagicMirror browser console for errors

## Customization

See [README.md](README.md) for detailed customization instructions, including:
- Adjusting regex patterns for your website
- Changing timezone and schedule
- Modifying HTML styling
- Handling different menu formats

## Troubleshooting

**Menu not showing?**
- Check scraper logs: `docker-compose logs menu-scraper`
- Verify file exists and is readable
- Check browser console for errors

**Scraper not working?**
- Test URL manually: `curl https://your-menu-website.com`
- Check if website requires JavaScript (may need Playwright instead)
- Adjust regex patterns in docker-compose.yml

For more help, see the full [README.md](README.md).

