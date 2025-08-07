"""
Equipment Usage Analysis Utilities

This module provides functions for analyzing equipment popularity over time,
with a focus on comparing usage patterns across semesters and identifying trends
in equipment utilization for both individual equipment types and categories.

Functions:
    load_equipment_data:      Loads the enhanced dataset with equipment information
    analyze_equipment_usage:  Analyzes usage by equipment types and categories
    calculate_rankings:       Calculates popularity rankings over time
    identify_peak_usage:      Identifies weeks with highest/lowest usage
    print_equipment_stats:    Prints key statistics about equipment usage
    save_equipment_stats:     Saves the computed statistics to CSV files
"""


import pandas as pd
import os
from analyze_usage import load_semester_data, calculate_percent_change


def load_equipment_data(file_path):
    """
    Loads the enhanced dataset containing equipment usage information and filters out irrelevant entries.
    
    Args:
        file_path (str): Path to the CSV file with enhanced data
        
    Returns:
        pandas.DataFrame: DataFrame with timestamp, semester, equipment type, and category data
    """
    # Load the data using the existing function
    df = load_semester_data(file_path)
    
    # Verify that equipment information is present
    if 'Access Type' not in df.columns:
        raise ValueError("'Access Type' column not found in the dataset")
        
    if 'Equipment_Category' not in df.columns:
        raise ValueError("'Equipment_Category' column not found in the dataset. Make sure to enhance the dataset with equipment categories first.")
    
    # Filter out irrelevant entries
    df = df[(df['Access Type'] != 'Jacobs MakerPass Access') & (df['Equipment_Category'] != 'Entry')]
    
    # Print summary of equipment data
    print(f"Equipment types in dataset: {df['Access Type'].nunique()}")
    print(f"Equipment categories in dataset: {df['Equipment_Category'].nunique()}")
    print(f"\nTop 5 equipment types: {df['Access Type'].value_counts().head(5).to_dict()}")
    print(f"\nEquipment categories: {df['Equipment_Category'].value_counts().to_dict()}")
    
    return df


def analyze_equipment_usage(df, equipment_field):
    """
    Analyzes equipment usage by individual equipment or equipment category, semester, and week.
    
    Args:
        df (pandas.DataFrame): DataFrame with timestamp, semester, and equipment data
        equipment_field (str): Field to use for equipment analysis ('Access Type' or 'Equipment_Category')
        
    Returns:
        tuple: (equipment_counts, equipment_pct, equipment_stats, pct_changes)
            - equipment_counts: DataFrame with counts by equipment, semester, and week
            - equipment_pct:    DataFrame with percent of total usage by equipment, semester, week
            - equipment_stats:  DataFrame with statistics by equipment and week across semesters
            - pct_changes:      DataFrame with percent changes week-to-week by equipment
    """
    # Validate the equipment fields
    if equipment_field not in ['Access Type', 'Equipment_Category']:
        raise ValueError("equipment_field must be 'Access Type' or 'Equipment_Category'")
    
    # Filter out irrelevant entries
    df = df[(df['Access Type'] != 'Jacobs MakerPass Access') & (df['Equipment_Category'] != 'Entry')]
    
    # Calculate total equipment usage by equipment/equipment category, semester, and week
    equipment_counts = df.groupby([equipment_field, 'Semester', 'Semester_Week']).size().reset_index(name='Count')
    
    # Calculate total counts per semester and week (for percentage calculations)
    total_counts = df.groupby(['Semester', 'Semester_Week']).size().reset_index(name='Total')
    
    # Merge to get totals alongside equipment counts
    merged_counts = pd.merge(
        equipment_counts, 
        total_counts, 
        on=['Semester', 'Semester_Week'], 
        how='left'
    )
    
    # Calculate percentage of overall usage that each equipment/equipment category represents
    merged_counts['Percentage'] = (merged_counts['Count'] / merged_counts['Total']) * 100
    equipment_pct = merged_counts[[equipment_field, 'Semester', 'Semester_Week', 'Count', 'Total', 'Percentage']]
    
    # Aggregate data across semesters by equipment/equipment category and week
    equipment_stats = equipment_counts.groupby([equipment_field, 'Semester_Week']).agg(
        avg_usage=('Count', 'mean'),
        std_usage=('Count', 'std'),
        min_usage=('Count', 'min'),
        max_usage=('Count', 'max'),
        num_semesters=('Count', 'count')
    ).reset_index()
    
    # Handle NaN values in std_usage (occurs when there's only one value)
    equipment_stats['std_usage'] = equipment_stats['std_usage'].fillna(0)
    
    # Compute percent change from previous week for each equipment type
    # First, create a pivot to get weeks as columns for each equipment and semester
    pivot = equipment_counts.pivot_table(
        index=[equipment_field, 'Semester'], 
        columns='Semester_Week', 
        values='Count'
    ).reset_index()
    
    # Then calculate percent change for each row (each equipment-semester combination)
    pct_changes = pivot.copy()
    for col in pct_changes.columns:
        if isinstance(col, int) and col > 1:  # Only process week columns, starting from week 2
            prev_col = col - 1
            if prev_col in pct_changes.columns:
                # Calculate percentage change from previous week
                pct_changes[f'pct_change_{col}'] = ((pct_changes[col] - pct_changes[prev_col]) / pct_changes[prev_col] * 100)
    
    # Clean up the pivot and percent change DataFrames
    pct_changes = pct_changes.drop(columns=[col for col in pct_changes.columns if isinstance(col, int)])
    
    return equipment_counts, equipment_pct, equipment_stats, pct_changes


