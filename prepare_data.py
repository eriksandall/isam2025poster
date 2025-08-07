"""
Data preparation utilities.

This module provides functions for cleaning, anonymizing, and preparing 
makerspace usage data for analysis. It also includes functionality to
enhance datasets with semester-related information.

Functions:
    anonymize:              Anonymizes personal data by replacing names with hash IDs.
    clean_and_load:         Filters and cleans raw makerspace access data.
    add_semester_info:      Adds semester name and week number to each row.
    enhance_dataset:        Enhances the dataset with semester and equipment information.
    add_equipment_category: Categorizes equipment types into broader categories.
"""


import hashlib
import os
import pandas as pd
from api_integration import fetch_terms
from datetime import datetime
from dotenv import load_dotenv


def anonymize(input_file_path, output_file_path):
    """
    Anonymizes personal data by replacing names with unique hash IDs
    and removing personal information.
    
    Args:
        input_file_path (str):  Path to the input CSV containing personal data
        output_file_path (str): Path where the anonymized CSV will be saved
    """
    # Load the data
    df = pd.read_csv(input_file_path)
    
    # Function to generate a unique ID from First Name and Last Name
    def generate_unique_id(first_name, last_name):
        # Combine the first and last names
        name_string = f"{first_name} {last_name}"
        
        # Hash the combined string to generate a unique ID
        unique_id = hashlib.sha256(name_string.encode()).hexdigest()
        
        return unique_id
    
    # Apply the function to the First Name and Last Name columns
    df['Unique ID'] = df.apply(lambda row: generate_unique_id(row['First Name'], row['Last Name']), axis=1)
    
    # Remove personally identifiable information
    df = df.drop(columns=['First Name', 'Last Name'])
    
    # Save the updated DataFrame to a new CSV
    df.to_csv(output_file_path, index=False)
    
    print(f"Anonymized data saved to '{output_file_path}'")


def clean_and_load(file_path, covid_start, covid_end):
    """
    Converts makerspace access data timestamps to datetime, removes duplicates,
    removes COVID-era data, and returns a DataFrame.
    
    Args:
        file_path (str):        Path to the CSV file containing raw data
        covid_start (datetime): Start date of COVID campus closure period
        covid_end (datetime):   End date of COVID campus closure period
        
    Returns:
        pandas.DataFrame: Cleaned and filtered dataset
    """
    # Load the data from the CSV file and parse the Timestamp column as datetime
    df = pd.read_csv(file_path, parse_dates=["Timestamp"], dayfirst=False)

    # Remove duplicates
    df = df.drop_duplicates()

    # Filter out COVID closure period
    df = df[~((df["Timestamp"] >= covid_start) & (df["Timestamp"] <= covid_end))]

    return df


