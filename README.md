# ISAM 2025 Makerspace Usage Analysis

This repository contains the code and data analysis for the research poster to be presented at the International Symposium of Academic Makerspaces (ISAM) 2025. The goal of this project is to analyze makerspace usage data from Spring 2015 to Spring 2024 to identify trends and patterns in overall usage and equipment popularity.

## Description

The analysis focuses on two main areas:
1. **Overall Usage Trends**: Analyzing total weekly makerspace usage aggregated into a single time series, excluding COVID closure weeks, and identifying trends over time.
2. **Equipment Popularity**: Analyzing the usage of different equipment and equipment types over time, comparing their popularity, and identifying trends in equipment usage rankings.

## Usage Instructions

To run the analysis and generate visualizations, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/eriksandall/isam2025poster.git
   cd isam2025poster
   ```

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare the data**:
   - Ensure you have the raw makerspace usage data in the `data` directory.
   - Run the data preparation script to clean and enhance the dataset:
     ```bash
     python prepare_data.py
     ```

4. **Analyze overall usage trends**:
   - Run the usage analysis script to generate weekly usage statistics and visualizations:
     ```bash
     python analyze_usage.py
     ```

5. **Analyze equipment popularity**:
   - Run the equipment analysis script to generate equipment usage statistics and visualizations:
     ```bash
     python analyze_equipment.py
     ```

6. **Visualize the results**:
   - Run the visualization scripts to generate charts and heatmaps:
     ```bash
     python visualize_usage.py
     python visualize_equipment.py
     ```