def calculate_rankings(equipment_pct, equipment_field):
    """
    Calculates individual equipment or equipment category popularity rankings over time.
    
    Args:
        equipment_pct (pandas.DataFrame): DataFrame with percentage usage data
        equipment_field (str): Field to use for equipment analysis
        
    Returns:
        tuple: (rankings, top_equipment, top_pivot, consistency)
            - rankings:      DataFrame with equipment rankings by semester and week
            - top_equipment: DataFrame with the top equipment for each semester and week
            - top_pivot:     Pivot table showing how top equipment changes week by week
            - consistency:   DataFrame with ranking consistency metrics
    """
    # Get the ranking of each equipment type for each semester and week
    rankings = equipment_pct.copy()
    
    # Add a rank column (1 = most used)
    rankings['Rank'] = rankings.groupby(['Semester', 'Semester_Week'])['Count'].rank(ascending=False, method='min')
    
    # Identify the top equipment for each semester and week
    top_equipment = rankings[rankings['Rank'] == 1].copy()
    
    try:
        # Create a pivot table to easily see how the top equipment changes week by week
        # In case of ties (multiple items with rank 1), take the first one
        # First, create a temporary ID to make each row unique
        top_equipment_deduped = top_equipment.copy()
        
        # If there are duplicates, keep only the one with the highest count
        top_equipment_deduped = top_equipment_deduped.sort_values(
            ['Semester', 'Semester_Week', 'Count'], 
            ascending=[True, True, False]
        ).drop_duplicates(['Semester', 'Semester_Week'])
        
        # Now create the pivot table with the deduplicated data
        top_pivot = top_equipment_deduped.pivot(
            index='Semester', 
            columns='Semester_Week', 
            values=equipment_field
        )
    except Exception as e:
        print(f"Warning: Could not create pivot table: {e}")
        # Create an empty DataFrame as a fallback
        top_pivot = pd.DataFrame()
    
    # Analyze consistency of rankings
    consistency = rankings.groupby(equipment_field)['Rank'].agg(['mean', 'std', 'min', 'max']).reset_index()
    consistency = consistency.sort_values('mean')  # Sort by average rank
    
    return rankings, top_equipment, top_pivot, consistency


