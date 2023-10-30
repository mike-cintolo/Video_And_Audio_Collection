#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 01:12:36 2023

@author: michaelcintolo

Description: "Show_title (Production_Year) S00E00 - Episode_Title.File_Ext"

            "S" is for Season Number
            "E" is for Episode Number
            
            Not all files have a Season Number and/or Episode Number. 
            Some will have neither. 
            Cycle through the files in the directory, only process files with valid extensions.
            Parse out the name based on the above naming convention. 
            Check to see if the file has been updated in the database, if it has do nothing.
            If the file has not been updated in the database then add it. 
            There is also an error log and a successful completion CSV file.
            
Collections: CartoonCollection, MovieCollection, TVShowCollection, RadioShowCollection, MusicCollection, AudioBookCollection

"""

import os
import json
import csv

# **************************
# ***** Initialization *****
# **************************

# ***** Environment Variables *****

# Set the program_name and production variables
program_name = "RadioShowCollection"  # Change this based on collection
# production = True  # Set this to True for production
production = False  # Set this to False for test

# Get the path to the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the input and output paths based on the script's location
input_dir = os.path.join(os.path.dirname(script_dir), 'Input')
output_dir = os.path.join(os.path.dirname(script_dir), 'Output')

# Construct the path to the JSON configuration file in the parent directory
config_dir = os.path.join(os.path.dirname(script_dir), 'Config')

# Define the filename for the configuration file
os_config_filename = 'os_config.json'

# Construct the full path to the JSON configuration file
os_config_file_path = os.path.join(config_dir, os_config_filename)

# Load the JSON configuration from the specified path
with open(os_config_file_path, "r") as config_file:
    config = json.load(config_file)

# Determine the environment based on the 'production' variable
environment = "production" if production else "test"

# Access the collection path based on the environment and program_name
collection_dir = config["Collections"][program_name][f"{environment}_dir"]

# Define the file path
csv_file_name = 'Inner_Sanctum_Episode_List.csv'
csv_file_path = os.path.join(input_dir, csv_file_name)

episode_data = {}

with open(csv_file_path, 'r') as csvfile:
    # Read in the CSV file 
    reader = csv.reader(csvfile)
    
    # Skip the header row if present
    next(reader) 
    
    # Iterate through rows in the CSV file
    for row in reader:
        # Load the columns into variables
        season_number = row[0].strip()  # Column A (Season Number)
        episode_title = row[2].strip()   # Column C (Episode Title)
        episode_number = row[1].strip()  # Column B (Episode Number)

        # Format season and episode numbers with leading zeros
        season_number = season_number.zfill(2) # Ensure season_number is stored as a two-character string
        episode_number = episode_number.zfill(2)  # Ensure episode_number is stored as a two-character string

        # Use a tuple of (season_number, episode_title) as the key
        episode_key = (season_number, episode_title)
        
        # Store episode numbers as two-character strings
        episode_data[episode_key] = episode_number
        
# Initialize variables to store data
data_record = {
    "show_title": "",
    "production_year": "",
    "season_number": "",
    "episode_number": "",
    "episode_title": "",
    "file_ext": "",
    "file_name": ""
}

# Define function to parse out file name elements
def parse_file_name(file_name, data_record):
    
    # Initialize default values for fields
    data_record["show_title"], data_record["production_year"], data_record["season_number"], data_record["episode_number"], data_record["episode_title"], data_record["file_ext"] = "Unknown", "1900", "0", "0", "Unknown", "Unknown"

    # Initilaize data record file name with file name passed in
    data_record["file_name"] = file_name
    
    # Not every file has a season_number or episode_number
    # This logic will determine if they do and reset fields to what is in file_name
    # THese fields will always be after the first right paren and before the episode title indicator
    first_right_paren = file_name.find(") ")
    
    # ***** parse out season_number and episode_number *****
    # The season num season_number and episode_number will be after the first right paren and the following hyphen
    if first_right_paren != -1:
        episode_title_sep = file_name.find(" - ", first_right_paren)
        
        # first right paren and the following hyphen found
        if episode_title_sep != -1:
            
            # Find where "E" is after the right paren
            episode_ind = file_name.find("E",first_right_paren)
            
            # If the episode indeicator position less than the hyphen position
            if episode_ind != -1 and episode_ind < episode_title_sep:
                # Load episode_number with what comes after the "E" and the hyphen
                data_record["episode_number"] = file_name[episode_ind + 1:episode_title_sep].strip()
                
                # Now see if there is a "S" after first right paren, indicating that there is a season number
                season_ind = file_name.find("S",first_right_paren)
                
                # Season number found
                if season_ind != -1:
                    
                    # Make sure the season number is before the episode number
                    if season_ind < episode_title_sep:
                        
                        # Load season_number what is after the "S" and before the "E"
                        data_record["season_number"] = file_name[season_ind + 1:episode_ind]

    # ***** parse out show_title *****
    # Find the position of " ("
    start_position = 0
    end_position = file_name.find(" (")

    # Find the first left paren
    if end_position != -1:
        # Extract the portion of the file_name between the start and the first left paren for the show_title
        data_record["show_title"] = file_name[start_position:end_position].strip()

    # ***** parse out production_year *****
    # Find the positions of " (" and ")"
    start_position = file_name.find(" (") + 2
    end_position = file_name.find(")")

    # Extract the production_year
    if start_position != -1 and end_position != -1:
        # LOad the production_year with what is between the first left and right paren
        data_record["production_year"] = file_name[start_position:end_position]

    # ***** parse out episode_title *****
    # Find the positions of " - " and "."
    start_position = file_name.find(" - ")
    
    # If start position found
    if start_position != -1:
        # Find the first period starting from the right of the file_name
        end_position = file_name.rfind(".")

        # If start and end position found
        if start_position != -1 and end_position != -1:
            # Load the episode_title from what is between  " - " and "."
            data_record["episode_title"] = file_name[start_position + 3:end_position].strip()

    # ***** parse out the file_ext *****
    # Find the last period in the file_name (should be the extension)
    # Use os.path.splitext to extract the file extension correctly
    _, file_ext_with_dot = os.path.splitext(file_name)
    data_record["file_ext"] = file_ext_with_dot[1:].lower()

# Function to rename files
def rename_files(collection_dir, data_record, episode_data):
    
    # Iterate through files in directory
    for file_name in os.listdir(collection_dir):
        
        # Parse out the file name into the data_record
        parse_file_name(file_name, data_record)
        
        # Create a tuple with (season_number, episode_title)
        episode_key = (data_record["season_number"], data_record["episode_title"])
        
        # Check if the tuple exists in the episode_data dictionary
        if episode_key in episode_data:
            data_record["episode_number"] = episode_data[episode_key]

             # Convert season_number and episode_number to integers
            season_number = int(data_record["season_number"])
            episode_number = int(data_record["episode_number"])
            
            # Create the new file name with formatted season and episode numbers
            new_filename = f'{data_record["show_title"]} ({data_record["production_year"]}) S{season_number:02d}E{episode_number:02d} - {data_record["episode_title"]}.{data_record["file_ext"]}'

            # Rename the file
            old_file_path = os.path.join(collection_dir, file_name)
            new_file_path = os.path.join(collection_dir, new_filename)
            os.rename(old_file_path, new_file_path)

# Now, call the function to rename files
rename_files(collection_dir, data_record, episode_data)