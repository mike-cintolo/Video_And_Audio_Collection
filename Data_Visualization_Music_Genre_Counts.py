#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 06:54:56 2023

@author: michaelcintolo
"""

import mysql.connector
import json
import matplotlib.pyplot as plt
import squarify

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

# Query to retrieve music genre counts from the database
query = """
    SELECT genre, COUNT(*) AS count
    FROM MusicCollection
    GROUP BY genre
    ORDER BY count DESC
"""

# Execute the query
cursor = db.cursor(dictionary=True)
cursor.execute(query)

# Fetch the results
results = cursor.fetchall()

# Separate genre names and counts from the results
genres = [row["genre"] for row in results]
genre_counts = [row["count"] for row in results]

# Choose the top N genres to display, and group the rest into "Other"
N = 25  # Adjust N as needed
top_genres = genres[:N]
top_counts = genre_counts[:N]
other_count = sum(genre_counts[N:])

# Append "Other" category to the top genres
top_genres.append("Other")
top_counts.append(other_count)

# Create a treemap
plt.figure(figsize=(10, 6))
squarify.plot(
    sizes=top_counts,
    label=[f"{genre}\n({count})" for genre, count in zip(top_genres, top_counts)],
    alpha=0.7,
    color=['lightcoral', 'lightsalmon', 'lightseagreen', 'lightgreen', 'lightsteelblue', 'lightskyblue', 'lightpink', 'lightyellow', 'lightcyan', 'lightgray', 'lightblue']
)
plt.axis('off')
plt.title(f'Top {N} Music Genres and "Other"', fontsize=16, fontweight='bold')

plt.show()

# Close the database connection
db.close()