def identify_peak_usage(equipment_stats, equipment_field):
    """
    Identifies weeks with highest and lowest usage for each individual equipment or equipment category.
    
    Args:
        equipment_stats (pandas.DataFrame): DataFrame with equipment usage statistics
        equipment_field (str):              Field to use for equipment analysis
        
    Returns:
        tuple: (peak_weeks, low_weeks)
            - peak_weeks: DataFrame showing peak usage week for each equipment type
            - low_weeks:  DataFrame showing lowest usage week for each equipment type
    """
    try:
        # Collect rows in lists (pd.contact() will be deprecated in future versions)
        peak_rows = []
        low_rows = []
        
        # Process each equipment/equipment category individually to find peak usage
        for equip_type in equipment_stats[equipment_field].unique():
            # Get data for this equipment/equipment category
            equip_data = equipment_stats[equipment_stats[equipment_field] == equip_type]
            
            # Skip if no data
            if equip_data.empty:
                continue
                
            try:
                # Find week with highest usage
                max_usage_idx = equip_data['avg_usage'].idxmax()
                # Get the row with max usage and add to results
                peak_rows.append(equipment_stats.loc[max_usage_idx].to_dict())
            except Exception as e:
                print(f"  Warning: Could not find peak week for {equip_type}: {e}")
        
        # For lowest usage, apply the 75% threshold
        # Get the maximum number of semesters for each equipment/equipment category
        semester_counts = equipment_stats.groupby(equipment_field)['num_semesters'].max().to_dict()
        
        # Process each equipment/equipment cateogry individually to find low usage
        for equip_type in equipment_stats[equipment_field].unique():
            # Get data for this equipment/equipment category
            equip_data = equipment_stats[equipment_stats[equipment_field] == equip_type]
            
            # Skip if no data
            if equip_data.empty:
                continue
            
            # Apply the 75% threshold to this equipment/equipment category only
            max_semesters = semester_counts.get(equip_type, 0)
            if max_semesters == 0:
                continue
                
            # Filter to weeks with good coverage
            common_weeks_data = equip_data[equip_data['num_semesters'] >= 0.75 * max_semesters]
            
            # Skip if no weeks meet the threshold
            if common_weeks_data.empty:
                print(f"  Note: No weeks with sufficient data for {equip_type} (75% threshold)")
                continue
                
            try:
                # Find week with lowest usage that meets threshold
                min_usage_idx = common_weeks_data['avg_usage'].idxmin()
                # Get the row with min usage and add to results
                low_rows.append(equipment_stats.loc[min_usage_idx].to_dict())
            except Exception as e:
                print(f"  Warning: Could not find low week for {equip_type}: {e}")
        
        # Create DataFrames from collected rows
        peak_weeks = pd.DataFrame(peak_rows) if peak_rows else pd.DataFrame(columns=equipment_stats.columns)
        low_weeks = pd.DataFrame(low_rows) if low_rows else pd.DataFrame(columns=equipment_stats.columns)
        
        # Report summary
        print(f"Found peak usage weeks for {len(peak_weeks)} out of {len(equipment_stats[equipment_field].unique())} {equipment_field} types")
        print(f"Found low usage weeks for {len(low_weeks)} out of {len(equipment_stats[equipment_field].unique())} {equipment_field} types")
        
        return peak_weeks, low_weeks
    
    except Exception as e:
        print(f"Error in identify_peak_usage: {e}")
        print(f"Equipment field: {equipment_field}")
        print(f"Number of unique equipment types: {len(equipment_stats[equipment_field].unique())}")
        print(f"Equipment stats shape: {equipment_stats.shape}")
        
        # Return empty DataFrames as a fallback
        empty_df = pd.DataFrame(columns=equipment_stats.columns)
        return empty_df, empty_df


