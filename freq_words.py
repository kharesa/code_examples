import pandas as pd
import nltk
from nltk.corpus import stopwords

# Load the dataframe
df = pd.read_csv("your_file.csv")

# Create an empty list to store the words
words = []

# Define the stopwords to exclude
stop_words = set(stopwords.words("english"))

# Iterate through the rows in the column
for row in df['your_column']:
    # Convert the text to lowercase
    row = row.lower()
    # Tokenize the text into words
    row_words = nltk.word_tokenize(row)
    # Filter out the stopwords
    row_words = [word for word in row_words if word not in stop_words]
    # Add the remaining words to the list
    words.extend(row_words)

# Count the frequency of each word
word_freq = nltk.FreqDist(words)

# Get the top 50 most frequent words
top_words = word_freq.most_common(50)

# Print the list of top words
print(top_words)
