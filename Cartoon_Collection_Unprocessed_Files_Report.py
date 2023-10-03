#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 22:22:14 2023

@author: michaelcintolo

Description: "Show_title (Production_Year) S00E00 - Episode_Title.File_Ext"

            "S" is for Season Number
            "E" is for Episode Number
            
            Not all files have a Season Number and/or Episode Number. 
            Some will have neither. 
            Cartoon movies only have Show_Title and Production_Year 
            and possibly a tag [Animated] after Production_Year and before extention.
            Cycle through the files in the directory.
            Check to see if the file has been updated in the database, if it has do nothing.
            If the file has not been updated in the database then add it CSV Report.
           
# Directory where Cartoon files are located
# base_directory = '/home/michaelcintolo/Videos/VideosToUpdate/' # Test
base_directory = '/run/media/michaelcintolo/Primary/1. Cartoons/' # Production
"""

import os
# import csv
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

# Directory where Cartoon files are located
# cartoon_show_directory = '/home/michaelcintolo/Videos/VideosToUpdate/' # Test
cartoon_show_directory = '/run/media/michaelcintolo/Primary/1. Cartoons/' # Production

# Output file path for missing TV show files
output_file_path = '/home/michaelcintolo/Programming/OutputFiles/Cartoon_Collection_Uprocessed_Files_Report.csv'

# Initialize a file count variable
file_count = 0

try:
    # Create a list to store missing TV show files
    missing_cartoons = []

    # Iterate through all files in the TV show directory
    for root, _, files in os.walk(cartoon_show_directory):
        for filename in files:
            # Use os.path.splitext to extract the file extension correctly
            _, file_ext_with_dot = os.path.splitext(filename)
            file_ext = file_ext_with_dot[1:].lower()

            # Increment the file count
            file_count += 1

            # Print the filename and file count to the console
            print(f"Processing file {file_count}: {filename}")

            file_path = os.path.join(root, filename)

            # Check if the TV show exists in the database by counting matching records
            cursor.execute("SELECT COUNT(*) FROM CartoonCollection WHERE File_Name = %s", (filename,))
            result = cursor.fetchone()

            # You need to consume the result using fetchone() or fetchall()
            # This can be done by simply reading the result variable
            _ = result  # Consuming the result, no need to use

            count = result[0]  # Get the count from the result

            if count == 0:
                # Inside the loop where you add missing TV show files to the list
                # Construct a tuple with file_path and filename
                file_tuple = (file_ext,file_path, filename)
                
                # Add the tuple to the missing_cartoons list
                missing_cartoons.append(file_tuple)

    # Create a DataFrame from the missing_cartoons list
    missing_cartoons_df = pd.DataFrame(missing_cartoons, columns=["File_Ext", "File_Path", "Filename"])  

    # Save the missing TV show information to a CSV file
    missing_cartoons_df.to_csv(output_file_path, index=False, columns=["File_Ext", "File_Path", "Filename"])  

except Exception as e:
    print("An error occurred:", str(e))
finally:
    # Close the database connection
    if db.is_connected():
        cursor.close()
        db.close()

print(f"Cartoon Unprocessed Files Report saved to {output_file_path}")