def print_equipment_stats(equipment_stats, peak_weeks, low_weeks, top_pivot, consistency, equipment_field):
    """
    Prints key statistics about equipment usage.
    
    Args:
        equipment_stats (pandas.DataFrame): Statistics by equipment and week
        peak_weeks (pandas.DataFrame):      Peak usage weeks by equipment
        low_weeks (pandas.DataFrame):       Low usage weeks by equipment
        top_pivot (pandas.DataFrame):       Pivot table showing top equipment by week
        consistency (pandas.DataFrame):     Equipment ranking consistency metrics
        equipment_field (str):              Field used for equipment analysis
    """
    print(f"\n===== {equipment_field.upper()} USAGE SUMMARY STATISTICS =====")
    
    # Print overall equipment popularity
    print(f"\n--- Overall {equipment_field} Popularity ---")
    avg_by_equipment = equipment_stats.groupby(equipment_field)['avg_usage'].mean().sort_values(ascending=False)
    for i, (equipment, avg) in enumerate(avg_by_equipment.items(), 1):
        if i <= 5:  # Print top 5
            print(f"{i}. {equipment}: {avg:.2f} average uses")
    
    # Print peak usage weeks
    print(f"\n--- Peak Usage Weeks by {equipment_field} ---")
    for _, row in peak_weeks.sort_values('avg_usage', ascending=False).head(5).iterrows():
        print(f"{row[equipment_field]}: Week {row['Semester_Week']} with {row['avg_usage']:.2f} average uses")
    
    # Print low usage weeks
    print(f"\n--- Lowest Usage Weeks by {equipment_field} ---")
    for _, row in low_weeks.sort_values('avg_usage').head(5).iterrows():
        print(f"{row[equipment_field]}: Week {row['Semester_Week']} with {row['avg_usage']:.2f} average uses")
    
    # Print equipment ranking consistency
    print(f"\n--- {equipment_field} Ranking Consistency ---")
    print(f"Most consistently popular {equipment_field} (lowest rank = highest usage):")
    for _, row in consistency.head(3).iterrows():
        print(f"{row[equipment_field]}: Avg Rank {row['mean']:.2f} (min: {row['min']}, max: {row['max']})")
    
    # Print information about changes in top equipment
    print(f"\n--- Weekly Changes in Top {equipment_field} ---")
    semester_count = len(top_pivot)
    changes = 0
    for week in range(2, top_pivot.shape[1] + 1):
        if week in top_pivot.columns and week - 1 in top_pivot.columns:
            diff_count = (top_pivot[week] != top_pivot[week - 1]).sum()
            if diff_count > 0:
                changes += 1
                print(f"Week {week-1} to Week {week}: {diff_count} semesters changed top {equipment_field} ({diff_count/semester_count:.1%})")


def save_equipment_stats(equipment_counts, equipment_pct, equipment_stats, 
                         rankings, peak_weeks, low_weeks, 
                         equipment_field, output_dir="analysis"):
    """
    Saves the computed equipment statistics to CSV files.
    
    Args:
        equipment_counts (pandas.DataFrame): Usage counts by equipment, semester, and week
        equipment_pct (pandas.DataFrame):    Percentage data by equipment, semester, and week
        equipment_stats (pandas.DataFrame):  Statistics by equipment and week
        rankings (pandas.DataFrame):         Equipment rankings by semester and week
        peak_weeks (pandas.DataFrame):       Peak usage weeks by equipment
        low_weeks (pandas.DataFrame):        Low usage weeks by equipment
        equipment_field (str):               Field used for equipment analysis
        output_dir (str):                    Directory to save output files
    """
    # Create descriptive suffix for filenames based on equipment field
    field_suffix = equipment_field.lower().replace(' ', '_')
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save detailed equipment counts
    counts_path = f"{output_dir}/{field_suffix}_counts.csv"
    equipment_counts.to_csv(counts_path, index=False)
    print(f"Saved {equipment_field} counts to {counts_path}")
    
    # Save percentage data
    pct_path = f"{output_dir}/{field_suffix}_percentages.csv"
    equipment_pct.to_csv(pct_path, index=False)
    print(f"Saved {equipment_field} percentages to {pct_path}")
    
    # Save equipment statistics
    stats_path = f"{output_dir}/{field_suffix}_stats.csv"
    equipment_stats.to_csv(stats_path, index=False)
    print(f"Saved {equipment_field} statistics to {stats_path}")
    
    # Save rankings
    rank_path = f"{output_dir}/{field_suffix}_rankings.csv"
    rankings.to_csv(rank_path, index=False)
    print(f"Saved {equipment_field} rankings to {rank_path}")
    
    # Save peak and low weeks
    peaks_path = f"{output_dir}/{field_suffix}_peak_weeks.csv"
    peak_weeks.to_csv(peaks_path, index=False)
    print(f"Saved {equipment_field} peak weeks to {peaks_path}")
    
    lows_path = f"{output_dir}/{field_suffix}_low_weeks.csv"
    low_weeks.to_csv(lows_path, index=False)
    print(f"Saved {equipment_field} low weeks to {lows_path}")


