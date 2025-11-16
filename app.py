
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from preprocess import preprocess
import helper
import plotly.express as px
import seaborn as sns
from datetime import datetime
import io
import base64

# Page config
st.set_page_config(page_title="WhatsApp Analyzer", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

# Custom CSS for animations and styling
st.markdown("""
<style>
    /* Smooth animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    /* Animated elements */
    .main .block-container {
        animation: fadeIn 0.6s ease-out;
    }

    .stButton>button {
        transition: all 0.3s ease;
        border-radius: 10px;
        font-weight: 600;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white !important;
        animation: fadeIn 0.8s ease-out;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .stMetric label {
        color: white !important;
        font-weight: 600 !important;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    h1 {
        animation: slideIn 0.5s ease-out;
    }

    h2, h3 {
        animation: fadeIn 0.7s ease-out;
    }

    .stDownloadButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        animation: pulse 2s infinite;
    }

    .stDownloadButton>button:hover {
        animation: none;
        transform: scale(1.05);
    }

    /* Dataframe styling */
    .dataframe {
        animation: fadeIn 1s ease-out;
        border-radius: 10px;
        overflow: hidden;
    }

    /* Card effect for sections */
    .element-container {
        animation: fadeIn 0.8s ease-out;
    }

    /* Progress animation */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    .css-1d391kg .stMarkdown, [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }

    /* Metric styling for both themes */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }

    /* Chart container animation */
    .js-plotly-plot {
        animation: fadeIn 1s ease-out;
    }

    /* Custom title styling */
    .custom-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        animation: slideIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Apply dark theme permanently
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #fafafa !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d29 0%, #2d1b3d 100%) !important;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #fafafa !important;
    }
</style>
""", unsafe_allow_html=True)
plt.style.use('dark_background')

# Sidebar with custom title color
st.sidebar.markdown("""
<h1 style='text-align: center; 
           background: linear-gradient(90deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%);
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
           font-size: 2rem;
           font-weight: 800;
           padding: 10px 0;'>
    🔍 WP Chat Analyser
</h1>
""", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("📁 Choose a WhatsApp .txt file", type=["txt"])

df = None
if uploaded_file is not None:
    with st.spinner('🔄 Processing your chat...'):
        data = uploaded_file.read().decode("utf-8", errors="ignore")
        df = preprocess(data)
    st.sidebar.success("✅ File loaded successfully!")

if df is not None:
    user_list = df['user'].unique().tolist()

    # Remove unwanted users
    for u in ['group_notification', 'Meta AI']:
        if u in user_list:
            user_list.remove(u)

    user_list.sort()
    user_list.insert(0, 'over all')

    # Date Range Selector
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Date Range Filter")
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_range"
    )

    # Filter dataframe by date range
    if len(date_range) == 2:
        df = df[(df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])]

    # User Selection
    st.sidebar.markdown("---")
    selected_user = st.sidebar.selectbox("👤 Show analysis for:", user_list, key="user_select")

    # Comparison Mode
    st.sidebar.markdown("---")
    compare_mode = st.sidebar.checkbox("🔄 Compare Users", key="compare_check")
    compare_user = None

    if compare_mode:
        compare_users = [u for u in user_list if u != selected_user and u != 'over all']
        if compare_users:
            compare_user = st.sidebar.selectbox("Compare with:", compare_users, key="compare_select")

    # Show raw data
    with st.expander("📊 View Raw Data"):
        st.dataframe(df, use_container_width=True)

    # Analyze button
    if st.sidebar.button("🚀 Analyze", type="primary", key="analyze_btn"):
        st.session_state.analyzed = True

    if st.session_state.analyzed:

        # Function to download figure without rerun
        def get_image_download_link(fig, filename):
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='#0e1117')
            buf.seek(0)
            return buf.getvalue()


        # Progress bar
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
        progress_bar.empty()

        # Get stats
        num_message, words, media, links = helper.fetch_stats(selected_user, df)

        # Comparison stats
        if compare_mode and compare_user:
            num_message2, words2, media2, links2 = helper.fetch_stats(compare_user, df)

        # Title with animation
        st.markdown('<h1 class="custom-title">📊 Chat Analysis Dashboard</h1>', unsafe_allow_html=True)

        st.markdown("---")

        # Statistics Display
        st.subheader("📈 Top Statistics")

        if compare_mode and compare_user:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💬 Messages", num_message, f"{selected_user}")
                st.metric("", num_message2, delta=num_message2 - num_message, delta_color="normal", help=compare_user)
            with col2:
                st.metric("📝 Words", words, f"{selected_user}")
                st.metric("", words2, delta=words2 - words, delta_color="normal", help=compare_user)
            with col3:
                st.metric("🖼️ Media", media, f"{selected_user}")
                st.metric("", media2, delta=media2 - media, delta_color="normal", help=compare_user)
            with col4:
                st.metric("🔗 Links", links, f"{selected_user}")
                st.metric("", links2, delta=links2 - links, delta_color="normal", help=compare_user)
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💬 Total Messages", num_message)
            with col2:
                st.metric("📝 Total Words", words)
            with col3:
                st.metric("🖼️ Total Media", media)
            with col4:
                st.metric("🔗 Total Links", links)

        # Download Summary
        st.markdown("---")
        summary_text = f"""WhatsApp Chat Analysis Summary
{'=' * 60}
User: {selected_user}
Date Range: {date_range[0] if len(date_range) == 2 else min_date} to {date_range[1] if len(date_range) == 2 else max_date}

📊 STATISTICS
{'─' * 60}
Total Messages: {num_message}
Total Words: {words}
Total Media: {media}
Total Links: {links}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        st.download_button(
            label="📥 Download Summary Report",
            data=summary_text,
            file_name=f"summary_{selected_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            key="summary_download"
        )

        # Monthly Timeline
        st.markdown("---")
        st.subheader("📅 Monthly Timeline")
        timeline = helper.monthly_timeline(df, selected_user)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(timeline['date'], timeline['message'], marker='o', linewidth=2.5,
                markersize=8, label=selected_user, color='#667eea')

        if compare_mode and compare_user:
            timeline2 = helper.monthly_timeline(df, compare_user)
            ax.plot(timeline2['date'], timeline2['message'], marker='s', linewidth=2.5,
                    markersize=8, label=compare_user, color='#764ba2')
            ax.legend(fontsize=12, frameon=True, shadow=True)

        ax.grid(True, alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Date", fontsize=12, fontweight='bold')
        plt.ylabel("No of Messages", fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

        st.download_button(
            "💾 Download Chart",
            get_image_download_link(fig, "monthly_timeline.png"),
            f"monthly_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "image/png",
            key="monthly_download"
        )

        # Daily Timeline
        st.markdown("---")
        st.subheader("📆 Daily Timeline")
        daily_timeline = helper.daily_timeline(df, selected_user)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(daily_timeline['date'], daily_timeline['message'],
                color='#667eea', marker='o', linewidth=2, markersize=6, label=selected_user)

        if compare_mode and compare_user:
            daily_timeline2 = helper.daily_timeline(df, compare_user)
            ax.plot(daily_timeline2['date'], daily_timeline2['message'],
                    color='#764ba2', marker='s', linewidth=2, markersize=6, label=compare_user)
            ax.legend(fontsize=12, frameon=True, shadow=True)

        ax.grid(True, alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Date", fontsize=12, fontweight='bold')
        plt.ylabel("No of Messages", fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

        st.download_button(
            "💾 Download Chart",
            get_image_download_link(fig, "daily_timeline.png"),
            f"daily_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "image/png",
            key="daily_download"
        )

        # Activity Map
        st.markdown("---")
        st.subheader("⚡ Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Most Active Day")
            busy_day = helper.week_activity_map(df, selected_user)
            colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140']

            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(busy_day.index, busy_day.values, color=colors[:len(busy_day)])
            ax.set_xlabel("Day Name", fontsize=12, fontweight='bold')
            ax.set_ylabel("Number of Messages", fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

            st.download_button(
                "💾 Download",
                get_image_download_link(fig, "active_day.png"),
                f"active_day_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "image/png",
                key="day_download"
            )

        with col2:
            st.markdown("### 📅 Most Active Month")
            busy_month = helper.month_activity_map(df, selected_user)
            colors = ['#fa709a', '#fee140', '#30cfd0', '#667eea', '#f093fb', '#4facfe']

            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(busy_month.index, busy_month.values, color=colors[:len(busy_month)])
            ax.set_xticklabels(busy_month.index, rotation=45, ha='right')
            ax.set_xlabel("Month Name", fontsize=12, fontweight='bold')
            ax.set_ylabel("Number of Messages", fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            st.pyplot(fig)

            st.download_button(
                "💾 Download",
                get_image_download_link(fig, "active_month.png"),
                f"active_month_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "image/png",
                key="month_download"
            )

        # Heatmap
        st.markdown("---")
        st.subheader("🔥 Activity Heatmap")
        period_df = helper.show_heatmap(df, selected_user)
        pivot_df = period_df.pivot_table(
            index='day_name',
            columns='period',
            values='user_message',
            aggfunc='count'
        ).fillna(0)
        pivot_df = pivot_df.reindex(sorted(pivot_df.columns, key=lambda x: int(x.split("-")[0])), axis=1)

        fig = plt.figure(figsize=(20, 7))

        sns.heatmap(pivot_df, annot=True, fmt='.0f', cmap='RdYlGn', linewidths=0.5,
                    cbar_kws={'label': 'Message Count'})
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.xlabel("Time Period", fontsize=12, fontweight='bold')
        plt.ylabel("Day Name", fontsize=12, fontweight='bold')
        plt.title("Heatmap of Messages by Day and Period", fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        st.pyplot(fig)

        st.download_button(
            "💾 Download Heatmap",
            get_image_download_link(fig, "heatmap.png"),
            f"heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "image/png",
            key="heatmap_download"
        )

        # Most busy person
        if selected_user == "over all":
            st.markdown("---")
            st.subheader("👥 Most Busy Users")
            fig, x, new_df = helper.show_top_user(df)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📊 Top 5 Active Users")
                st.pyplot(fig)
                st.download_button(
                    "💾 Download",
                    get_image_download_link(fig, "busy_users.png"),
                    f"busy_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    "image/png",
                    key="users_download"
                )
            with col2:
                st.markdown("### 📈 Message Distribution")
                st.dataframe(new_df, use_container_width=True)

        # WordCloud and Common Words
        st.markdown("---")
        st.subheader("💬 Word Analysis")
        st_words = helper.most_common_words(df, selected_user)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ☁️ WordCloud")
            wc_img = helper.wc_stats(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.imshow(wc_img, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout()
            st.pyplot(fig)

            st.download_button(
                "💾 Download",
                get_image_download_link(fig, "wordcloud.png"),
                f"wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "image/png",
                key="wc_download"
            )

        with col2:
            st.markdown("### 📝 Top 20 Words")
            st.dataframe(st_words, use_container_width=True, height=400)

        # Common Words Bar Chart
        st.markdown("---")
        st.subheader("📊 Most Common Words Chart")
        n = len(st_words)
        colors = plt.cm.viridis(np.linspace(0, 1, n))

        fig, ax = plt.subplots(figsize=(12, 10))
        bars = ax.barh(st_words['word'], st_words['count'], color=colors)
        ax.invert_yaxis()
        ax.set_xlabel("Frequency", fontsize=12, fontweight='bold')
        ax.set_ylabel("Words", fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        plt.tight_layout()
        st.pyplot(fig)

        st.download_button(
            "💾 Download Chart",
            get_image_download_link(fig, "common_words.png"),
            f"common_words_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "image/png",
            key="words_download"
        )

        # Emoji Analysis
        st.markdown("---")
        st.subheader("😊 Emoji Summary")
        emojis, new_df = helper.emojies(selected_user, df)

        if emojis is None:
            st.warning("⚠️ No emojis used by this user!")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📋 All Emojis Used")
                st.dataframe(emojis, use_container_width=True, height=400)
            with col2:
                st.markdown("### 🏆 Top 10 Emoji Usage")
                fig = px.pie(
                    new_df,
                    values='count',
                    names='emoji',
                    title="Top 10 Used Emojis",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
                fig.update_layout(showlegend=True, height=500)
                st.plotly_chart(fig, use_container_width=True)


        # Question vs Statement Analysis
        st.markdown("---")
        st.subheader("❓ Question vs Statement Analysis")

        questions, statements, q_percent, s_percent = helper.question_vs_statement(df, selected_user)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Overall Ratio")

            # Create metrics
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("❓ Questions", questions, f"{q_percent}%")
            with metric_col2:
                st.metric("💬 Statements", statements, f"{s_percent}%")

            # Pie chart for selected user
            fig = px.pie(
                values=[questions, statements],
                names=['Questions', 'Statements'],
                title=f"{selected_user}'s Communication Style",
                hole=0.4,
                color_discrete_sequence=['#667eea', '#764ba2']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
            fig.update_layout(showlegend=True, height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 👥 User Comparison")

            if selected_user == "over all":
                # Show all users comparison
                user_qs_df = helper.user_question_statement_analysis(df)
                st.dataframe(user_qs_df, use_container_width=True, height=400)

                # Bar chart
                fig = px.bar(
                    user_qs_df.head(10),
                    x='user',
                    y='question_percentage',
                    title='Top 10 Users by Question Percentage',
                    labels={'question_percentage': 'Question %', 'user': 'User'},
                    color='question_percentage',
                    color_continuous_scale='viridis',
                    text='question_percentage'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(
                    xaxis_tickangle=-45,
                    height=400,
                    xaxis={'type': 'category'},
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Show top 10 users for comparison
                user_qs_df = helper.user_question_statement_analysis(df)
                st.dataframe(user_qs_df.head(10), use_container_width=True, height=400)

                st.info(f"💡 **Insight:** {selected_user} asks questions {q_percent}% of the time. " +
                        ("This user is very inquisitive! 🤔" if q_percent > 30 else
                         "This user makes more statements. 💭" if q_percent < 15 else
                         "Balanced communication style. ⚖️"))

    else:
        # Welcome screen with animation
        st.markdown("""
            <div style="text-align: center; padding: 50px;">
                <h1 style="font-size: 4rem; animation: pulse 2s infinite;">📱</h1>
                <h1 style="font-size: 3rem; 
                           font-weight: 800;
                           background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                           -webkit-background-clip: text;
                           -webkit-text-fill-color: transparent;
                           text-align: center;
                           margin-bottom: 2rem;
                           animation: slideIn 0.5s ease-out;">
                    WhatsApp Chat Analyzer
                </h1>
                <p style="font-size: 1.2rem; color: #667eea;">Upload your WhatsApp chat export to get started!</p>
                <p style="margin-top: 30px; color: #fafafa;">📊 Analyze messages • 📈 Track activity • 😊 View emoji stats</p>
            </div>
            """, unsafe_allow_html=True)

