"""
API Integration Utilities

This module provides functions for interacting with the Cal's Term API
to fetch semester information for use in makerspace usage analysis.

Functions:
    fetch_terms: Retrieves semester information from the Term API.
"""

import requests
from datetime import datetime


def fetch_terms(term_ids, app_id, app_key):
    """
    Fetches semester information from the Term API for the given term IDs.

    Args:
        term_ids (list): List of term IDs to fetch data for.
        app_id (str):    Application ID for API authentication.
        app_key (str):   Application key for API authentication.

    Returns:
        list: A list of tuples containing (semester_name, start_date, end_date).
    """
    # Base URL for the Term API
    base_url = "https://gateway.api.berkeley.edu/uat/sis/v2/terms"

    # List to store the results
    terms_data = []

    # Headers for authentication
    headers = {
        "app_id": app_id,
        "app_key": app_key
    }

    # Iterate over each term ID
    for term_id in term_ids:
        try:
            # Construct the full API URL for the term ID, limited to undergraduate career
            url = f"{base_url}/{term_id}?career-code=ugrd"

            # Send a GET request to the API
            response = requests.get(url, headers=headers)

            # Check if the request was successful
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Extract the undergrad term data from the response
            ugrd_term = data.get("response", {}).get("terms", [])

            if not ugrd_term:
                raise KeyError(f"No UGRD term data found for term ID: {term_id}")

            # Get the semester name
            term = ugrd_term[0]
            semester_name = term.get("name")

            if not semester_name:
                raise KeyError(f"Semester name not found for term ID: {term_id}")

            # Extract the dates from the new locations in the JSON
            # Get start date from sessions > beginDate
            sessions = term.get("sessions", [])
            if not sessions:
                raise KeyError(f"No sessions found for term ID: {term_id}")

            start_date = sessions[0].get("beginDate")
            if not start_date:
                raise KeyError(f"Start date not found for term ID: {term_id}")

            # Get end date from fullyGradedDeadline at the `terms` level
            end_date = term.get("fullyGradedDeadline")
            if not end_date:
                raise KeyError(f"End date not found for term ID: {term_id}")

            # Convert the dates to datetime objects
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            # Append the tuple to the results list
            terms_data.append((semester_name, start_date, end_date))

        except requests.exceptions.RequestException as e:
            # Handle API request errors
            print(f"API request failed for term ID {term_id}: {e}")
        except KeyError as e:
            # Handle missing keys in the JSON response
            print(f"Key error for term ID {term_id}: {e}")
        except ValueError as e:
            # Handle date parsing errors
            print(f"Date parsing error for term ID {term_id}: {e}")

    return terms_data
