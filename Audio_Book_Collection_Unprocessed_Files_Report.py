#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 08:58:59 2023

@author: michaelcintolo

Description: This program will cycle through all the Audio Book Collection on a local hard drive,
            parse out the fields in the file/folder name and add a row to a database table for each file.
            The naming convention for the main folder for each audiobook is "Book_Title by Author".
            The naming convention for each file name is "Book_Title (Chapter) - Chapter_Title.mp3".
            The database is Entertainment.AudioBookCollection and the structure is:
                Author VARCHAR(40),
                Book_Title VARCHAR(80),
                Chapter_Number INT,
                Chapter_Title VARCHAR(255),
                File_Ext VARCHAR(10),
                File_Name VARCHAR(255)

# Define the directory where your audio book files are located
# audio_book_directory = '/home/michaelcintolo/Music/Mp3sToUpdate/' # Test
audio_book_directory = '/run/media/michaelcintolo/Primary/6. Audio Books/' # Productionm
"""
import os
import pandas as pd
import mysql.connector
import json

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

# Define the directory where your audio book files are located
# audio_book_directory = '/home/michaelcintolo/Music/Mp3sToUpdate/' # Test
audio_book_directory = '/run/media/michaelcintolo/Primary/6. Audio Books/' # Productionm

# Output file path for missing TV show files
output_file_path = '/home/michaelcintolo/Programming/OutputFiles/Audio_Book_Collection_Unprocessed_Files_Report.csv'

# Create a list to store information about missing audiobooks
missing_audiobooks = []

# Initialize a file count variable
file_count = 0

try:
    # Create a list to store missing TV show files
    missing_tv_shows = []

    # Iterate through all files in the TV show directory
    for root, _, files in os.walk(audio_book_directory):
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
            cursor.execute("SELECT COUNT(*) FROM AudioBookCollection WHERE File_Name = %s", (filename,))
            result = cursor.fetchone()

            # You need to consume the result using fetchone() or fetchall()
            # This can be done by simply reading the result variable
            _ = result  # Consuming the result, no need to use

            count = result[0]  # Get the count from the result

            if count == 0:
                # Inside the loop where you add missing TV show files to the list
                # Construct a tuple with file_path and filename
                file_tuple = (file_ext, file_path, filename)
                
                # Add the tuple to the missing_tv_shows list
                missing_audiobooks.append(file_tuple)

    # Create a DataFrame from the missing_tv_shows list
    missing_audiobooks_df = pd.DataFrame(missing_audiobooks, columns=["File_Ext", "File_Path", "Filename"])  

    # Save the missing TV show information to a CSV file
    missing_audiobooks_df.to_csv(output_file_path, index=False, columns=["File_Ext", "File_Path", "Filename"])  

except Exception as e:
    print("An error occurred:", str(e))
finally:
    # Close the database connection
    if db.is_connected():
        cursor.close()
        db.close()

print(f"Audio Book Unprocessed Files Report saved to {output_file_path}")
