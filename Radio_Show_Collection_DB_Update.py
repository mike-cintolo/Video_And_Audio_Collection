#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 16:33:49 2023

@author: michaelcintolo

Description: "Show_title (Production_Year) S00E00 - Episode_Title.File_Ext"

            "S" is for Season Number
            "E" is for Episode Number
            
            Not all files have a Season Number and/or Episode Number. 
            Some will have neither. 
            Cycle through the files in the directory, only process files with valid extensions.
            Parse out the name based on gthe above naming convention. 
            Check to see if the file has been updated in the database, if it has do nothing.
            If the file has not been updated in the database then add it. 
            There is also an error log and a successful completion CSV file.


# Directory where Radio Shows files are located
# base_directory = '/home/michaelcintolo/Music/Mp3sToUpdate/' # Test
base_directory = '/run/media/michaelcintolo/Primary/4. Radio Shows/' # Production
"""

import os
import json
import mysql.connector
import pandas as pd

# Read database credentials from a JSON config file
with open("/home/michaelcintolo/Programming/ConfigFiles/db_config.json", "r") as config_file:
    config = json.load(config_file)

db_host = config["DB_HOST"]
db_user = config["DB_USER"]
db_password = config["DB_PASSWORD"]
db_database = config["DB_DATABASE"]

# Connect to your MySQL database
db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_database
)

cursor = db.cursor()

# Directory where Radio Shows files are located
# base_directory = '/home/michaelcintolo/Music/Mp3sToUpdate/' # Test
base_directory = '/run/media/michaelcintolo/Primary/4. Radio Shows/' # Production

# Process only files with valid extensions
valid_extensions = ['mp3', 'mp4', 'flac', 'wav', 'wma', 'aac', 'ogg']

# Initialize a file count variable
file_count = 0

def parse_file_name(filename):
    # Initialize default values for fields
    show_title, production_year, season_number, episode_number, episode_title, file_ext = "Unknown", "1900", "0", "0", "Unknown", "Unknown"

    # Not every file has a season_number or episode_number
    # This logic will determine if they do and reset fields to what is in filename
    # THese fields will always be after the first right paren and before the episode title indicator
    first_right_paren = filename.find(") ")
    
    if first_right_paren != -1:
        episode_title_sep = filename.find(" - ", first_right_paren)
        
        if episode_title_sep != -1:
            episode_ind = filename.find("E",first_right_paren)
            if episode_ind != -1 and episode_ind < episode_title_sep:
                episode_number = filename[episode_ind + 1:episode_title_sep].strip()
                season_ind = filename.find("S",first_right_paren)
                if season_ind != -1:
                    if season_ind < episode_title_sep:
                        season_number = filename[season_ind + 1:episode_ind]

    # ***** parse out show_title *****
    # Find the position of " ("
    start_position = 0
    end_position = filename.find(" (")

    # Extract the portion of the filename
    if end_position != -1:
        show_title = filename[start_position:end_position].strip()

    # ***** parse out production_year *****
    # Find the positions of " (" and ")"
    start_position = filename.find(" (") + 2
    end_position = filename.find(")")

    # Extract the production_year
    if start_position != -1 and end_position != -1:
        production_year = filename[start_position:end_position]

    # ***** parse out episode_title *****
    # Find the positions of " - " and "."
    start_position = filename.find(" - ")
    if start_position != -1:
        end_position = filename.rfind(".")

        # Extract the episode_title
        if start_position != -1 and end_position != -1:
            episode_title = filename[start_position + 3:end_position].strip()

    # ***** parse out the file_ext *****
    # Find the last period in the filename (should be the extension)
    # Use os.path.splitext to extract the file extension correctly
    _, file_ext_with_dot = os.path.splitext(filename)
    file_ext = file_ext_with_dot[1:].lower()

    return show_title, production_year, season_number, episode_number, episode_title, file_ext

# Define a function to parse file names and insert data into the database
def insert_file_data(file_path):
    global file_count  # Declare file_count as global

    try:
        # Extract the file name from the file path
        file_name = os.path.basename(file_path)

        # Increment the file count
        file_count += 1

        # Print the filename and file count to the console
        print(f"Processing file {file_count}: {file_name}")

        # Check if the file name exists in the database for RadioShowCollection table
        query_collection = "SELECT COUNT(*) FROM Entertainment.RadioShowCollection WHERE File_Name = %s"
        cursor.execute(query_collection, (file_name,))
        result_collection = cursor.fetchone()
        if result_collection[0] > 0:
            print(f"File name already exists in the RadioShowCollection database: {file_name}")
            return  # Skip the insert if the file name exists in RadioShowCollection

        # Parse the file name
        show_title, production_year, season_number, episode_number, episode_title, file_ext = parse_file_name(file_name)

        # Example SQL query to insert data into the RadioShowCollection table
        insert_query_collection = "INSERT INTO Entertainment.RadioShowCollection (Show_Title, Production_Year, Season_Number, Episode_Number, Episode_Title, File_Ext, File_Name) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values_collection = (show_title, production_year, season_number, episode_number, episode_title, file_ext, file_name)

        cursor.execute(insert_query_collection, values_collection)
        db.commit()

        # Log the successfully inserted file
        log_successful_insert(show_title, production_year, season_number, episode_number, episode_title, file_ext, file_name)

    except Exception as e:
        # Log the error to a file
        log_error(file_path, str(e))

# Define a function to log successful inserts in a CSV file
def log_successful_insert(show_title, production_year, season_number, episode_number, episode_title, file_ext, file_name):
    success_data = {
        "Show_Title": [show_title],
        "Production_Year": [production_year],
        "Season_Number": [season_number],
        "Episode_Number": [episode_number],
        "Episode_Title": [episode_title],
        "File_Name": [file_name]
    }

    success_df = pd.DataFrame(success_data)
    success_file = '/home/michaelcintolo/Programming/OutputFiles/Radio_Show_Successful_Inserts.csv'

    # If the file doesn't exist, create it with headers
    if not os.path.exists(success_file):
        success_df.to_csv(success_file, index=False, header=True)
    else:
        success_df.to_csv(success_file, mode='a', index=False, header=False)

# Define a function to log errors to a log file
def log_error(file_path, error_message):
    error_log_file = '/home/michaelcintolo/Programming/OutputFiles/Radio_Show_Error_Log.txt'

    with open(error_log_file, 'a') as log_file:
        log_file.write(f"Error processing file: {file_path}\n")
        log_file.write(f"Error message: {error_message}\n\n")

for root, dirs, files in os.walk(base_directory):
    for file in files:
        if any(file.endswith(file_ext) for file_ext in valid_extensions):
            file_path = os.path.join(root, file)

            insert_file_data(file_path)

# Close the database connection when you're done
cursor.close()
db.close()
