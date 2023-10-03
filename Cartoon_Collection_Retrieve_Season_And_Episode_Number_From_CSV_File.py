#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 01:12:36 2023

@author: michaelcintolo

Description: "Show_title (Production_Year) S00E00 - Episode_Title.File_Ext"

            "S" is for Season Number
            "E" is for Episode Number
            
            There are files trhat are missing the Season Number and Episode Number.
            Created a CSV file with two columns the first is "S00E00" and the second 
            is the Episode_Title, that was retrieved from a web site. This program 
            Will read in the CSV file and put it into a Dictionary. Then it will cycle
            Through the video files, parse out the fields, match the Episode_Titles and 
            update the file name if there is a match.

"""

import os
import csv

# Define the paths
csv_file_path = '//home/michaelcintolo/Programming/InputFiles/Currious_George_Episode_List.csv'
directory_path = '/home/michaelcintolo/Videos/VideosToUpdate/'

# Load the CSV data into a dictionary for easy lookup
episode_data = {}
with open(csv_file_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header row if present
    for row in reader:
        episode_data[row[1].strip()] = row[0].strip()  # Column B (Episode_Title) to Column A (Season and Episode)

# Function to parse the filename
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

# Function to rename files
def rename_files(directory_path):
    for filename in os.listdir(directory_path):
        # Parse out the file name
        show_title, production_year, _, _, episode_title, file_ext = parse_file_name(filename)

        # Check if episode_title exists in the episode_data dictionary
        if episode_title in episode_data:
            season_episode = episode_data[episode_title]
            new_filename = f"{show_title} ({production_year}) {season_episode} - {episode_title}.{file_ext}"

            # Rename the file
            old_file_path = os.path.join(directory_path, filename)
            new_file_path = os.path.join(directory_path, new_filename)
            os.rename(old_file_path, new_file_path)

# Call the function to rename files
rename_files(directory_path)