#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 01:12:36 2023

@author: michaelcintolo

Description: Most Audio Book files only included the chapter number, not the title. I extracted the 
            chapter number and title from the web and put them into a CSV file. This program will 
            search the CSV file for the chapter number and then update the file name with the chapter 
            title. The CSV file is named the title of the book.
            
            The naming convention for the main folder for each audio book is "Book_Title by Author".
            
            The naming convention for each file name is 
            "Book_Title (Chapter_Number) - Chapter_Title.File_Ext".
            
            The databse is Entertainment.AudioBookCollection and the structure is:
                Author VARCHAR(40),
                Book_Title VARCHAR(80),
                Chapter_Number INT,
                Chapter_Title VARCHAR(255),
                File_Ext VARCHAR(10),
                File_Name VARCHAR(255)
     
Collections: CartoonCollection, MovieCollection, TVShowCollection, RadioShowCollection, MusicCollection, AudioBookCollection

"""

import os
import csv

# Define the paths
csv_file_path = '/home/michael/Programming/File_Management/Input/'
directory_path = '/home/michael/Music/AudioToUpdate/'

# Load the CSV data into a dictionary for easy lookup
book_data = {}

# Initialize variables to store data
data_record = {
    "author": "",
    "book_title": "",
    "chapter_number": "",
    "chapter_title": "",
    "file_ext": "",
    "file_name": ""
}

# Define function to parse out file name elements
def parse_file_name(file_name, data_record):
    
    # Initialize default values for fields
    data_record["book_title"], data_record["chapter_number"], data_record["chapter_title"], data_record["file_ext"] = "Unknown", "0", "Unknown", "Unknown"

    # Initilaize data record file name with file name passed in
    data_record["file_name"] = file_name
    
    # Find the last period in the filename (should be the extension)
    # Use os.path.splitext to extract the file extension correctly
    _, file_ext_with_dot = os.path.splitext(file_name)
    data_record["file_ext"] = file_ext_with_dot[1:].lower()

    # Split the file name to extract information
    file_parts = file_name[:-4].split(' - ')

    data_record["chapter_title"] = file_parts[1]

    # Check if there are enough parts to proceed
    if len(file_parts) == 2:
        # First get book_title
        data_record["book_title"] = file_parts[0].split(' (')[-2]

        # Now get chapter
        data_record["chapter_number"] = file_parts[0].split(' (')[+1]
        # data_record["chapter_number"] = data_record["chapter_number"].lstrip('C')
        data_record["chapter_number"] = data_record["chapter_number"].rstrip(')')

# Define function to retrieve contents of csv file
def load_csv_file(csv_file_path, book_data):
    
   with open(csv_file_path, 'r') as csvfile:
       reader = csv.reader(csvfile)
       
       next(reader)  # Skip the header row if present
       
       for row in reader:
           book_data[row[0].strip()] = row[1].strip()  # Column A (Chapter_Number), Column B (Chapter_Title) 
    
# Function to rename files
def rename_files(csv_file_path, directory_path):
    
    # Get a list of filenames in the directory
    filenames = os.listdir(directory_path)

    # Check if the list is not empty
    if filenames:
        # Retrieve the book_title from the first filename
        first_filename = filenames[0]
        book_title = first_filename.split(' (')[0]

        # Construct the CSV file path based on the parsed book_title
        csv_file_path = os.path.join(csv_file_path, f'{book_title}.csv')
        
        # Load csv file into book_data
        load_csv_file(csv_file_path, book_data)
    
        # Cycle through all files in the directory and rename them
        for filename in os.listdir(directory_path):
            
            # Parse out the file name
            parse_file_name(filename, data_record)
    
            # Check if chapter_number exists in the data_record dictionary
            chapter_number = data_record["chapter_number"]
            
            # Find the index of the chapter_number in book_data
            chapter_title = ""
            
            for key in book_data.keys():
                
                if key.find(chapter_number) != -1:
                    
                    chapter_title = book_data[key]  
                    
                    break
                
            # Check if the chapter_number was found in book_data
            if chapter_title:
                
                # Get the chapter_title using the found key
                data_record["chapter_title"] = chapter_title
                
                # Construct the new filename
                new_filename = f'{data_record["book_title"]} ({data_record["chapter_number"]}) - {data_record["chapter_title"]}.{data_record["file_ext"]}'
    
                # Rename the file
                old_file_path = os.path.join(directory_path, filename)
                new_file_path = os.path.join(directory_path, new_filename)
                os.rename(old_file_path, new_file_path)

# Call the function to rename files
rename_files(csv_file_path, directory_path)