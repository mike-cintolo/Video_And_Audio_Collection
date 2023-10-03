#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 13:20:02 2023

@author: michaelcintolo

Program: Music_Collection_Update_DB.py

Description: The music collection is organized by artist folder and all the music files for the artist 
            in the artist folder. Thos program will cycle through all thye artist folders, then through
            all the artist music files, parse out the individual pieces from the file name, then
            use the Last.FM API to retrieve back the genre. If the genre is not received from Last FM, 
            the program will use the Discorgs API to make a second attampt at retrieving genre. 
            Next this program will insert a record for each music file in the repository.
            A CSV file is produced with all records inserted into the database.
            
            The naming standard for the files are: 
            "Artist_Name (Release_Year) Album_Title - Song_Title.mp3" for albums 
            "Artist_Name (Release_Year) - Song_Title.mp3" for a single. 
            
# Define the directory where your audio book files are located
# music_directory = '/home/michaelcintolo/Music/Mp3sToUpdate/' # Test
music_directory = '/run/media/michaelcintolo/Primary/5. Music/' # Productionm
"""

import os
import pandas as pd
import requests
import json 
import mysql.connector

# Define the folder output CSV file path
csv_file_path = '/home/michaelcintolo/Programming/OutputFiles/Music_Collection_DB_Update.csv'

# Define the directory where your audio book files are located
# music_directory = '/home/michaelcintolo/Music/Mp3sToUpdate/' # Test
music_directory = '/run/media/michaelcintolo/Primary/5. Music/' # Productionm

# Initialize a file count variable
file_count = 0

# Initialize an empty list to store the data
data = []

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
 
# Read Discogs credentials from JSON file
with open('/home/michaelcintolo/Programming/ConfigFiles/discogs_credentials.json', 'r') as json_file:
    credentials = json.load(json_file)

DISCOGS_API_TOKEN = credentials["api_token"]
DISCOGS_API_SECRET = credentials["api_secret"]

# Read Last.FM credentials from JSON file
with open('/home/michaelcintolo/Programming/ConfigFiles/last_fm_credentials.json', 'r') as json_file:
    credentials = json.load(json_file)
    
LAST_FM_API_KEY = credentials["api_key"]

# Function to get genre information from Last.fm API
def get_genre_last_fm(artist_name, track_name):
    url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={LAST_FM_API_KEY}&artist={artist_name}&track={track_name}&format=json'
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            json_data = response.json()
            if 'track' in json_data and 'toptags' in json_data['track'] and 'tag' in json_data['track']['toptags']:
                tags = json_data['track']['toptags']['tag']
                if tags:
                    genre = tags[0]['name'].title()
                    
                    # Make sure what was returned was not greater than 10 characters.
                    if len(genre) > 10:
                        genre = 'Unknown'
                        
                    return genre
        except (KeyError, ValueError):
            pass
    
    return 'Unknown'

# Function to get genre information from Discogs API
def get_genre_discogs(artist_name, release_title):
    base_url = 'https://api.discogs.com/database/search'
    params = {
        'artist': artist_name,
        'release_title': release_title,
        'key': DISCOGS_API_TOKEN,
        'secret': DISCOGS_API_SECRET
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            json_data = response.json()
            if 'results' in json_data and len(json_data['results']) > 0:
                genre_list = json_data['results'][0]['genre']
               
                # Use only the first item
                genre = str(genre_list[0]).strip()
                
                # Make sure what was returned was not greater than 10 characters.
                if len(genre) > 10:
                    genre = 'Unknown'
                    
                return genre
        except (KeyError, ValueError):
            pass

    return 'Unknown'

# Function to check if a row with the given file_name exists in the database
def is_row_in_db(cursor, file_name):
    query = "SELECT 1 FROM MusicCollection WHERE File_Name = %s"
    cursor.execute(query, (file_name,))
    return cursor.fetchone() is not None

# Function to parse file name and add data to the list
def parse_filename(file_name, data_record):
     
    # Print the filename and file count to the console
    print(f"Processing file {file_count}: {file_name}")    
    
    # Find the last period in the filename (should be the extension)
    # Use os.path.splitext to extract the file extension correctly
    _, file_ext_with_dot = os.path.splitext(file_name)
    data_record["file_ext"] = file_ext_with_dot[1:].lower()

    data_record["file_name"] = file_name

    open_parenthesis = file_name.find('(')
    close_parenthesis = file_name.find(')')

    if open_parenthesis != -1 and close_parenthesis != -1:
        data_record["artist_name"] = file_name[:open_parenthesis].strip()
        data_record["release_year"] = file_name[open_parenthesis + 1:close_parenthesis].strip()
        remainder = file_name[close_parenthesis + 1:].strip()

        hyphen_position = remainder.find(' – ')
        period_position = remainder.rfind('.')

        if hyphen_position != -1:
            data_record["album_title"] = remainder[:hyphen_position].strip()
            data_record["song_title"] = remainder[hyphen_position + 3:period_position].strip()
        else:
            hyphen_position = remainder.strip().find('-')
            data_record["album_title"] = ''
            data_record["song_title"] = remainder[hyphen_position + 1:period_position].strip()

        data_record["genre"] = get_genre_last_fm(data_record["artist_name"], data_record["song_title"])

        # If genre is still 'Unknown,' try Discogs
        if data_record["genre"] == 'Unknown':
            data_record["genre"] = get_genre_discogs(data_record["artist_name"], data_record["album_title"])

        data.append([data_record["artist_name"], data_record["release_year"], data_record["album_title"], data_record["song_title"], data_record["genre"], data_record["file_ext"], data_record["file_name"]])

    else:
        data.append(["", "", "", "", "Unknown", data_record["file_ext"], data_record["file_name"]])
        
# Create a new CSV file each time the program runs
columns = ['Artist Name', 'Release Year', 'Album Title', 'Song Title', 'Genre', 'Filed Ext', 'File Name']
df = pd.DataFrame(data, columns=columns)
df = df.dropna()  # Remove rows with missing values
df.to_csv(csv_file_path, index=False)

# Initialize variables to store data
data_record = {
    "artist_name": "",
    "release_year": "",
    "album_title": "",
    "song_title": "",
    "genre": "",
    "file_ext": "",
    "file_name": ""
}

# Traverse the folder and its subfolders
for root, _, files in os.walk(music_directory):
    for file in files:
        file_path = os.path.join(root, file)
        
        # Increment the file count
        file_count += 1
             
        # Extract file name without extension
        file_name, _ = os.path.splitext(file)

        # Check if the file name is already in the database
        if is_row_in_db(cursor, file_name):
            print(f"Skipping file {file_count}: {file_name}")
            continue

        # Parse out file name and process the file
        parse_filename(file, data_record)

        # Insert the row into the database
        cursor.execute("INSERT INTO MusicCollection (Artist_Name, Release_Year, Album_Title, Song_Title, Genre, File_Ext, File_Name) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (data_record["artist_name"], data_record["release_year"], data_record["album_title"], data_record["song_title"], data_record["genre"], data_record["file_ext"], data_record["file_name"]))

        # Commit the database transaction
        db.commit()

        print(f'Inserted into the database and saved data for file {file_count}: {file_name}')
           
# Append the data to the CSV file
df = pd.DataFrame(data, columns=columns)
df.to_csv(csv_file_path, index=False, header=False, mode='a')

print(f'Data saved to {csv_file_path}')
