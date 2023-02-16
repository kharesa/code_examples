import pandas as pd
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim import corpora

# Load the dataframe
df = pd.read_csv("your_file.csv")

# Define the function to preprocess the text
def preprocess_text(text):
    """
    Preprocess the text by tokenizing, removing stopwords, and lemmatizing
    """
    result = []
    for token in simple_preprocess(text):
        if token not in STOPWORDS and len(token) > 3:
            result.append(token)
    return result

# Preprocess the text in the column
text_data = df['your_column'].map(preprocess_text)

# Create a dictionary from the preprocessed text
dictionary = corpora.Dictionary(text_data)

# Create a corpus from the dictionary
corpus = [dictionary.doc2bow(text) for text in text_data]

# Perform LDA topic modeling on the corpus
num_topics = 10
lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=dictionary,
                                           num_topics=num_topics,
                                           random_state=100,
                                           update_every=1,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)

# Create a dataframe to store the top topics and their keywords
topic_keywords = pd.DataFrame(columns=['Topic', 'Keywords'])

# Iterate through the topics and their keywords
for i, topic in lda_model.show_topics(formatted=True, num_topics=num_topics, num_words=10):
    # Add the topic and its keywords to the dataframe
    topic_keywords = topic_keywords.append(pd.Series([i, topic], index=topic_keywords.columns), ignore_index=True)

# Print the dataframe with the top topics and their keywords
print(topic_keywords)
