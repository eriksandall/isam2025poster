"""
Makerspace Usage Analysis Utilities

This module provides functions for analyzing makerspace usage data across semesters,
with a focus on comparing similar weeks across different semesters to identify trends
and patterns in usage.

Functions:
    load_semester_data:       Loads the enhanced dataset with semester information
    analyze_weekly_usage:     Analyzes usage by week across semesters
    calculate_percent_change: Calculates percent change between consecutive values
    identify_peak_weeks:      Identifies weeks with highest and lowest usage
    print_summary_stats:      Prints summary statistics to console
    save_summary_stats:       Saves summary statistics to a CSV file
"""

import pandas as pd


def load_semester_data(file_path):
    """
    Loads the enhanced dataset containing semester information.
    
    Args:
        file_path (str): Path to the CSV file with enhanced data
        
    Returns:
        pandas.DataFrame: DataFrame with timestamp and semester data
    """
    # Load the data, ensuring timestamp is parsed correctly
    df = pd.read_csv(file_path, parse_dates=["Timestamp"])
    
    # Ensure Semester_Week is an integer
    df["Semester_Week"] = df["Semester_Week"].astype(int)
    
    print(f"Loaded {len(df)} records from {file_path}")
    print(f"Semester range: {df['Semester'].nunique()} semesters")
    print(f"Week range: {df['Semester_Week'].min()} to {df['Semester_Week'].max()}")
    
    return df


def analyze_weekly_usage(df):
    """
    Analyzes weekly usage patterns across semesters.
    
    Args:
        df (pandas.DataFrame): DataFrame with timestamp and semester data
        
    Returns:
        tuple: (weekly_counts, weekly_stats)
            - weekly_counts: DataFrame with counts by semester and week
            - weekly_stats:  DataFrame with statistics by week across semesters
    """
    # Count entries by semester and week
    weekly_counts = df.groupby(["Semester", "Semester_Week"]).size().reset_index(name="Count")
    
    # Aggregate data across semesters by week
    weekly_stats = weekly_counts.groupby("Semester_Week").agg(
        avg_usage=("Count", "mean"),
        std_usage=("Count", "std"),
        min_usage=("Count", "min"),
        max_usage=("Count", "max"),
        num_semesters=("Count", "count")
    )
    
    # Handle NaN values in std_usage (occurs when there's only one value)
    weekly_stats["std_usage"] = weekly_stats["std_usage"].fillna(0)
    
    # Calculate percent change from previous week
    weekly_stats["percent_change"] = calculate_percent_change(weekly_stats["avg_usage"])
    
    return weekly_counts, weekly_stats


def calculate_percent_change(series):
    """
    Calculates percent change between consecutive values in a series.
    
    Args:
        series (pandas.Series): Series of values
        
    Returns:
        pandas.Series: Series of percent changes
    """
    # Calculate percent change, with NaN for the first entry
    percent_change = series.pct_change() * 100
    
    # Round to two decimal places
    percent_change = percent_change.round(2)
    
    return percent_change


def identify_peak_weeks(weekly_stats):
    """
    Identifies weeks with highest and lowest average usage.
    
    Args:
        weekly_stats (pandas.DataFrame): DataFrame with weekly statistics
        
    Returns:
        tuple: (highest_week, lowest_week) 
            - Tuples containing (week_number, avg_usage)
    """
    # Find week with highest average usage
    highest_idx = weekly_stats["avg_usage"].idxmax()
    highest_week = (highest_idx, weekly_stats.loc[highest_idx, "avg_usage"])
    
    # Find week with lowest average usage
    # Filter to only include weeks that appear in most semesters (at least 75%)
    common_weeks = weekly_stats[weekly_stats["num_semesters"] >= 0.75 * weekly_stats["num_semesters"].max()]
    lowest_idx = common_weeks["avg_usage"].idxmin()
    lowest_week = (lowest_idx, weekly_stats.loc[lowest_idx, "avg_usage"])
    
    return highest_week, lowest_week