def analyze_equipment_popularity(file_path="data/enhanced_log.csv", output_dir="analysis"):
    """
    Main function to analyze equipment popularity over time for both individual
    equipment types (Access Type) and equipment categories (Equipment_Category).
    
    Args:
        file_path (str):  Path to the CSV file with enhanced data
        output_dir (str): Directory to save output files
        
    Returns:
        dict: Dictionary containing analysis results for both equipment types and categories
    """
    # Load data with equipment information
    df = load_equipment_data(file_path)
    
    results = {}
    
    # Analyze by individual equipment types (Access Type)
    print("\n=== Analyzing Individual Equipment Types (Access Type) ===")
    equipment_field = 'Access Type'
    
    equipment_counts, equipment_pct, equipment_stats, pct_changes = analyze_equipment_usage(df, equipment_field)
    rankings, top_equipment, top_pivot, consistency = calculate_rankings(equipment_pct, equipment_field)
    try:
        peak_weeks, low_weeks = identify_peak_usage(equipment_stats, equipment_field)
        if peak_weeks.empty or low_weeks.empty:
            print(f"Warning: Unable to identify peak or low usage weeks for {equipment_field}")
    except Exception as e:
        print(f"Error identifying peak usage for {equipment_field}: {e}")
        # Create empty DataFrames with the right columns as fallbacks
        peak_weeks = pd.DataFrame(columns=equipment_stats.columns)
        low_weeks = pd.DataFrame(columns=equipment_stats.columns)
    
    print_equipment_stats(equipment_stats, peak_weeks, low_weeks, top_pivot, consistency, equipment_field)
    save_equipment_stats(
        equipment_counts, equipment_pct, equipment_stats, 
        rankings, peak_weeks, low_weeks, equipment_field, output_dir
    )
    
    # Store results for individual equipment types
    results['access_type'] = {
        'counts': equipment_counts,
        'percentages': equipment_pct,
        'stats': equipment_stats,
        'changes': pct_changes,
        'rankings': rankings,
        'top_equipment': top_equipment,
        'top_pivot': top_pivot,
        'consistency': consistency,
        'peak_weeks': peak_weeks,
        'low_weeks': low_weeks
    }
    
    # Analyze by equipment categories (Equipment_Category)
    print("\n=== Analyzing Equipment Categories (Equipment_Category) ===")
    equipment_field = 'Equipment_Category'
    
    category_counts, category_pct, category_stats, category_changes = analyze_equipment_usage(df, equipment_field)
    category_rankings, top_category, category_pivot, category_consistency = calculate_rankings(category_pct, equipment_field)
    category_peaks, category_lows = identify_peak_usage(category_stats, equipment_field)
    
    print_equipment_stats(category_stats, category_peaks, category_lows, category_pivot, category_consistency, equipment_field)
    save_equipment_stats(
        category_counts, category_pct, category_stats, 
        category_rankings, category_peaks, category_lows, equipment_field, output_dir
    )
    
    # Store results for equipment categories
    results['equipment_category'] = {
        'counts': category_counts,
        'percentages': category_pct,
        'stats': category_stats,
        'changes': category_changes,
        'rankings': category_rankings,
        'top_equipment': top_category,
        'top_pivot': category_pivot,
        'consistency': category_consistency,
        'peak_weeks': category_peaks,
        'low_weeks': category_lows
    }
    
    print("\nEquipment analysis complete. Results saved to the analysis directory.")
    return results


if __name__ == "__main__":
    # Execute equipment analysis
    results = analyze_equipment_popularity()
    
    # Results for equipment types and categories are stored in the dictionary
    access_type_results = results['access_type']
    category_results = results['equipment_category']