"""
Makerspace Usage Visualization Utilities

This module provides functions for visualizing makerspace usage trends,
focusing on weekly patterns across semesters with both line charts and
heatmaps for Spring, Fall, and combined semester analyses.

Functions:
    plot_weekly_averages:    Creates line charts of average weekly usage
    create_usage_heatmaps:   Creates heatmaps showing usage intensity by week
    visualize_usage_trends:  Main function to generate all visualizations
"""


import matplotlib.pyplot as plt
import seaborn as sns
import os
from analyze_usage import load_semester_data, analyze_weekly_usage


def plot_weekly_averages(weekly_counts, output_dir="img"):
    """
    Creates line charts showing average weekly usage across semesters.
    
    Args:
        weekly_counts (pandas.DataFrame): DataFrame with counts by semester and week
        output_dir (str):                 Directory to save the output images
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract season (Fall/Spring) from semester name
    weekly_counts['Season'] = weekly_counts['Semester'].str.contains('Fall').map({True: 'Fall', False: 'Spring'})
    
    # 1. Plot for Spring semesters
    spring_data = weekly_counts[weekly_counts['Season'] == 'Spring']
    spring_pivot = spring_data.pivot(index="Semester_Week", columns="Semester", values="Count")
    
    plt.figure(figsize=(12, 6))
    spring_pivot.plot(marker='o', linestyle='-', ax=plt.gca())
    plt.title('Average Weekly Usage - Spring Semesters')
    plt.xlabel('Week of Semester')
    plt.ylabel('Number of Makerspace Visits')
    plt.grid(True, alpha=0.3)
    plt.legend(title='Semester')
    
    # Set integer ticks on x-axis
    ax = plt.gca()
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/spring_weekly_usage.png", dpi=300)
    plt.close()
    
    # 2. Plot for Fall semesters
    fall_data = weekly_counts[weekly_counts['Season'] == 'Fall']
    fall_pivot = fall_data.pivot(index="Semester_Week", columns="Semester", values="Count")
    
    plt.figure(figsize=(12, 6))
    fall_pivot.plot(marker='o', linestyle='-', ax=plt.gca())
    plt.title('Average Weekly Usage - Fall Semesters')
    plt.xlabel('Week of Semester')
    plt.ylabel('Number of Makerspace Visits')
    plt.grid(True, alpha=0.3)
    plt.legend(title='Semester')
    
    # Set integer ticks on x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/fall_weekly_usage.png", dpi=300)
    plt.close()
    
    # 3. Plot for all semesters combined by season
    # Calculate average by season and week
    season_avg = weekly_counts.groupby(['Season', 'Semester_Week'])['Count'].mean().reset_index()
    season_pivot = season_avg.pivot(index='Semester_Week', columns='Season', values='Count')
    
    plt.figure(figsize=(12, 6))
    season_pivot.plot(marker='o', linestyle='-', ax=plt.gca())
    plt.title('Average Weekly Usage - Fall vs Spring Semesters')
    plt.xlabel('Week of Semester')
    plt.ylabel('Average Number of Makerspace Visits')
    plt.grid(True, alpha=0.3)
    plt.legend(title='Season')
    
    # Set integer ticks on x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/combined_weekly_usage.png", dpi=300)
    plt.close()
    
    print(f"Line charts saved to {output_dir}/")


def create_usage_heatmaps(weekly_counts, output_dir="img"):
    """
    Creates heatmaps showing the intensity of usage across weeks.
    
    Args:
        weekly_counts (pandas.DataFrame): DataFrame with counts by semester and week
        output_dir (str):                 Directory to save the output images
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract season (Fall/Spring) from semester name
    weekly_counts['Season'] = weekly_counts['Semester'].str.contains('Fall').map({True: 'Fall', False: 'Spring'})
    weekly_counts['Year'] = weekly_counts['Semester'].str.extract(r'(\d{4})').astype(int)
    
    # 1. Heatmap for Spring semesters
    spring_data = weekly_counts[weekly_counts['Season'] == 'Spring']
    spring_pivot = spring_data.pivot(index="Semester", columns="Semester_Week", values="Count")
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(spring_pivot, cmap="YlGnBu", annot=False, fmt=".0f", 
                cbar_kws={'label': 'Number of Visits'})
    plt.title('Usage Intensity by Week - Spring Semesters')
    plt.xlabel('Week of Semester')
    plt.ylabel('Semester')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/spring_heatmap.png", dpi=300)
    plt.close()
    
    # 2. Heatmap for Fall semesters
    fall_data = weekly_counts[weekly_counts['Season'] == 'Fall']
    fall_pivot = fall_data.pivot(index="Semester", columns="Semester_Week", values="Count")
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(fall_pivot, cmap="YlGnBu", annot=False, fmt=".0f", 
                cbar_kws={'label': 'Number of Visits'})
    plt.title('Usage Intensity by Week - Fall Semesters')
    plt.xlabel('Week of Semester')
    plt.ylabel('Semester')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/fall_heatmap.png", dpi=300)
    plt.close()
    
    # 3. Combined heatmap showing average by season
    # Create a pivot table with Week as columns, Season as rows, and average count as values
    season_avg = weekly_counts.groupby(['Season', 'Semester_Week'])['Count'].mean().reset_index()
    season_pivot = season_avg.pivot(index='Season', columns='Semester_Week', values='Count')
    
    plt.figure(figsize=(14, 4))
    sns.heatmap(season_pivot, cmap="YlGnBu", annot=True, fmt=".1f", 
                cbar_kws={'label': 'Average Number of Visits'})
    plt.title('Average Usage Intensity by Week - Fall vs Spring')
    plt.xlabel('Week of Semester')
    plt.ylabel('Season')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/season_heatmap.png", dpi=300)
    plt.close()
    
    # 4. Year-over-year heatmap (all semesters)
    # Group by year and week, take average if multiple semesters in a year
    year_week_avg = weekly_counts.groupby(['Year', 'Semester_Week'])['Count'].mean().reset_index()
    year_pivot = year_week_avg.pivot(index='Year', columns='Semester_Week', values='Count')
    
    plt.figure(figsize=(14, 10))
    sns.heatmap(year_pivot, cmap="YlGnBu", annot=False, fmt=".0f", 
                cbar_kws={'label': 'Average Number of Visits'})
    plt.title('Usage Intensity by Week - Year over Year')
    plt.xlabel('Week of Semester')
    plt.ylabel('Year')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/yearly_heatmap.png", dpi=300)
    plt.close()
    
    print(f"Heatmaps saved to {output_dir}/")


def visualize_usage_trends(file_path, output_dir):
    """
    Main function to generate all visualizations for makerspace usage trends.
    
    Args:
        file_path (str):  Path to the CSV file with enhanced data
        output_dir (str): Directory to save the output images
    """
    # Load data and perform weekly aggregation
    df = load_semester_data(file_path)
    weekly_counts, weekly_stats = analyze_weekly_usage(df)
    
    # Generate line charts
    plot_weekly_averages(weekly_counts, output_dir)
    
    # Generate heatmaps
    create_usage_heatmaps(weekly_counts, output_dir)
    
    print(f"All visualizations have been saved to the {output_dir}/ directory")


if __name__ == "__main__":
    # Execute visualization functions
    visualize_usage_trends(file_path="data/enhanced_log.csv", output_dir="img")