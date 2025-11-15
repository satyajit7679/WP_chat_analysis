import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from preprocess import preprocess
import helper
import plotly.express as px

st.sidebar.title("WP Chat Analyser")
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp .txt file", type=["txt"])

df = None
if uploaded_file is not None:
    data = uploaded_file.read().decode("utf-8", errors="ignore")
    df = preprocess(data)
    st.dataframe(df)

if df is not None:
    user_list = df['user'].unique().tolist()

    # Remove unwanted users if present
    for u in ['group_notification', 'Meta AI']:
        if u in user_list:
            user_list.remove(u)

    user_list.sort()
    user_list.insert(0, 'over all')

    selected_user = st.sidebar.selectbox("Show analysis for:", user_list)

    if st.sidebar.button("Analyze"):
        num_message, words, media, links = helper.fetch_stats(selected_user, df)
        st.title("Total sharing information")
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




