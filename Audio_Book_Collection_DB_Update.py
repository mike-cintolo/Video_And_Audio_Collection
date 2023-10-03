#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 09:26:02 2023

@author: michaelcintolo

Description: This program will cycle through all the Audio Book Collection on a local hard drive,
            parse out the fields in the file/folder name and add a row to a database table for each file.
            The naming convention for the main folder for each audio book is "Book_Title by Author".
            The naming convention for each file name is "Book_Title (Chapter_Number) - Chapter_Title.mp3".
            The databse is Entertainment.AudioBookCollection and the structure is:
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

# Initialize a file count variable
file_count = 0

# Iterate through all folders in the specified directory
for root, dirs, _ in os.walk(audio_book_directory):
    for folder in dirs:
        # Extract Author_Name from folder name
        author_name = folder.split(' by ')[-1]

        # Iterate through files in the folder
        folder_path = os.path.join(root, folder)
        for filename in os.listdir(folder_path):
            if filename.endswith(('mp3', 'mp4', 'flac', 'wav', 'wma', 'aac')): 
                # Find the last period in the filename (should be the extension)
                # Use os.path.splitext to extract the file extension correctly
                _, file_ext_with_dot = os.path.splitext(filename)
                file_ext = file_ext_with_dot[1:].lower()
                
                # Increment the file count
                file_count += 1
     
                # Print the filename and file count to the console
                print(f"Processing file {file_count}: {filename}")

                # Split the file name to extract information
                file_parts = filename[:-4].split(' - ')

                chapter_title = file_parts[1]

                # Check if there are enough parts to proceed
                if len(file_parts) == 2:
                    # First get book_title
                    book_title = file_parts[0].split(' (')[-2]

                    # Now get chapter
                    chapter_number = file_parts[0].split(' (')[+1]
                    chapter_number = chapter_number.lstrip('C')
                    chapter_number = chapter_number.rstrip(')')

                    # Check if the audiobook already exists in the database
                    select_query = "SELECT COUNT(*) FROM AudioBookCollection WHERE File_Name = %s"
                    select_values = (filename,)

                    cursor.execute(select_query, select_values)
                    result = cursor.fetchone()[0]

                    if result == 0:
                        # If the audiobook doesn't exist, insert it into the database
                        insert_query = "INSERT INTO AudioBookCollection (Author, Book_Title, Chapter_Number, Chapter_Title, File_Ext, File_Name) VALUES (%s, %s, %s, %s, %s, %s)"
                        insert_values = (author_name, book_title, chapter_number, chapter_title, file_ext, filename)

                        cursor.execute(insert_query, insert_values)
                        db.commit()

# Close the database connection
db.close()
