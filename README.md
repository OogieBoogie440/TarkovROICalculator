# Tarkov Hideout ROI Scheduler

A real-time dashboard to calculate the most profitable Hideout crafts in Escape from Tarkov.

## Features
- **Live Market Data**: Fetches prices from Tarkov-Market and Tarkov.dev.
- **Smart Scheduling**: Suggests crafting queues based on your available playtime (2h, 4h, 8h).
- **ROI Analysis**: Calculates true profit per hour, accounting for fuel and component costs.

## How to Run Locally
1. Install Python.
2. Run `pip install -r requirements.txt`.
3. Run `python src/main.py`.
4. Open `dashboard/index.html` in your browser.

## How to Host (Free)
1. Fork this repo to GitHub.
2. Go to **Settings > Secrets and variables > Actions**.
3. Add a New Repository Secret named `TARKOV_MARKET_API_KEY` with your API key.
4. Go to **Settings > Pages**.
5. Set Source to `Deploy from a branch` and select `main` (or `master`) and the `/dashboard` folder (if possible) or just root.
   * *Note: You might need to move index.html to root or configure the build source.*
