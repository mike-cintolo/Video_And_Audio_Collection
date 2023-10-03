#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 07:20:08 2023

@author: michaelcintolo
"""

import mysql.connector
import json
import matplotlib.pyplot as plt

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

# Define the number of top genres you want to retrieve
top_n = 12  # You can change this to any number you prefer

# Execute the query to get all genres with counts
query = """
    SELECT g.Genre_Name, COUNT(mg.Movie_ID) AS Count
    FROM Genres g
    LEFT JOIN MovieGenres mg ON g.Genre_ID = mg.Genre_ID
    GROUP BY g.Genre_Name
    ORDER BY Count DESC
"""

# Execute the query
cursor = db.cursor(dictionary=True)
cursor.execute(query)

# Fetch all results
results = cursor.fetchall()

# Separate genre names and counts from the results
genres = [row["Genre_Name"] for row in results]
genre_counts = [row["Count"] for row in results]

# Check if the total number of genres is greater than top_n
if len(genres) > top_n:
    # Get the top "n" genres and their counts
    top_genres = genres[:top_n]
    top_counts = genre_counts[:top_n]

    # Sum the counts of the remaining genres as "Other"
    other_count = sum(genre_counts[top_n:])

    # Append "Other" to the top genres and its count
    top_genres.append("Other")
    top_counts.append(other_count)

    # Define custom colors for the segments
    custom_colors = ['gold', 'lightcoral', 'lightskyblue', 'lightgreen', 'lightsalmon',
                     'lightseagreen', 'lightsteelblue', 'lightcyan', 'lightpink', 'lightslategray',
                     'lightblue', 'lightyellow', 'lightgray', 'lightgreen', 'lightpink',
                     'lightblue', 'lightcoral', 'lightseagreen', 'lightsalmon', 'lightcyan']

    # Create a pie chart for the top genres with custom colors
    plt.figure(figsize=(8, 8))
    plt.pie(top_counts, labels=top_genres, autopct='%1.1f%%', startangle=140, colors=custom_colors)
    plt.title('Distribution of Movie Genres', fontsize=16, fontweight='bold')

    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.tight_layout()
    plt.show()
else:
    # If the total number of genres is not greater than top_n, create the chart as before
    plt.figure(figsize=(12, 6))
    plt.barh(genres, genre_counts, color='skyblue')
    plt.xlabel('Number of Movies', fontsize=14, fontweight='bold')
    plt.ylabel('Movie Genres', fontsize=14, fontweight='bold')
    plt.title('Distribution of Movie Genres', fontsize=16, fontweight='bold')

    # Annotate each bar with the count
    for i, count in enumerate(genre_counts):
        plt.text(count + 5, i, str(count), va='center', fontsize=12, fontweight='bold', color='black')

    plt.tight_layout()
    plt.show()

# Close the database connection
db.close()
