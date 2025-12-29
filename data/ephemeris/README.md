# Swiss Ephemeris Data Files

This directory should contain the Swiss Ephemeris data files for accurate planet calculations.

## Required Files

For basic functionality, download:
- `sepl_18.se1` - Main planets (1800-2400)
- `semo_18.se1` - Moon (1800-2400)

For asteroids (optional):
- `seas_18.se1` - Asteroids

## Download Instructions

1. Visit: https://www.astro.com/ftp/swisseph/ephe/
2. Download the required `.se1` files
3. Place them in this directory

## Alternative: Environment Variable

You can also set the `EPHE_PATH` environment variable to point to your existing ephemeris files location.
