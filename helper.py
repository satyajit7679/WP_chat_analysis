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

# timeline graph
def monthly_timeline(df, selected_user):
    if selected_user != "over all":
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month', 'month_name']).count()['user_message']
    timeline = timeline.to_frame(name="message").reset_index()

    # your loop
    time = []
    for i in range(timeline.shape[0]):
        time.append(f"{timeline['month_name'][i]}-{timeline['year'][i]}")
    timeline['time'] = time

    # real date for sorting
    timeline['date'] = pd.to_datetime(
        timeline['year'].astype(str) + "-" + timeline['month'].astype(str) + "-01"
    )

    timeline = timeline.sort_values("date")
    return timeline
def daily_timeline(df, selected_user):
    if selected_user != "over all":
        df = df[df['user'] == selected_user]

    daily = df.groupby('date').count()['user_message'].reset_index()
    daily = daily.rename(columns={"user_message": "message"})
    return daily
def week_activity_map(df, selected_user):
    if selected_user != "over all":
        df= df[df['user'] == selected_user]
    return df['day_name'].value_counts()

def month_activity_map(df, selected_user):
    if selected_user != "over all":
        df= df[df['user'] == selected_user]
    return df['month_name'].value_counts()

def show_heatmap(df, selected_user):
    if selected_user != "over all":
        df = df[df['user'] == selected_user]
    df = df.copy()
    periods = []
    sort_keys = []
    for hour in df['hour']:
        if hour == 23:
            periods.append(f"{hour}-00")
            sort_keys.append(hour)      # 23
        elif hour == 0:
            periods.append(f"00-{hour+1}")
            sort_keys.append(hour)      # 0
        else:
            periods.append(f"{hour}-{hour+1}")
            sort_keys.append(hour)      # 1-22

    df['period'] = periods
    df['period_sort'] = sort_keys      # store sort index
    return df


## Question vs Statement Ratio Analysis
def question_vs_statement(df, selected_user):
    """
    Analyze questions vs statements in messages
    Returns: question_count, statement_count, question_percentage
    """
    if selected_user != "over all":
        df = df[df['user'] == selected_user]

    # Remove media and group notifications
    temp = df[df['user_message'] != 'group_notification']
    temp = temp[~temp['user_message'].isin([
        '<Media omitted>', '<media omitted>', 'Media omitted', 'media omitted'
    ])]

    questions = 0
    statements = 0

    for msg in temp['user_message']:
        msg = str(msg).strip()
        if msg.endswith('?'):
            questions += 1
        else:
            statements += 1

    total = questions + statements
    question_percentage = round((questions / total * 100), 2) if total > 0 else 0
    statement_percentage = round((statements / total * 100), 2) if total > 0 else 0

    return questions, statements, question_percentage, statement_percentage


## User-wise Question vs Statement Analysis (for comparison)
def user_question_statement_analysis(df):
    """
    Analyze question vs statement ratio for all users
    Returns: DataFrame with user-wise breakdown
    """
    # Remove unwanted users
    df = df[~df['user'].isin(['group_notification', 'Meta AI'])]

    # Remove media messages
    df = df[~df['user_message'].isin([
        '<Media omitted>', '<media omitted>', 'Media omitted', 'media omitted'
    ])]

    user_data = []

    for user in df['user'].unique():
        user_df = df[df['user'] == user]

        questions = 0
        statements = 0

        for msg in user_df['user_message']:
            msg = str(msg).strip()
            if msg.endswith('?'):
                questions += 1
            else:
                statements += 1

        total = questions + statements
        question_percentage = round((questions / total * 100), 2) if total > 0 else 0

        user_data.append({
            'user': user,
            'questions': questions,
            'statements': statements,
            'total_messages': total,
            'question_percentage': question_percentage
        })

    result_df = pd.DataFrame(user_data)
    result_df = result_df.sort_values('question_percentage', ascending=False)

    return result_df