def add_semester_info(df, terms_data, output_file_path=None):
    """
    Adds 'Semester' and 'Semester_Week' columns to the DataFrame with weeks 
    running Monday-Sunday regardless of semester start day.
    
    Args:
        df (pandas.DataFrame):            DataFrame with 'Timestamp' column
        terms_data (list):                List of tuples with (semester_name, start_date, end_date)
        output_file_path (str, optional): Path to save the enhanced DataFrame
        
    Returns:
        pandas.DataFrame: Enhanced DataFrame with semester information
    """
    # Make a copy of the dataframe to avoid modifying the original
    enhanced_df = df.copy()
    
    # Initialize new columns with default values
    enhanced_df['Semester'] = 'Unknown'
    enhanced_df['Semester_Week'] = None
    
    # Sort terms chronologically to handle any potential overlaps
    sorted_terms = sorted(terms_data, key=lambda x: x[1])
    
    for semester_name, start_date, end_date in sorted_terms:
        # Create a mask for records that fall within this semester's date range
        mask = (enhanced_df['Timestamp'] >= start_date) & (enhanced_df['Timestamp'] <= end_date)
        
        # Assign semester name to matching records
        enhanced_df.loc[mask, 'Semester'] = semester_name
        
        # Find the Monday of the first week (may be before semester actually starts)
        days_to_monday = start_date.weekday()  # 0 for Monday, 1 for Tuesday, etc.
        first_monday = start_date - pd.Timedelta(days=days_to_monday)
        
        # Calculate the week number for each record
        days_since_first_monday = (enhanced_df.loc[mask, 'Timestamp'] - first_monday).dt.days
        enhanced_df.loc[mask, 'Semester_Week'] = (days_since_first_monday // 7) + 1
    
    # Remove summer sessions (rows with 'Unknown' semester)
    rows_before = len(enhanced_df)
    enhanced_df = enhanced_df[enhanced_df['Semester'] != 'Unknown']
    rows_removed = rows_before - len(enhanced_df)
    print(f"Removed {rows_removed} rows with 'Unknown' semester data (Summer sessions & COVID semesters)")
    
    # Save enhanced data if output path is provided
    if output_file_path:
        enhanced_df.to_csv(output_file_path, index=False)
        print(f"Enhanced data saved to '{output_file_path}'")
    
    return enhanced_df


def enhance_dataset(df, terms_data, output_file_path=None):
    """
    Enhances the dataset by adding semester information and equipment categories.
    
    Args:
        df (pandas.DataFrame):              DataFrame with 'Timestamp' and 'Access Type' columns
        terms_data (list):                  List of tuples with (semester_name, start_date, end_date)
        output_file_path (str, optional):   Path to save the enhanced DataFrame
        
    Returns:
        pandas.DataFrame: Enhanced DataFrame with semester and equipment information
    """
    # Make a copy of the dataframe to avoid modifying the original
    enhanced_df = df.copy()
    
    # Normalize equipment names before adding semester info
    equipment_normalization = {
        'Jacobs DiWire Room 220C': 'Jacobs DiWire',
        'Jacobs Vinyl Cutter and Inkjet': 'Jacobs Vinyl Cutter'
    }
    
    # Replace the equipment names directly in the dataframe
    enhanced_df['Access Type'] = enhanced_df['Access Type'].replace(equipment_normalization)
    print(f"Normalized equipment names: merged 'Jacobs DiWire Room 220C' and 'Jacobs Vinyl Cutter and Inkjet'")
    
    # Initialize new columns with default values
    enhanced_df['Semester'] = 'Unknown'
    enhanced_df['Semester_Week'] = None
    
    # Sort terms chronologically to handle any potential overlaps
    sorted_terms = sorted(terms_data, key=lambda x: x[1])
    
    for semester_name, start_date, end_date in sorted_terms:
        # Create a mask for records that fall within this semester's date range
        mask = (enhanced_df['Timestamp'] >= start_date) & (enhanced_df['Timestamp'] <= end_date)
        
        # Assign semester name to matching records
        enhanced_df.loc[mask, 'Semester'] = semester_name
        
        # Find the Monday of the first week (may be before semester actually starts)
        days_to_monday = start_date.weekday()  # 0 for Monday, 1 for Tuesday, etc.
        first_monday = start_date - pd.Timedelta(days=days_to_monday)
        
        # Calculate the week number for each record
        days_since_first_monday = (enhanced_df.loc[mask, 'Timestamp'] - first_monday).dt.days
        enhanced_df.loc[mask, 'Semester_Week'] = (days_since_first_monday // 7) + 1
    
    # Remove summer sessions (rows with 'Unknown' semester)
    rows_before = len(enhanced_df)
    enhanced_df = enhanced_df[enhanced_df['Semester'] != 'Unknown']
    rows_removed = rows_before - len(enhanced_df)
    print(f"Removed {rows_removed} rows with 'Unknown' semester data (Summer sessions & COVID semesters)")
    
    # Add equipment categories
    enhanced_df = add_equipment_category(enhanced_df)
    
    # Save enhanced data if output path is provided
    if output_file_path:
        enhanced_df.to_csv(output_file_path, index=False)
        print(f"Enhanced data saved to '{output_file_path}'")
    
    return enhanced_df


def add_equipment_category(df):
    """
    Adds an 'Equipment_Category' column based on the 'Access Type' field.
    
    Args:
        df (pandas.DataFrame): DataFrame with 'Access Type' column
        
    Returns:
        pandas.DataFrame: DataFrame with added 'Equipment_Category' column
    """
    # Make a copy of the dataframe to avoid modifying the original
    enhanced_df = df.copy()
    
    # Define equipment category mapping
    equipment_categories = {
        # Advanced 3D Printing
        'Jacobs Connex' : 'Advanced 3D Printing',
        'Jacobs Dimension' : 'Advanced 3D Printing',
        'Jacobs Form 3' : 'Advanced 3D Printing',
        'Jacobs Fortus' : 'Advanced 3D Printing',
        
        # Advanced Prototyping
        'Jacobs FabLight Laser' : 'Advanced Prototyping',
        'Jacobs OMAX Waterjet' : 'Advanced Prototyping',
        'Jacobs Shopbot' : 'Advanced Prototyping',
        
        # Basic 3D Printing
        'Jacobs Type A' : 'Basic 3D Printing',
        
        # Basic Prototyping
        'Jacobs DiWire' : 'Basic Prototyping',
        'Jacobs Inkjet' : 'Basic Prototyping',
        'Jacobs Vinyl Cutter' : 'Basic Prototyping',
        
        # Laser Cutting
        'Jacobs Laser Access' : 'Laser Cutting',
        
        # Metal Shop
        'Jacobs Metal Shop' : 'Metal Shop',
        
        # Wood Shop
        'Jacobs Wood Shop' : 'Wood Shop',
        
        # Entry
        'Jacobs MakerPass Access' : 'Entry',
    }
    
    # Create a function to map specific equipment to categories
    def map_equipment_category(access_type):
        # First try direct mapping
        if access_type in equipment_categories:
            return equipment_categories[access_type]
        
        # If no direct match, try to find partial matches
        for equip, category in equipment_categories.items():
            if equip.lower() in access_type.lower():
                return category
        
        # Default category for unmapped equipment
        return 'Other'
    
    # Apply the mapping function to create the Equipment_Category column
    enhanced_df['Equipment_Category'] = enhanced_df['Access Type'].apply(map_equipment_category)
    
    # Print statistics about the categorization
    print("\nEquipment Categorization Summary:")
    print(f"Total equipment types: {enhanced_df['Access Type'].nunique()}")
    print(f"Total categories: {enhanced_df['Equipment_Category'].nunique()}")
    print("\nCategory counts:")
    print(enhanced_df['Equipment_Category'].value_counts())
    
    return enhanced_df


if __name__ == '__main__':
    # Anonymize data
    input_file_path = 'data/log.csv'
    output_file_path = 'data/anonymized_log.csv'
    anonymize(input_file_path, output_file_path)
    
    # Remove data from COVID pandemic, and load into a DataFrame
    file_path = output_file_path
    covid_start = datetime.strptime('2020-03-14', '%Y-%m-%d')
    covid_end = datetime.strptime('2021-08-25', '%Y-%m-%d')
    df = clean_and_load(file_path, covid_start, covid_end)

    # Fetch semester data from campus via the Terms API
    term_ids = [2162, 2168, 2172, 2178, 2182, 2188, 2192, 2198, 2218, 2222, 2228,
                2232, 2238, 2242]  # Spring 2016 to Spring 2024, excluding Summers and COVID semesters
    load_dotenv()  # Load variables from .env file
    app_id = os.getenv('APP_ID')
    app_key = os.getenv('API_KEY')
    terms = fetch_terms(term_ids, app_id, app_key)
    
    # Enhance the DataFrame with semester information and equipment categories
    enhanced_df = enhance_dataset(df, terms, output_file_path='data/enhanced_log.csv')