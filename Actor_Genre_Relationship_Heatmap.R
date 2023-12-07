# Load required libraries
library(ggplot2)
library(dplyr)

# Specify the path to your CSV file
csv_file_path <- "/home/michaelcintolo/Programming/File_Management/Input/Actor_Genre_Relationship_Heatmap.csv"

# Read the CSV file into a data frame
movie_data <- read.csv(csv_file_path)

# Create a count of relationships
relationship_count <- movie_data %>%
  group_by(Actor_Name, Genre_Name) %>%
  summarise(Relationship_Count = n())

# Choose the top N actors and genres
top_n_actors <- 10
top_n_genres <- 10

top_actors <- relationship_count %>%
  group_by(Actor_Name) %>%
  summarise(Total_Count = sum(Relationship_Count)) %>%
  top_n(top_n_actors, Total_Count)

top_genres <- relationship_count %>%
  group_by(Genre_Name) %>%
  summarise(Total_Count = sum(Relationship_Count)) %>%
  top_n(top_n_genres, Total_Count)

# Filter the data to include only the top N actors and genres
filtered_data <- relationship_count %>%
  filter(Actor_Name %in% top_actors$Actor_Name, Genre_Name %in% top_genres$Genre_Name)

# Create a heatmap using ggplot2
heatmap_plot <- ggplot(filtered_data, aes(x = Actor_Name, y = Genre_Name, fill = Relationship_Count)) +
  geom_tile() +
  labs(title = "Top Actor-Genre Relationship Heatmap", x = "Actor Name", y = "Genre Name", fill = "Relationship Count") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Display the heatmap
print(heatmap_plot)





