import pandas as pd
import matplotlib.pyplot as plt
import string
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import re
import emoji
extractor = URLExtract()
def fetch_stats(selected_user, df):

    # Filter dataframe only if a specific user is selected
    if selected_user != "over all":
        df = df[df['user'] == selected_user]


    # number of messages
    num_msgs = df.shape[0]

    # number of words (vectorized – faster)
    num_words = df['user_message'].str.split().str.len().sum()

    #num of meadia share
    num_media = df[df['user_message'] == '<Media omitted>'].shape[0]

    #num of link share
    all_url = []
    for msg in df['user_message']:
        urls = extractor.find_urls(msg)
        all_url.extend(urls)


    return num_msgs, num_words ,num_media, len(all_url)

## show top 5 member
def show_top_user(df):
    x = df['user'].value_counts().sort_values(ascending=False).head(5)
    new_df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'user':'name','count':'percentage'})


    fig, ax = plt.subplots()

    colors = ["red", "green", "blue", "orange", "purple"]

    ax.bar(x.index, x.values, color=colors[:len(x)])
    ax.set_xticklabels(x.index, rotation=90)
    ax.set_xlabel("user name")
    ax.set_ylabel("number of messages")

    return fig, x ,new_df  # return both plot and data


## clean massege


def clean_messages(df, selected_user):
    # Filter by selected user
    if selected_user != "over all":
        df = df[df['user'] == selected_user]

    # Remove unwanted messages
    temp = df[df['user_message'] != 'group_notification']
    temp = temp[~temp['user_message'].isin([
        '<Media omitted>', '<media omitted>', 'Media omitted', 'media omitted'
    ])]

    # Load stopwords
    with open('stop_words.txt', 'r', encoding='utf-8') as f:
        stop_words = set(f.read().splitlines())

    # Punctuation remover
    translator = str.maketrans('', '', string.punctuation)

    # URL pattern
    url_pattern = r'(https?://\S+|www\.\S+|https\S+)'

    cleaned_words = []

    for msg in temp['user_message']:
        # Remove URLs
        msg = re.sub(url_pattern, "", msg)

        # Lowercase + remove punctuation
        clean_msg = msg.lower().translate(translator)

        # Remove stopwords
        words = [w for w in clean_msg.split() if w not in stop_words]

        cleaned_words.extend(words)

    return cleaned_words


## Word cloud

def wc_stats(selected_user, df):

    cleaned_words = clean_messages(df, selected_user)

    final_text = " ".join(cleaned_words)

    wc = WordCloud(
        width=500,
        height=500,
        background_color="white",
        min_font_size=10
    ).generate(final_text)

    return wc

## most common word bar chart
def most_common_words(df, selected_user):

    cleaned_words = clean_messages(df, selected_user)

    result = pd.DataFrame(
        Counter(cleaned_words).most_common(20),
        columns=['word', 'count']
    )

    return result

## show emoji

def emojies(selected_user,df):
    if selected_user != "over all":
        df = df[df['user'] == selected_user]
    emojis = []

    for msg in df['user_message']:
        for ch in msg:
            if ch in emoji.EMOJI_DATA:
                emojis.append(ch)
    if len(emojis) == 0:
        return None, None
    emo = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))),columns=['emoji', 'count'])
    new_df = pd.DataFrame(Counter(emojis).most_common(10),columns=['emoji', 'count'])
    return emo,new_df


def p(selected_user,df):
    if selected_user != "over all":



