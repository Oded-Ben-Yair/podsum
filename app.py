import streamlit as st
import requests
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="PodSum",
    page_icon="🎙️",
    layout="centered"
)

# Custom CSS for modern design
st.markdown("""
<style>
    /* Reset and base styles */
    .main {
        padding: 0 !important;
        max-width: 1000px;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        max-width: 800px;
    }

    /* Remove ALL dividers and lines */
    hr {display: none !important;}
    .css-18e3th9 {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .css-1d391kg, .css-12oz5g7 {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Header styles - simplified */
    .logo-text {
        font-size: 2.2rem;
        font-weight: 700;
        color: #333;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Input field styling */
    .stTextInput>div>div>input {
        padding: 0.75rem;
        font-size: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        background-color: #f9f9f9;
        box-shadow: none !important;
    }

    /* Button styling */
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: 600;
        padding: 0.75rem;
        border-radius: 8px;
        margin-top: 1rem;
        font-size: 1rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #E43B3B;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }

    /* Summary container styles */
    .summary-container {
        background-color: #ffffff;
        padding: 25px 30px;
        border-radius: 12px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Bullet point styles */
    li {
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    ul {
        padding-left: 20px;
        margin-top: 0;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Hide warning messages */
    .stAlert {display: none;}

    /* Download button styling */
    .stDownloadButton>button {
        background-color: #f0f0f0;
        color: #333;
        border: 1px solid #ddd;
        margin-top: 1rem;
    }
    .stDownloadButton>button:hover {
        background-color: #e0e0e0;
    }

    /* Professional language selector */
    .language-selector {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
        background: #f9f9f9;
        border-radius: 30px;
        padding: 4px;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Remove all default radio button styling */
    div.row-widget.stRadio > div {
        flex-direction: row;
        align-items: center;
        justify-content: center;
        background-color: transparent !important;
        border: none !important;
    }

    div.row-widget.stRadio > div > label {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    div.row-widget.stRadio > div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        background: #f5f5f5;
        border-radius: 30px;
        padding: 4px;
        width: fit-content;
        margin: 0 auto;
        border: 1px solid #e0e0e0;
    }

    div.row-widget.stRadio > div[role="radiogroup"] > label {
        padding: 8px 16px !important;
        margin: 0 4px !important;
        border-radius: 20px !important;
        transition: all 0.2s ease;
        font-size: 0.9rem;
        font-weight: 500;
    }

    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        display: none;
    }

    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
        background-color: #FF4B4B !important;
        color: white !important;
    }

    /* Remove any horizontal lines */
    .element-container:has(hr) {
        display: none !important;
    }

    /* Remove any extra padding */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Simple header - just text, no SVG or extra elements
st.markdown('<h1 class="logo-text">PodSum</h1>', unsafe_allow_html=True)

# Input field
url = st.text_input("", placeholder="Paste YouTube URL here...")

# Language selector - custom container for better styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    language = st.radio(
        "",
        options=["English", "Hebrew / עברית"],
        horizontal=True,
        label_visibility="collapsed"
    )

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube URL"""
    if "youtu.be" in youtube_url:
        return youtube_url.split("/")[-1].split("?")[0]
    elif "youtube.com/watch" in youtube_url:
        import urllib.parse as urlparse
        parsed_url = urlparse.urlparse(youtube_url)
        return urlparse.parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def get_video_info(video_id):
    """Get video title and description using public API"""
    try:
        api_url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            return {
                'title': data.get('title', 'Unknown Title'),
                'author': data.get('author_name', 'Unknown Author'),
                'thumbnail': data.get('thumbnail_url', None)
            }
        else:
            return None
    except Exception:
        return None

def generate_valuable_summary(video_id, title, author, language="English"):
    """Generate summary focused on valuable insights and knowledge in the specified language"""
    try:
        if language == "English":
            prompt = f"""
            Extract the most valuable insights and knowledge from this content:
            "{title}" by {author}

            Create a focused summary that:
            1. Highlights the 10-12 MOST VALUABLE insights, lessons, and actionable takeaways
            2. Emphasizes practical knowledge that can be applied immediately
            3. Includes the core ideas, frameworks, and mental models discussed
            4. Captures any surprising or counter-intuitive points
            5. Distills complex ideas into clear, concise explanations
            6. Prioritizes depth and value over chronological order

            Each bullet point should provide substantial value to someone who wants the knowledge without listening to the full podcast.
            Format as bullet points only in English.
            """
        else:  # Hebrew
            prompt = f"""
            חלץ את התובנות והידע הכי ערכיים מהתוכן הזה:
            "{title}" מאת {author}

            צור סיכום ממוקד ש:
            1. מדגיש 10-12 תובנות, לקחים ופעולות ערכיות ביותר
            2. מדגיש ידע מעשי שניתן ליישם באופן מיידי
            3. כולל את הרעיונות המרכזיים, מסגרות החשיבה ומודלים מנטליים שנדונו
            4. לוכד נקודות מפתיעות או אינטואיטיביות
            5. מזקק רעיונות מורכבים להסברים ברורים ותמציתיים
            6. מעדיף עומק וערך על פני סדר כרונולוגי

            כל נקודה צריכה לספק ערך משמעותי למישהו שרוצה את הידע מבלי להאזין לפודקאסט המלא.
            פרמט כנקודות בלבד בעברית, עם ניקוד מלא וכתיבה מימין לשמאל.
            """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract the most valuable knowledge from content in the requested language. Your summaries feel like high-quality notes on essential wisdom."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

# Simple UI - URL input, language selector, and button
if st.button("Summarize") and url:
    with st.spinner("Extracting valuable insights..."):
        # Extract video ID
        video_id = extract_video_id(url)

        if not video_id:
            st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
        else:
            # Get video info
            video_info = get_video_info(video_id)

            if not video_info:
                st.error("Could not retrieve video information. Please try again.")
            else:
                # Generate summary in selected language
                summary = generate_valuable_summary(
                    video_id,
                    video_info['title'],
                    video_info['author'],
                    language
                )

                if summary:
                    # Display thumbnail
                    if video_info['thumbnail']:
                        st.image(video_info['thumbnail'], use_column_width=True)

                    # Display summary in a clean container
                    st.markdown("<div class='summary-container'>", unsafe_allow_html=True)

                    # Set text direction for Hebrew
                    if language == "Hebrew / עברית":
                        st.markdown("<div dir='rtl'>", unsafe_allow_html=True)

                    st.markdown(summary)

                    if language == "Hebrew / עברית":
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Add download button for the summary
                    st.download_button(
                        label="Download Summary",
                        data=summary,
                        file_name="podcast_summary.txt",
                        mime="text/plain"
                    )