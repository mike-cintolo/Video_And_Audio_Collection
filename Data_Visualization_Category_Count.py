#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 06:31:09 2023

@author: michaelcintolo
"""

import mysql.connector
import json
import matplotlib.pyplot as plt
import numpy as np

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

# Define the main tables in the database
tables = [
    "TVShowCollection",
    "RadioShowCollection",
    "MusicCollection",
    "MovieCollection",
    "CartoonsCollection",
    "AudioBookCollection"
]

# Initialize empty lists to store category names and counts
categories = []
content_counts = []

# Iterate through the tables and retrieve counts
for table in tables:
    # Query to retrieve counts from the current table
    query = f"SELECT COUNT(*) AS count FROM {table}"
    
    # Execute the query
    cursor = db.cursor(dictionary=True)
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchone()
    
    # Extract the count and table name
    count = result["count"]
    category = table.replace("Collection", "")  # Remove "Collection" from table name
    
    # Append the category name and count to the respective lists
    categories.append(category)
    content_counts.append(count)

# Create a horizontal bar chart
plt.figure(figsize=(12, 8))
plt.barh(categories, content_counts, color='skyblue')
plt.xlabel('Number of Items', fontsize=14, fontweight='bold')
plt.ylabel('Multimedia Categories', fontsize=14, fontweight='bold')
plt.title('Distribution of Multimedia Content Categories', fontsize=16, fontweight='bold')

# Annotate each bar with the count
for i, count in enumerate(content_counts):
    plt.text(count + 10, i, str(count), va='center', fontsize=12, fontweight='bold', color='black')

# Customize colors
colors = ['lightcoral', 'lightsalmon', 'lightseagreen', 'lightgreen', 'lightsteelblue', 'lightskyblue']
plt.barh(categories, content_counts, color=colors)

plt.show()

# Close the database connection
db.close()
