#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 09:45:53 2023

@author: michaelcintolo

Description: This program will cycle through all the Movie Collection on a local hard drive,
            parse out the fields in the file name and update five database tables for each file.
            The naming convention for each file name is:
                "Movie_Title (Prod_Year) Actor_Name, Actor_Name [Genre, Genre].mp3".
                There may be one or many actors seperated by a comma.
                There may be one or many genres seperated by a comma.
                
            The five database tables that reside in the Entertainment databse: 
                MovieCollection, Actors, Genres, MovieActors and MovieGenres.
                
# Directory where movie files are located
# movie_root = '/home/michaelcintolo/Videos/VideosToUpdate/' # Test
movie_root = '/run/media/michaelcintolo/Primary/2. Movies/' # Production

"""
import json
import mysql.connector
import os
import logging

# Set up logging
log_directory = '/home/michaelcintolo/Programming/OutputFiles/'
logging.basicConfig(filename=os.path.join(log_directory, 'movie_parser.log'), level=logging.INFO)
error_log = os.path.join(log_directory, 'movie_error.log')

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
# movie_root = '/home/michaelcintolo/Videos/VideosToUpdate/' # Test
movie_root = '/run/media/michaelcintolo/Primary/2. Movies/' # Production

# Initialize a file count variable
file_count = 0

# Define a function to parse file names
def parse_filename(filename):
    # Initialize default values for fields
    movie_title, production_year, actors, genres, file_ext = "Unknown", "1900", "Unknown", "Unknown", "Unknown"
    
    # ***** parse out show_title *****
    # Find the position of " ("
    start_position = 0
    end_position = filename.find(" (")
    
    # Extract the portion of the filename
    if end_position != -1:
        movie_title = filename[start_position:end_position].strip()
    
    # ***** parse out production_year *****
    # Find the positions of " (" and ")"
    start_position = filename.find(" (") + 2
    end_position = filename.find(")")
    
    # Extract the production_year
    if start_position != -1 and end_position != -1:
        production_year = filename[start_position:end_position]
               
    # ***** parse out actors *****
    start_position = filename.find(")")
    end_position = filename.find("[")

    # Extract the production_year
    if start_position != -1 and end_position != -1:
        # Load actors into string variable
        actors_str = filename[start_position + 1:end_position]

        # Seperate out actors 
        actors = [actor.strip() for actor in actors_str.split(',')]

   # ***** parse out genres *****
    start_position = filename.find("[")
    end_position = filename.find("]")

    # Extract the production_year
    if start_position != -1 and end_position != -1:
        # Load genres into string variable
        genres_str = filename[start_position + 1:end_position]
        
        # Seperate out genres 
        genres = [genre.strip() for genre in genres_str.split(',')]
        
    # ***** parse out the file_ext *****
    # Find the last period in the filename (should be the extension)
    # Use os.path.splitext to extract the file extension correctly
    _, file_ext_with_dot = os.path.splitext(filename)
    file_ext = file_ext_with_dot[1:].lower()

    return movie_title, production_year, actors, genres, file_ext

try:
    # Iterate through movie files in the specified directory
    for filename in os.listdir(movie_root):
        # Increment the file count for each processed file
        file_count += 1

        # Print the filename and file count to the console
        print(f"Processing file {file_count}/{len(os.listdir(movie_root))}: {filename}")

        file_path = os.path.join(movie_root, filename)
        if os.path.isfile(file_path):
            # Parse the file name
            parsed_info = parse_filename(filename)
            if parsed_info:
                movie_title, production_year, actors, genres, file_ext = parsed_info

                # Check if the movie exists in the database
                cursor.execute("SELECT Movie_ID FROM MovieCollection WHERE Movie_Title = %s AND Production_Year = %s", (movie_title, production_year))
                existing_movie = cursor.fetchone()

                if existing_movie:
                    # Log that the movie exists in the database and was skipped
                    logging.info(f"Movie '{movie_title}' ({production_year}) already exists in the database. Skipped file: {filename}")
                else:
                    # Insert actors into the Actors table and retrieve Actor_IDs
                    actor_ids = []
                    for actor in actors:
                        # Check if the actor already exists in the Actors table
                        cursor.execute("SELECT Actor_ID FROM Actors WHERE Actor_Name = %s", (actor,))
                        existing_actor = cursor.fetchone()
                        if existing_actor:
                            actor_id = existing_actor[0]
                        else:
                            # Insert the actor into the Actors table
                            cursor.execute("INSERT INTO Actors (Actor_Name) VALUES (%s)", (actor,))
                            db.commit()
                            cursor.execute("SELECT LAST_INSERT_ID()")
                            actor_id = cursor.fetchone()[0]
                        
                        actor_ids.append(actor_id)

                    # Insert genres into the Genres table and retrieve Genre_IDs
                    genre_ids = []
                    for genre in genres:
                        # Check if the genre already exists in the Genres table
                        cursor.execute("SELECT Genre_ID FROM Genres WHERE Genre_Name = %s", (genre,))
                        existing_genre = cursor.fetchone()
                        if existing_genre:
                            genre_id = existing_genre[0]
                        else:
                            # Insert the genre into the Genres table
                            cursor.execute("INSERT INTO Genres (Genre_Name) VALUES (%s)", (genre,))
                            db.commit()
                            cursor.execute("SELECT LAST_INSERT_ID()")
                            genre_id = cursor.fetchone()[0]
                        
                        genre_ids.append(genre_id)

                    # Insert movie information into the MovieCollection Table
                    cursor.execute("INSERT INTO MovieCollection (Movie_Title, Production_Year, File_Ext, File_Name) VALUES (%s, %s, %s, %s)",
                                   (movie_title, production_year, file_ext, filename))

                    db.commit()

                    # Retrieve the Movie_ID for the inserted movie
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    movie_id = cursor.fetchone()[0]

                    # Insert movie-genre relationships into MovieGenres table
                    for genre_id in genre_ids:
                        cursor.execute("INSERT INTO MovieGenres (Movie_ID, Genre_ID) VALUES (%s, %s)",
                                       (movie_id, genre_id))

                    # Insert movie-actor relationships into MovieActors table
                    for actor_id in actor_ids:
                        cursor.execute("INSERT INTO MovieActors (Movie_ID, Actor_ID) VALUES (%s, %s)",
                                       (movie_id, actor_id))

                    db.commit()

                    # Log a successful processing message to movie_parser.log
                    logging.info(f"Processed file: {filename}")

except mysql.connector.Error as db_error:
    # Handle database-related errors
    error_message = f"Database error: {db_error}"
    logging.error(error_message)
    print(error_message)

except Exception as e:
    # Handle other exceptions
    error_message = f"Error processing file '{filename}': {str(e)}"
    logging.error(error_message)
    print(error_message)
    with open(error_log, 'a') as err_file:
        err_file.write(error_message + '\n')

finally:
    # Close the database cursor and connection
    if cursor:
        cursor.close()
    if db and db.is_connected():
        db.close()
