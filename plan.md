# Tarkov Hideout ROI Scheduler

## Concept
A dashboard to maximize Hideout profitability by calculating real-time ROI and Opportunity Cost.

## Features
1.  **Real-time Profit Calculator**:
    *   Fetches live Flea Market prices.
    *   Calculates crafting costs vs. selling components (Opportunity Cost).
    *   Identifies the most profitable crafts per hour.

2.  **Smart Queue Planner**:
    *   Input: "Time available to play" (e.g., 4 hours).
    *   Output: Optimal sequence of crafts (e.g., Short craft -> Short craft -> Long overnight craft).

3.  **Dashboard UI**:
    *   Visual representation of profits.
    *   "Do Not Craft" warnings for negative opportunity costs.
    *   Queue visualization.

## Tech Stack
*   **Logic/Backend**: Python (Data fetching, calculations).
*   **Data Source**: Tarkov.dev API (GraphQL).
*   **Frontend**: HTML/CSS/JS (Modern, "Glassmorphism" design).

## Workflow
1.  `fetch_data.py`: Retrieves hideout recipes and current market prices.
2.  `analyzer.py`: Processes data to find ROI and build queues.
3.  `dashboard/`: Web interface to display the results.
