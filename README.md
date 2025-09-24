# Flow Report Dashboard

An internal analytics tool for processing and visualizing post-trade data. The dashboard reads from an Excel dataset and provides interactive charts to help teams explore trading activity across clients, venues, regions, and timeframes.

## Overview
The dashboard allows users to:
- Upload and analyze `.xlsx` post-trade data  
- Filter results by timeframe (day, week, month, year), side (buy/sell), venue type, region, client, ticker, and date  
- Visualize trading activity through interactive charts, including:
  - Traded value by side (Buy vs Sell)  
  - Traded value by sector  
  - Traded value by client  
  - Traded value over time  
  - Traded value by region  
  - Traded value by execution venue (Lit vs Dark)  
  - Traded value by ticker and destination  

A simple Tkinter login screen wraps the app for local use.  

## Tech Stack
- **Backend:** Python 3.x, pandas, openpyxl  
- **Frontend:** Dash (Plotly), Tkinter  
- **Visualization:** Plotly Express & Graph Objects  

## How It Works
1. User logs in via a simple Tkinter GUI.  
2. The app loads a specified Excel file from the Downloads folder.  
3. Data is parsed and filtered based on dropdown selections.  
4. Interactive Dash charts are generated to explore trade activity.  
5. The dashboard automatically opens in the browser.  

## Getting Started
### Prerequisites
- Python 3.7+  
- Required libraries:  
  ```bash
  pip install pandas openpyxl dash plotly


### File Structure
├── flow_report.py                       # Main Python script
├── Copy of sample_post_trade_data.xlsx  # Sample input file
└── README.md                            # Project documentation

