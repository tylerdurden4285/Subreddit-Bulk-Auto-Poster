import streamlit as st
import pandas as pd
from connector import send_post, check_flairs
from logger import setup_custom_logger

# Setup logger
logger = setup_custom_logger(__name__)
logger.propagate = False

# Streamlit UI setup
st.title("Reddit Post Scheduler")
st.write("""
This app allows you to schedule posts on multiple subreddits at once. 
You can select the flair for each subreddit and schedule the post.
**IMPORTANT**: Your text file must be formatted like this example or it won't work:
""")

st.expander("Example", expanded=False).code("r/learnpython\nr/programming\nr/python")

uploaded_file = st.file_uploader("Choose your subreddit text file", type="txt", accept_multiple_files=False)
if uploaded_file:
    content = uploaded_file.getvalue().decode("utf-8")
    lines = content.split("\n")
    subreddits = [line.strip().removeprefix('r/') for line in lines if line.strip() and line.startswith('r/')]

    if subreddits:
        data = []
        for subreddit in subreddits:
            flairs = check_flairs(subreddit)
            if flairs and flairs['flairs']:
                flair_options = {flair['flair_text']: flair['flair_id'] for flair in flairs['flairs']}
                selected_flair_text = st.selectbox(f"Select flair for {subreddit}:", list(flair_options.keys()))
                selected_flair_id = flair_options[selected_flair_text]
                data.append([subreddit, selected_flair_text, selected_flair_id])
            else:
                # Append None or a similar indicator that no flair is available/required
                data.append([subreddit, "No Flair", None])

        df = pd.DataFrame(data, columns=['Subreddit', 'Flair Name', 'Flair ID'])
        st.table(df)

        title = st.text_input("Title")
        body = st.text_area("Body")

        if st.button("Schedule Post"):
            success_count = 0  # Initialize success counter
            for index, row in df.iterrows():
                response = send_post(title, body, row['Flair ID'], row['Subreddit'])
                if response:
                    st.success(f"Post scheduled successfully on {row['Subreddit']}")
                    success_count += 1  # Increment the success counter
                else:
                    st.error(f"Failed to schedule post on {row['Subreddit']}")

            st.info(f"Finished. Posted to {success_count} subreddits.")
            st.balloons()
    else:
        st.error("No subreddits found in the file. Please make sure the file is formatted correctly.")
else:
    st.info("Please upload a text file to start scheduling posts.")