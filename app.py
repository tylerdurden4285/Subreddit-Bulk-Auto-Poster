import streamlit as st
import pandas as pd
from api import send_post, check_flairs

# log to app.log file in the same directory
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger(__name__)



st.title("Reddit Post Scheduler")

st.write("This app allows you to schedule posts on multiple subreddits at once. "
         "You can select the flair for each subreddit and schedule the post."
         "\n\n**IMPORTANT**: Your text file must be formatted like this example or it wont work:")

# show text file example

st.expander("Example", expanded=False).code("""
r/learnpython
r/programming
r/python
""")


st.divider()
uploaded_file = st.file_uploader("Choose your subreddit text file", type="txt", accept_multiple_files=False)
if uploaded_file is not None:
    st.divider()
    content = uploaded_file.getvalue().decode("utf-8")
    lines = content.split("\n")
    # Remove 'r/' prefix right when extracting subreddit names
    subreddits = [line.strip().removeprefix('r/') for line in lines if line.strip() and line.startswith('r/')]

    if subreddits:
        data = []
        for subreddit in subreddits:
            flairs = check_flairs(subreddit)
            if flairs and flairs['flairs']:
                st.subheader("Flair Selection")
                st.write(
                    "If the subreddit has flair choice requirements you'll be able to make your selection in the dropbox below. If not, then flair is not needed to post there and no action is needed from you.\n\n")

                flair_options = {flair['flair_text']: flair['flair_id'] for flair in flairs['flairs']}
                select_key = f"Select flair for {subreddit}"
                selected_flair = st.selectbox(f"Select flair for {subreddit}:", list(flair_options.keys()), key=select_key)
                data.append([subreddit, f"{selected_flair}"])
            else:
                data.append([subreddit, "None"])

        df = pd.DataFrame(data, columns=['Subreddit', 'Flair'])
        df.index = df.index + 1
        st.subheader("Subreddits")
        st.write("The following subreddits and their flairs have been loaded:")
        st.table(df)

        st.divider()
        st.subheader("Post Details")
        title = st.text_input("Title")
        body = st.text_area("Body")

        if st.button("Submit"):
            success_count = 0
            errors = []
            for i, row in df.iterrows():
                # Check if flair information is present and split properly
                if ':' in row['Flair']:
                    flair_id = row['Flair'].split(': ')[-1]
                else:
                    flair_id = None  # No flair needed or available

                # Try to send the post
                result = send_post(title, body, flair_id, row['Subreddit'])
                if result:
                    if 'post_url' in result:
                        post_url = result.get('post_url', '#')
                        st.markdown(f"**Post sent for subreddit:** [{row['Subreddit']}]({post_url})")
                        success_count += 1
                    else:
                        errors.append(f"Failed to send post for {row['Subreddit']}: {result.get('message', 'Unknown error')}")
                else:
                    errors.append(f"Failed to send post: No response received for {row['Subreddit']}.")

            if errors:
                for error in errors:
                    st.error(error)
            st.success(f"Job finished. Total successful posts: {success_count}.")