def print_summary_stats(weekly_stats, highest_week, lowest_week):
    """
    Prints summary statistics to the console.
    
    Args:
        weekly_stats (pandas.DataFrame): DataFrame with weekly statistics
        highest_week (tuple):            Week with highest usage (week_number, avg_usage)
        lowest_week (tuple):             Week with lowest usage (week_number, avg_usage)
    """
    print("\n===== MAKERSPACE USAGE SUMMARY STATISTICS =====")
    print(f"Number of weeks analyzed: {len(weekly_stats)}")
    print(f"Average weekly usage across all weeks: {weekly_stats['avg_usage'].mean():.2f}")
    print(f"Standard deviation across all weeks: {weekly_stats['avg_usage'].std():.2f}")
    print("\n--- Peak Weeks ---")
    print(f"Highest usage: Week {highest_week[0]} with average of {highest_week[1]:.2f} entries")
    print(f"Lowest usage: Week {lowest_week[0]} with average of {lowest_week[1]:.2f} entries")
    
    print("\n--- Weekly Trends ---")
    print("Weeks with highest percent increase:")
    top_increases = weekly_stats.sort_values("percent_change", ascending=False).head(3)
    for week, row in top_increases.iterrows():
        print(f"  Week {week}: {row['percent_change']:.2f}% increase from previous week")
    
    print("\nWeeks with highest percent decrease:")
    top_decreases = weekly_stats.sort_values("percent_change").head(3)
    for week, row in top_decreases.iterrows():
        print(f"  Week {week}: {row['percent_change']:.2f}% decrease from previous week")


def save_summary_stats(weekly_stats, weekly_counts, output_dir):
    """
    Saves summary statistics to CSV files.
    
    Args:
        weekly_stats (pandas.DataFrame):  DataFrame with weekly statistics
        weekly_counts (pandas.DataFrame): DataFrame with counts by semester and week
        output_dir (str):                Base path for output files
    """
    # Save weekly statistics across all semesters
    stats_path = f"{output_dir}/weekly_stats.csv"
    weekly_stats.to_csv(stats_path)
    print(f"Saved weekly statistics to {stats_path}")
    
    # Save detailed weekly counts by semester
    counts_path = f"{output_dir}/weekly_counts.csv"
    weekly_counts.to_csv(counts_path, index=False)
    print(f"Saved weekly counts by semester to {counts_path}")
    
    # Create a pivot table for easier visualization
    pivot_counts = weekly_counts.pivot(index="Semester_Week", columns="Semester", values="Count")
    pivot_path = f"{output_dir}/pivot_table.csv"
    pivot_counts.to_csv(pivot_path)
    print(f"Saved pivot table to {pivot_path}")


def analyze_makerspace_usage(file_path, output_dir=None):
    """
    Main function to analyze makerspace usage data.
    
    Args:
        file_path (str):             Path to the CSV file with enhanced data
        output_dir (str, optional):  Base path for output files
        
    Returns:
        tuple: (weekly_counts, weekly_stats) 
            - DataFrames with analysis results
    """
    # Step 1: Load the data
    df = load_semester_data(file_path)
    
    # Steps 2-4: Analyze weekly usage
    weekly_counts, weekly_stats = analyze_weekly_usage(df)
    
    # Step 5: Identify peak weeks
    highest_week, lowest_week = identify_peak_weeks(weekly_stats)
    
    # Step 6: Print summary statistics
    print_summary_stats(weekly_stats, highest_week, lowest_week)
    
    # Step 7: Save statistics to files if output path is provided
    if output_dir:
        save_summary_stats(weekly_stats, weekly_counts, output_dir)
    
    return weekly_counts, weekly_stats


if __name__ == '__main__':
    # Run the analysis on the enhanced dataset
    enhanced_df_path = "data/enhanced_log.csv"
    usage_analysis_dir = "analysis"
    
    weekly_counts, weekly_stats = analyze_makerspace_usage(enhanced_df_path, usage_analysis_dir)
    
    # Display samples of results
    print("\nSample of weekly counts by semester:")
    print(weekly_counts.sample(5))
    
    print("\nSample of weekly statistics across semesters:")
    print(weekly_stats.sample(5))