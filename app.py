import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from preprocess import preprocess
import helper
import plotly.express as px
import seaborn as sns




st.sidebar.title("WP Chat Analyser")
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp .txt file", type=["txt"])

df = None
if uploaded_file is not None:
    data = uploaded_file.read().decode("utf-8", errors="ignore")
    df = preprocess(data)


if df is not None:
    user_list = df['user'].unique().tolist()
    st.dataframe(df)
    # Remove unwanted users if present
    for u in ['group_notification', 'Meta AI']:
        if u in user_list:
            user_list.remove(u)

    user_list.sort()
    user_list.insert(0, 'over all')

    selected_user = st.sidebar.selectbox("Show analysis for:", user_list)

    if st.sidebar.button("Analyze"):
        num_message, words, media, links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        #Total masseges
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_message)

        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Total Media")
            st.title(media)
        with col4:
            st.header("Total Links")
            st.title(links)

        #Show time line graph
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(df, selected_user)
        fig, ax = plt.subplots()
        ax.plot(timeline['date'], timeline['message'],marker='o')  # using date, not label
        plt.xticks(rotation='vertical')
        plt.xlabel("Date")
        plt.ylabel("No of Messages")
        st.pyplot(fig)

        #Show daily time line graph
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(df, selected_user)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['date'], daily_timeline['message'],color='black', marker='o')
        plt.xticks(rotation='vertical')
        plt.xlabel("Date")
        plt.ylabel("No of Messages")
        st.pyplot(fig)

        ## Most activity in a week
        st.title("Activity map")
        col1,col2 = st.columns(2)
        with col1:
            st.header("Most active day")
            busy_day = helper.week_activity_map(df,selected_user)
            colors = [
                "teal", "olive", "navy", "maroon", "lime",
                "orange", "purple", "green", "red", "blue",
                "cyan", "magenta", "yellow", "brown", "pink",
                "gold", "skyblue", "coral", "darkgreen", "violet"
            ]

            fig, ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color=colors)
            ax.set_xlabel("days name")
            ax.set_ylabel("number of messages")
            st.pyplot(fig)
        with col2:
            st.header("Most active month")
            busy_month = helper.month_activity_map(df, selected_user)
            colors = [
                "gold", "skyblue", "coral", "darkgreen", "violet",
                "teal", "olive", "navy", "maroon", "lime",
                "orange", "purple", "green", "red", "blue",
                "cyan", "magenta", "yellow", "brown", "pink"
            ]

            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color=colors)
            ax.set_xticklabels(busy_month.index, rotation=90)
            ax.set_xlabel("month name")
            ax.set_ylabel("number of messages")
            st.pyplot(fig)

        ## show heatmap
        st.title("Show heatmap")
        # Get processed DF
        period_df = helper.show_heatmap(df, selected_user)
        # Create pivot table from processed DF (period_df, not df)
        pivot_df = period_df.pivot_table(
            index='day_name',
            columns='period',
            values='user_message',
            aggfunc='count'
        ).fillna(0)
        plt.figure(figsize=(20, 6))
        sns.heatmap(pivot_df, annot=True, fmt='.0f')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.xlabel("Period")
        plt.ylabel("Day Name")
        plt.title("Heatmap of Messages by Day and Period")
        st.pyplot(plt)

        #Most busy person in Group
        if selected_user == "over all":
            st.title("Most busy user")

            fig, x, new_df = helper.show_top_user(df)

            col1, col2 = st.columns(2)

            with col1:
                st.header("Most busy user Bar chart")
                st.pyplot(fig)

            with col2:
                st.header("Percentage of messsages")
                st.dataframe(new_df)

        ##wordclound image


    #Most common word


        st_words = helper.most_common_words(df, selected_user)
        col1, col2 = st.columns(2)
        with col1:
            st.title("WordCloud")
            wc_img = helper.wc_stats(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(wc_img)
            plt.imshow(wc_img)
            st.pyplot(fig)
        with col2:
            st.title("Most Common Words")
            st.dataframe(st_words)
        #Most Common Word bar chart
        st.title('Most Common Words Bar Chart')
        n = len(st_words)
        # Generate rainbow colors
        colors = plt.cm.rainbow(np.linspace(0, 1, n))

        fig, ax = plt.subplots()

        ax.barh(
            st_words['word'],
            st_words['count'],
            color=colors  # ← rainbow colors here
        )

        ax.invert_yaxis()  # Most common word on top
        ax.set_xlabel("Frequency")
        ax.set_ylabel("Words")
        plt.tight_layout()

        st.pyplot(fig)


        ## Show emoji
        st.title("Emoji Summary")
        emojis, new_df = helper.emojies(selected_user, df)
        if emojis is None:
            st.warning("No emojis used by this user!")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.header('Show used Emojis')
                st.dataframe(emojis)

            with col2:
                st.header('Top 10 Emoji Usage')

                # Plotly pie chart with colored emojis
                fig = px.pie(
                    new_df,
                    values=new_df['count'],
                    names=new_df['emoji'],
                    title="Top 10 Used Emojis",
                )

                st.plotly_chart(fig, use_container_width=True)




