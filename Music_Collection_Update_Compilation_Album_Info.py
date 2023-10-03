#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 16:41:23 2023

@author: michaelcintolo

Program: Update_Compilation_Album_Info.py

Description: This program will use the Spotify API to update music files from compilation albums.
            The program will retrieve back the Release_Year for music files from compiltion albums.
            The program will update the music file name to add the Release_Year, move the updated
            file to an artist folder in a completed folder and then update a log file with the 
            Updated file information.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json  

# Read Discogs credentials from JSON file
with open('/home/michaelcintolo/Programming/ConfigFiles/spotify_credentials.json', 'r') as json_file:
    credentials = json.load(json_file)

SPOTIPY_CLIENT_ID = credentials["client_id"]
SPOTIPY_CLIENT_SECRET = credentials["client_secret"]

# Initialize Spotify API client
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Input and output directories
input_directory = '/home/michaelcintolo/Music/Mp3sToUpdate/'
output_directory = '/home/michaelcintolo/Music/Mp3sUpdated/'

# Create an empty DataFrame to store file and artist folder names
data = pd.DataFrame(columns=['File Name', 'Artist Folder'])

# Iterate through folders in the input directory
for album_folder in os.listdir(input_directory):
    album_path = os.path.join(input_directory, album_folder)

    # Ensure it's a directory
    if os.path.isdir(album_path):
        # Iterate through music files in the album folder
        for music_file in os.listdir(album_path):
            if music_file.endswith('.mp3'):
                # Parse out album title and song title from folder and file names
                album_title = album_folder
                song_title = os.path.splitext(music_file)[0]

                # Search for the album on Spotify
                album_results = sp.search(q=f'album:"{album_title}"', type='album')

                # If the album is found, search for the track within that album
                if album_results['albums']['items']:
                    album_id = album_results['albums']['items'][0]['id']
                    track_results = sp.album_tracks(album_id)
                    for track_info in track_results['items']:
                        if track_info['name'] == song_title:
                            # Extract artist and release year information from the track
                            artist_name = track_info['artists'][0]['name']
                            release_year = track_info['album']['release_date'][:4]

                            # Create the artist folder (remove leading/trailing spaces)
                            artist_folder = os.path.join(output_directory, artist_name.strip())

                            # Create the artist folder if it doesn't exist
                            if not os.path.exists(artist_folder):
                                os.makedirs(artist_folder)

                            # Rename the music file
                            new_file_name = f'{artist_name.strip()} ({release_year}) {album_title.strip()} - {song_title.strip()}.mp3'
                            new_file_path = os.path.join(artist_folder, new_file_name)
                            old_file_path = os.path.join(album_path, music_file)

                            # Move the file to the artist folder
                            os.rename(old_file_path, new_file_path)

                            # Add file and artist folder names to the DataFrame
                            data = data.append({'File Name': new_file_name, 'Artist Folder': artist_name.strip()}, ignore_index=True)
                            break
                else:
                    # If the album is not found on Spotify, log it and skip renaming and moving
                    data = data.append({'File Name': music_file, 'Artist Folder': 'Not Found on Spotify'}, ignore_index=True)

# Save the DataFrame to a spreadsheet
spreadsheet_path = '/home/michaelcintolo/Programming/OutputFiles/Music_Compilation_Album_Update.xlsx'
data.to_excel(spreadsheet_path, index=False, engine='openpyxl')
