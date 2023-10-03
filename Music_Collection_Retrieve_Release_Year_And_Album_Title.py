#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 16:42:47 2023

@author: michaelcintolo

Program: Music_Collection_Retrieve_Release_Year_And_Album_Title.py

Description: This program uses the Spotify API to retrieve back the Album Title and the Year Released.
            The program will also update the file name to include this information.
            The naming convention is "Artist_Name (Release_Year) Album_Title - Song_Title.mp3"
            
            This program will attempt to rettieve release year and album title from Spotify.
            
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import csv  
import shutil
import json  

# Read Discogs credentials from JSON file
with open('/home/michaelcintolo/Programming/ConfigFiles/spotify_credentials.json', 'r') as json_file:
    credentials = json.load(json_file)

SPOTIPY_CLIENT_ID = credentials["client_id"]
SPOTIPY_CLIENT_SECRET = credentials["client_secret"]

# Initialize the Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Specify the directory containing your music files
music_directory = '/home/michaelcintolo/Music/Mp3sToUpdate/'

# Define a function to remove text within parentheses
def remove_text_in_parentheses(text):
    return re.sub(r'\([^)]*\)', '', text).strip()  # Removes text within ()

# Specify the directory for the CSV file
csv_directory = '/home/michaelcintolo/Programming/OutputFiles/'

# Create a CSV file to log the file names that are not updated
csv_file = open(os.path.join(csv_directory, 'Music_Files_Not_Updated.csv'), 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['File Name', 'Error Message'])  # Write header row

# Specify the directory to move updated files
updated_directory = '/home/michaelcintolo/Music/MP3sUpdated/'

# Loop through the files in the directory
for filename in os.listdir(music_directory):
    if filename.endswith('.mp3'):
        # Extract artist name and song title from the filename
        file_parts = filename.replace('.mp3', '').split(' - ')
        if len(file_parts) == 2:
            artist_name, song_title = file_parts
            
            # Check if a "(release_year)" exists in the file name
            year_match = re.search(r'\((\d{4})\)', artist_name)
            if year_match:
                existing_release_year = year_match.group(1)
                # Remove "(release_year)" from artist name
                artist_name = artist_name.replace(year_match.group(0), '')
            else:
                existing_release_year = None
            
            # Continue with the search
            try:
                results = sp.search(q=f'artist:{artist_name} track:{song_title}', type='track', limit=1)
                
                if results['tracks']['total'] > 0:
                    track = results['tracks']['items'][0]
                    
                    # Extract release year and album title
                    release_year = track['album']['release_date'][:4]
                    album_title = track['album']['name']
                    
                    # Remove text within parentheses from album title
                    album_title = remove_text_in_parentheses(album_title)
                    
                    # Construct the new file name
                    if existing_release_year:
                        # If "(release_year)" already exists, replace it with the year from Spotify
                        new_filename = f'{artist_name} ({release_year}) {album_title} - {song_title}.mp3'
                    else:
                        new_filename = f'{artist_name} ({release_year}) {album_title} - {song_title}.mp3'
                    
                    # Rename the music file
                    old_filepath = os.path.join(music_directory, filename)
                    new_filepath = os.path.join(music_directory, new_filename)
                    
                    try:
                        os.rename(old_filepath, new_filepath)
                        print(f'Renamed: {old_filepath} -> {new_filepath}')
                        
                        # Move the updated file to the 'MP3sUpdated' folder
                        shutil.move(new_filepath, os.path.join(updated_directory, new_filename))
                        print(f'Moved to {updated_directory}: {new_filename}')
                    except Exception as e:
                        print(f'Error renaming {old_filepath}: {str(e)}')
                else:
                    error_message = f'Metadata not found for {artist_name} - {song_title}'
                    print(error_message)
                    
                    # Log the file name and error message to the CSV file
                    csv_writer.writerow([filename, error_message])
            except Exception as e:
                error_message = f'Error during Spotify search: {str(e)}'
                print(error_message)
                
                # Log the file name and error message to the CSV file
                csv_writer.writerow([filename, error_message])

# Close the CSV file
csv_file.close()
