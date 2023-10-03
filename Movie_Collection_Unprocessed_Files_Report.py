#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 22:22:14 2023

@author: michaelcintolo

Description: This program will cycle through all the Movie Collection on a local hard drive,
            Check to see if the file name exist in the main databse table. 
            If the file does not exist add it to the Movie Unprocessed File Report.
            
            The naming convention for each file name is:
                "Movie_Title (Prod_Year) Actor_Name, Actor_Name [Genre, Genre].mp3".
                There may be one or many actors seperated by a comma.
                There may be one or many genres seperated by a comma.
                
            The five database tables that reside in the Entertainment databse: 
                MovieCollection, Actors, Genres, MovieActors and MovieGenres.
                
# Directory where movie files are located
# movies_directory = '/home/michaelcintolo/Videos/VideosToUpdate/' # Test
movies_directory = '/run/media/michaelcintolo/Primary/2. Movies/' # Production
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

# Directory where movie files are located
# movies_directory = '/home/michaelcintolo/Videos/VideosToUpdate/' # Test
movies_directory = '/run/media/michaelcintolo/Primary/2. Movies/' # Production

# Output file path for missing TV show files
output_file_path = '/home/michaelcintolo/Programming/OutputFiles/Movie_Collection_Uprocessed_Files_Report.csv'

# Initialize a file count variable
file_count = 0

try:
    # Create a list to store missing TV show files
    missing_movies = []

    # Iterate through all files in the TV show directory
    for root, _, files in os.walk(movies_directory):
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
            cursor.execute("SELECT COUNT(*) FROM MovieCollection WHERE File_Name = %s", (filename,))
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
                missing_movies.append(file_tuple)

    # Create a DataFrame from the missing_cartoons list
    missing_movies_df = pd.DataFrame(missing_movies, columns=["File_Ext", "File_Path", "Filename"])  

    # Save the missing TV show information to a CSV file
    missing_movies_df.to_csv(output_file_path, index=False, columns=["File_Ext", "File_Path", "Filename"])  

except Exception as e:
    print("An error occurred:", str(e))
finally:
    # Close the database connection
    if db.is_connected():
        cursor.close()
        db.close()

print(f"Movie Unprocessed Files Report saved to {output_file_path}")
