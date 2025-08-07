"""
Equipment Popularity Visualization Utilities

This module provides functions for visualizing equipment popularity data,
focused on generating bar charts showing equipment usage across all categories
and ranking changes over time for all equipment types.

Functions:
    plot_equipment_popularity:  Creates bar charts showing relative equipment popularity
    plot_ranking_changes:       Visualizes how equipment rankings change over time
    visualize_equipment_trends: Main function to generate all equipment visualizations
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from analyze_equipment import analyze_equipment_popularity


def plot_equipment_popularity(results, output_dir="img"):
    """
    Creates bar charts showing the relative popularity of each equipment or equipment category.
    
    Args:
        results (dict):   Dictionary containing equipment analysis results
        output_dir (str): Directory to save the output images
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process both equipment types and categories
    for data_type, data in [('access_type', results['access_type']), 
                            ('equipment_category', results['equipment_category'])]:
        
        # Get field name based on data type
        field_name = 'Access Type' if data_type == 'access_type' else 'Equipment_Category'
        display_name = 'Equipment Type' if data_type == 'access_type' else 'Equipment Category'
        
        # Extract the relevant statistics
        equipment_stats = data['stats']
        
        # 1. Overall Popularity Bar Chart
        # Calculate average usage across all weeks for each equipment type
        avg_by_equipment = equipment_stats.groupby(field_name)['avg_usage'].mean().sort_values(ascending=False)
        
        plt.figure(figsize=(14, 10))
        bars = plt.bar(avg_by_equipment.index, avg_by_equipment.values, color='steelblue')
        plt.title(f'Overall {display_name} Popularity', fontsize=16)
        plt.xlabel(display_name, fontsize=12)
        plt.ylabel('Average Usage', fontsize=12)
        plt.xticks(rotation=90, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        plt.savefig(f"{output_dir}/{data_type}_overall_popularity.png", dpi=300)
        plt.close()
        
        # 2. Popularity by Semester Bar Chart
        # Get equipment percentages data
        equipment_pct = data['percentages']
        
        # Calculate average percentage by semester for all equipment
        semester_avg = equipment_pct.groupby([field_name, 'Semester'])['Percentage'].mean().reset_index()
        
        # If there are too many equipment types, create multiple charts
        all_equipment = semester_avg[field_name].unique()
        
        # Create a facet grid if there are many equipment types
        if len(all_equipment) > 10:
            # Create multiple plots with 10 equipment types each
            for i in range(0, len(all_equipment), 10):
                equipment_subset = all_equipment[i:i+10]
                subset_data = semester_avg[semester_avg[field_name].isin(equipment_subset)]
                
                plt.figure(figsize=(16, 12))
                sns.barplot(x='Semester', y='Percentage', hue=field_name, data=subset_data)
                plt.title(f'{display_name} Popularity by Semester (Group {i//10 + 1})', fontsize=16)
                plt.xlabel('Semester', fontsize=12)
                plt.ylabel('Percentage of Total Usage', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.legend(title=display_name, bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(axis='y', alpha=0.3)
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{data_type}_semester_popularity_group{i//10 + 1}.png", dpi=300)
                plt.close()
        else:
            # If there are fewer equipment types, create a single plot
            plt.figure(figsize=(16, 12))
            sns.barplot(x='Semester', y='Percentage', hue=field_name, data=semester_avg)
            plt.title(f'All {display_name} Popularity by Semester', fontsize=16)
            plt.xlabel('Semester', fontsize=12)
            plt.ylabel('Percentage of Total Usage', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.legend(title=display_name, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{data_type}_semester_popularity.png", dpi=300)
            plt.close()
        
        # 3. Week-by-Week Popularity for All Equipment
        # Calculate average percentage by week for all equipment
        weekly_avg = equipment_pct.groupby([field_name, 'Semester_Week'])['Percentage'].mean().reset_index()
        
        # If there are too many equipment types, create multiple charts
        if len(all_equipment) > 8:
            # Create multiple plots with 8 equipment types each for readability
            for i in range(0, len(all_equipment), 8):
                equipment_subset = all_equipment[i:i+8]
                subset_data = weekly_avg[weekly_avg[field_name].isin(equipment_subset)]
                
                plt.figure(figsize=(16, 10))
                sns.lineplot(x='Semester_Week', y='Percentage', hue=field_name, 
                            data=subset_data, marker='o', linewidth=2)
                plt.title(f'{display_name} Popularity by Week (Group {i//8 + 1})', fontsize=16)
                plt.xlabel('Week of Semester', fontsize=12)
                plt.ylabel('Percentage of Total Usage', fontsize=12)
                plt.grid(alpha=0.3)
                plt.xticks(range(1, weekly_avg['Semester_Week'].max()+1))
                plt.legend(title=display_name, bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{data_type}_weekly_popularity_group{i//8 + 1}.png", dpi=300)
                plt.close()
        else:
            # If there are fewer equipment types, create a single plot
            plt.figure(figsize=(16, 10))
            sns.lineplot(x='Semester_Week', y='Percentage', hue=field_name, 
                        data=weekly_avg, marker='o', linewidth=2)
            plt.title(f'All {display_name} Popularity by Week of Semester', fontsize=16)
            plt.xlabel('Week of Semester', fontsize=12)
            plt.ylabel('Percentage of Total Usage', fontsize=12)
            plt.grid(alpha=0.3)
            plt.xticks(range(1, weekly_avg['Semester_Week'].max()+1))
            plt.legend(title=display_name, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{data_type}_weekly_popularity.png", dpi=300)
            plt.close()
        
    print(f"Equipment popularity charts saved to {output_dir}/")


def plot_ranking_changes(results, output_dir="img"):
    """
    Visualizes how equipment rankings change over time for all equipment types/categories.
    
    Args:
        results (dict):   Dictionary containing equipment analysis results
        output_dir (str): Directory to save the output images
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process both equipment types and categories
    for data_type, data in [('access_type', results['access_type']), 
                            ('equipment_category', results['equipment_category'])]:
        
        # Get field name based on data type
        field_name = 'Access Type' if data_type == 'access_type' else 'Equipment_Category'
        display_name = 'Equipment Type' if data_type == 'access_type' else 'Equipment Category'
        
        # Extract the relevant data
        rankings = data['rankings']
        consistency = data['consistency']
        
        # 1. Ranking Consistency Visualization for All Equipment
        # Sort by consistency (mean rank)
        all_consistent = consistency.sort_values('mean')
        
        # If there are too many equipment types, create multiple charts
        if len(all_consistent) > 15:
            # Create multiple charts with 15 equipment types each
            for i in range(0, len(all_consistent), 15):
                subset = all_consistent.iloc[i:i+15]
                
                plt.figure(figsize=(16, 10))
                bars = plt.bar(subset[field_name], subset['mean'], color='teal',
                            yerr=subset['std'], capsize=5, alpha=0.7)
                
                # Add error bars showing min and max ranks
                for j, (_, row) in enumerate(subset.iterrows()):
                    plt.plot([j, j], [row['min'], row['max']], 'k-', alpha=0.5)
                    plt.plot([j-0.1, j+0.1], [row['min'], row['min']], 'k-', alpha=0.5)
                    plt.plot([j-0.1, j+0.1], [row['max'], row['max']], 'k-', alpha=0.5)
                
                plt.title(f'{display_name} Ranking Consistency (Group {i//15 + 1})', fontsize=16)
                plt.xlabel(display_name, fontsize=12)
                plt.ylabel('Average Rank (1 = Most Popular)', fontsize=12)
                plt.xticks(rotation=90, ha='right')
                plt.grid(axis='y', alpha=0.3)
                plt.gca().invert_yaxis()  # Invert y-axis so 1 (top rank) is at the top
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{data_type}_ranking_consistency_group{i//15 + 1}.png", dpi=300)
                plt.close()
        else:
            # If there are fewer equipment types, create a single chart
            plt.figure(figsize=(16, 10))
            bars = plt.bar(all_consistent[field_name], all_consistent['mean'], color='teal',
                        yerr=all_consistent['std'], capsize=5, alpha=0.7)
            
            # Add error bars showing min and max ranks
            for i, (_, row) in enumerate(all_consistent.iterrows()):
                plt.plot([i, i], [row['min'], row['max']], 'k-', alpha=0.5)
                plt.plot([i-0.1, i+0.1], [row['min'], row['min']], 'k-', alpha=0.5)
                plt.plot([i-0.1, i+0.1], [row['max'], row['max']], 'k-', alpha=0.5)
            
            plt.title(f'All {display_name} Ranking Consistency', fontsize=16)
            plt.xlabel(display_name, fontsize=12)
            plt.ylabel('Average Rank (1 = Most Popular)', fontsize=12)
            plt.xticks(rotation=90, ha='right')
            plt.grid(axis='y', alpha=0.3)
            plt.gca().invert_yaxis()  # Invert y-axis so 1 (top rank) is at the top
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{data_type}_ranking_consistency.png", dpi=300)
            plt.close()
        
        # 2. Ranking Changes Over Time (Heatmap) for All Equipment
        # Get all unique equipment types from the rankings
        all_equipment = rankings[field_name].unique()
        
        # Due to visualization constraints, we need to split this if there are many equipment types
        if len(all_equipment) > 20:
            # Create multiple heatmaps with 20 equipment types each for readability
            for i in range(0, len(all_equipment), 20):
                equipment_subset = all_equipment[i:i+20]
                subset_rankings = rankings[rankings[field_name].isin(equipment_subset)]
                
                # Create a pivot table with weeks as columns, equipment as rows, and average rank as values
                rank_pivot = pd.pivot_table(subset_rankings, 
                                          values='Rank', 
                                          index=field_name,
                                          columns='Semester_Week',
                                          aggfunc='mean')
                
                plt.figure(figsize=(16, 12))
                sns.heatmap(rank_pivot, cmap='YlGnBu_r', annot=True, fmt=".1f", 
                           cbar_kws={'label': 'Average Rank (1 = Most Popular)'})
                plt.title(f'{display_name} Ranking Changes by Week (Group {i//20 + 1})', fontsize=16)
                plt.xlabel('Week of Semester', fontsize=12)
                plt.ylabel(display_name, fontsize=12)
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{data_type}_rank_heatmap_group{i//20 + 1}.png", dpi=300)
                plt.close()
        else:
            # If there are fewer equipment types, create a single heatmap
            rank_pivot = pd.pivot_table(rankings, 
                                      values='Rank', 
                                      index=field_name,
                                      columns='Semester_Week',
                                      aggfunc='mean')
            
            plt.figure(figsize=(16, 14))
            sns.heatmap(rank_pivot, cmap='YlGnBu_r', annot=True, fmt=".1f", 
                       cbar_kws={'label': 'Average Rank (1 = Most Popular)'})
            plt.title(f'All {display_name} Ranking Changes by Week', fontsize=16)
            plt.xlabel('Week of Semester', fontsize=12)
            plt.ylabel(display_name, fontsize=12)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{data_type}_rank_heatmap.png", dpi=300)
            plt.close()
        
        # 3. Ranking Distribution (Box Plot) for All Equipment
        # Due to visualization constraints, we need to split this if there are many equipment types
        if len(all_equipment) > 20:
            # Create multiple box plots with 20 equipment types each for readability
            for i in range(0, len(all_equipment), 20):
                equipment_subset = all_equipment[i:i+20]
                subset_rankings = rankings[rankings[field_name].isin(equipment_subset)]
                
                plt.figure(figsize=(16, 12))
                sns.boxplot(x=field_name, y='Rank', hue=field_name, data=subset_rankings, palette='viridis', legend=False)
                plt.title(f'{display_name} Ranking Distribution (Group {i//20 + 1})', fontsize=16)
                plt.xlabel(display_name, fontsize=12)
                plt.ylabel('Rank (1 = Most Popular)', fontsize=12)
                plt.xticks(rotation=90, ha='right')
                plt.grid(axis='y', alpha=0.3)
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{data_type}_rank_distribution_group{i//20 + 1}.png", dpi=300)
                plt.close()
        else:
            # If there are fewer equipment types, create a single box plot
            plt.figure(figsize=(16, 10))
            sns.boxplot(x=field_name, y='Rank', hue=field_name, data=rankings, palette='viridis', legend=False)
            plt.title(f'All {display_name} Ranking Distribution', fontsize=16)
            plt.xlabel(display_name, fontsize=12)
            plt.ylabel('Rank (1 = Most Popular)', fontsize=12)
            plt.xticks(rotation=90, ha='right')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{data_type}_rank_distribution.png", dpi=300)
            plt.close()
        
        # 4. Ranking Changes Over Semesters (For All Equipment)
        # For each equipment type, show how ranking changed across semesters
        # Due to visualization constraints, we need to split this if there are many equipment types
        if len(all_equipment) > 15:
            # Create multiple charts with 10 equipment types each for readability
            for i in range(0, len(all_equipment), 10):
                equipment_subset = all_equipment[i:i+10]
                
                plt.figure(figsize=(16, 10))
                
                for equip in equipment_subset:
                    equip_ranks = rankings[rankings[field_name] == equip].sort_values(['Semester', 'Semester_Week'])
                    semester_ranks = equip_ranks.groupby('Semester')['Rank'].mean().reset_index()
                    plt.plot(semester_ranks['Semester'], semester_ranks['Rank'], marker='o', linewidth=2, label=equip)
                
                plt.title(f'{display_name} Ranking Changes Over Semesters (Group {i//10 + 1})', fontsize=16)
                plt.xlabel('Semester', fontsize=12)
                plt.ylabel('Average Rank (1 = Most Popular)', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.grid(alpha=0.3)
                plt.gca().invert_yaxis()  # Invert y-axis so 1 (top rank) is at the top
                plt.legend(title=display_name, bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{data_type}_semester_trend_group{i//10 + 1}.png", dpi=300)
                plt.close()
        else:
            # If there are fewer equipment types, create a single chart
            plt.figure(figsize=(16, 10))
            
            for equip in all_equipment:
                equip_ranks = rankings[rankings[field_name] == equip].sort_values(['Semester', 'Semester_Week'])
                semester_ranks = equip_ranks.groupby('Semester')['Rank'].mean().reset_index()
                plt.plot(semester_ranks['Semester'], semester_ranks['Rank'], marker='o', linewidth=2, label=equip)
            
            plt.title(f'All {display_name} Ranking Changes Over Semesters', fontsize=16)
            plt.xlabel('Semester', fontsize=12)
            plt.ylabel('Average Rank (1 = Most Popular)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.grid(alpha=0.3)
            plt.gca().invert_yaxis()  # Invert y-axis so 1 (top rank) is at the top
            plt.legend(title=display_name, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{data_type}_semester_trend.png", dpi=300)
            plt.close()
    
    print(f"Equipment ranking visualizations saved to {output_dir}/")


def filter_entry_data(results):
    """
    Filters out 'Jacobs MakerPass Access' from Access Type and 'Entry' from Equipment_Category.
    
    Args:
        results (dict): Dictionary containing equipment analysis results
        
    Returns:
        dict: Filtered results dictionary
    """
    filtered_results = {'access_type': {}, 'equipment_category': {}}
    
    # Filter Access Type data
    for key, data in results['access_type'].items():
        if isinstance(data, pd.DataFrame) and 'Access Type' in data.columns:
            # Filter out 'Jacobs MakerPass Access'
            filtered_results['access_type'][key] = data[data['Access Type'] != 'Jacobs MakerPass Access'].copy()
        else:
            # For non-DataFrame data or DataFrames without 'Access Type' column, copy as is
            filtered_results['access_type'][key] = data
    
    # Filter Equipment_Category data
    for key, data in results['equipment_category'].items():
        if isinstance(data, pd.DataFrame) and 'Equipment_Category' in data.columns:
            # Filter out 'Entry' category
            filtered_results['equipment_category'][key] = data[data['Equipment_Category'] != 'Entry'].copy()
        else:
            # For non-DataFrame data or DataFrames without 'Equipment_Category' column, copy as is
            filtered_results['equipment_category'][key] = data
    
    print(f"Filtered 'Jacobs MakerPass Access' from Access Type data")
    print(f"Filtered 'Entry' from Equipment_Category data")
    
    return filtered_results


def visualize_equipment_trends(results, file_path, output_dir):
    """
    Main function to generate all visualizations for equipment popularity trends.
    
    Args:
        results (dict, optional): Dictionary with equipment analysis results (if already computed)
        file_path (str):          Path to the CSV file with enhanced data
        output_dir (str):         Directory to save the output images
    """
    # If results not provided, run the analysis
    if results is None:
        results = analyze_equipment_popularity(file_path, output_dir="analysis")
    
    # Filter out entry-related data if requested
    results = filter_entry_data(results)
    
    # Generate popularity visualizations
    plot_equipment_popularity(results, output_dir)
    
    # Generate ranking change visualizations
    plot_ranking_changes(results, output_dir)
    
    print(f"All equipment visualizations have been saved to the {output_dir}/ directory")


if __name__ == "__main__":
    # Execute visualization functions
    visualize_equipment_trends(results=None, file_path="data/enhanced_log.csv", output_dir="img")