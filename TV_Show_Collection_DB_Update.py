#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 09:26:02 2023

@author: michaelcintolo

Description: This program will cycle through all the TV Show Collection on a local hard drive,
            parse out the fields in the file name and add a row to a database table for each file.
            The naming convention for the main folder for each TV Show is "TV_Show_Title".
            The naming convention for each file name is:
                "TV_Show_Title (Production_Year) S00E00 - Episode_Title.Ext".
                "S00E00" - S stands for Season, E stands for Episode, followed by the number.
                Not all files will have a Season.
            The database is Entertainment.TVShowCollection and the structure is:
                Show_Title VARCHAR(80),
                Production_Year INT,
                Season_Number INT,
                Episode_Number INT,
                Episode_Title VARCHAR(120),
                File_Ext VARCHAR(5),
                File_Name VARCHAR(255)

# Directory where TV Show files are located
# tv_show_directory = '/home/michaelcintolo/Videos/VideosToUpdate/' # Test
tv_show_directory = '/run/media/michaelcintolo/Primary/3. TV Shows/' # Production
"""

import json
import os
import mysql.connector
import logging

# Set up logging
logging.basicConfig(filename='tv_show_parser.log', level=logging.INFO)

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

# Directory where TV Show files are located
# tv_show_directory = '/home/michaelcintolo/Videos/VideosToUpdate/' # Test
tv_show_directory = '/run/media/michaelcintolo/Primary/3. TV Shows/' # Productionon

# List of valid video file extensions
valid_extensions = ['mp4', 'avi', 'mkv', 'ogv', 'webm']

# Declare a global variable for file_count
global file_count  

# Initialize a file count variable
file_count = 0

# Define a function to parse file names
def parse_filename(filename):
    # Initialize default values for fields
    show_title, production_year, season_number, episode_number, episode_title, file_ext = "Unknown", "1900", "0", "0", "Unknown", "Unknown"
    
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
       
    # ***** parse out season_number *****    
    # Find the positions of "S" and "E"
    start_position = filename.find(")") + 2
    
    # Extract the season_number
    if start_position != -1:
        end_position = filename.find("E", start_position) 
        if end_position != -1 and end_position > start_position:
            season_number = filename[start_position:end_position].strip()
            season_number = season_number.lstrip('S')
        
    # ***** parse out episode_number *****    
    # Find the position of ")"
    end_position = filename.find(")")
        
    # Extract the actors
    if end_position != -1:
        start_position = filename.find("E", end_position) + 1
        end_position = filename.find(" ", start_position)
        
        if start_position != -1:
            episode_number = filename[start_position:end_position].strip()
    
    # ***** parse out episode_title *****   
    # Find the positions of " - " and "."
    start_position = filename.find(" - ") + 3
    end_position = filename.rfind('.') 

    # Extract the genre
    if start_position != -1 and end_position != - 1:
        episode_title = filename[start_position:end_position].strip() 

    # ***** parse out the file_ext *****
    # Find the last period in the filename (should be the extension)
    # Use os.path.splitext to extract the file extension correctly
    _, file_ext_with_dot = os.path.splitext(filename)
    file_ext = file_ext_with_dot[1:].lower()

    return show_title, production_year, season_number, episode_number, episode_title, file_ext

try:
    # Iterate through TV show folders on the hard drive
    for tv_show_folder in os.listdir(tv_show_directory):
        tv_show_path = os.path.join(tv_show_directory, tv_show_folder)
        if os.path.isdir(tv_show_path):
            # Iterate through files in each TV show folder
            for filename in os.listdir(tv_show_path):
                file_path = os.path.join(tv_show_path, filename)
                if os.path.isfile(file_path):
                    # Use os.path.splitext to extract the file extension correctly
                    _, file_ext_with_dot = os.path.splitext(filename)
                    file_ext = file_ext_with_dot[1:].lower()
                    
                    # Check if the file has a valid video extension
                    if file_ext in valid_extensions:
                        # Increment the file count
                        file_count += 1
             
                        # Print the filename and file count to the console
                        print(f"Processing file {file_count}: {filename}")
                    
                        # Parse the file name
                        parsed_info = parse_filename(filename)
                        
                        if parsed_info:
                            show_title, production_year, season_number, episode_number, episode_title, file_ext = parsed_info
    
                            # Check if the TV show and episode exist in the database
                            cursor.execute("SELECT COUNT(*) FROM TVShowCollection WHERE File_Name = %s", (filename,))
                            result = cursor.fetchone()
                            
                            # You need to consume the result using fetchone() or fetchall()
                            # This can be done by simply reading the result variable
                            _ = result  # Consuming the result, no need to use it
                            
                            count = result[0]  # Get the count from the result
                            
                            if count == 0:
                                # TV show and episode do not exist, insert data into the database
                                cursor.execute("INSERT INTO TVShowCollection (Show_Title, Production_Year, Season_Number, Episode_Number, Episode_Title, File_Ext, File_Name) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                               (show_title, production_year, season_number, episode_number, episode_title, file_ext, filename))
                                db.commit()  # Commit changes to the database

except mysql.connector.Error as e:
    # Handle MySQL errors and log errors
    logging.error(f"MySQL Error: {str(e)}")
    print("MySQL Error:", str(e))
except Exception as e:
    # Handle other exceptions and log errors
    logging.error(f"Error: {str(e)}")
    print("An error occurred:", str(e))
finally:
    # Close the database connection
    if db.is_connected():
        cursor.close()
        db.close()
