# Flowerpot Flow Report Dashboard

This is an internal analytics tool created to process and summarize product flow data for the Flowerpot team. It uses a Microsoft Excel `.xlsx` dataset to generate insights on client progress through the engagement pipeline.

## Overview

The dashboard reads from a preformatted Excel file and outputs key summaries:

- Total projects analyzed
- Client and partner participation
- Breakdown by engagement stages (e.g., Early Conversation, Pilot, Contract)
- Conversion rates across stages
- Reminders for client follow-up

## Features

- **Excel File Input**: Processes `.xlsx` files instead of `.csv`
- **Stage Analysis**: Understand how many clients are in each product stage
- **Conversion Metrics**: Track progress across engagement stages
- **Follow-Up Suggestions**: Flags clients who may need re-engagement

## Tech Stack

- Python 3.x
- pandas
- openpyxl (for reading `.xlsx` files)

## How It Works

1. Prompts user for the Excel file path
2. Loads the sheet using `pandas.read_excel()`
3. Parses relevant columns (e.g., `Client Name`, `Stage`, `Product`)
4. Generates a dashboard-style textual summary using the `print_stats()` function
5. Optionally allows saving results to a `.txt` file

## Getting Started

### Prerequisites
Install the necessary libraries:

```bash
pip install pandas openpyxl

### File Structure 
.
├── flow_report.py                         # Main Python script
├── Copy of sample_post_trade_data.xlsx   # Sample input file
└── README.md                              # Project documentation

