#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 06:13:51 2023

@author: michaelcintolo
"""

import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Sample text data (replace with your multimedia data)
text_data = [
    "movie film action adventure",
    "music song artist album",
    "tv show series drama comedy",
    "radio program broadcast news",
    "audiobook narrator novel chapter"
]

# Combine text data into a single string
combined_text = ' '.join(text_data)

# Generate the word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)

# Display the word cloud using matplotlib
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Multimedia Content', fontsize=16)
plt.show()
