# streamlit_reddit_poster

**INSTALL**:
 
1. install a python environment (e.g. python -m venv venv && source venv/bin/activate)
2. Copy the 'example.env' to '.env'  and add all your own environment variables (found in reddit prefs page mostly)
3. pip install -r requirements.txt (to install required python packages
4. run api with 'uvicorn app:app --reload'
5. run streamlit with 'streamlit run app.py'

**HOW TO USE**: 

Create a '.txt' file with the subreddits you want to post to use. If it needs flairs you'll be able to select the one you want.
Select if you want a text or link category post.
Add your data you want to post to the fields provided and submit it. 

**PLEASE NOTE**: 
 
* This is a work in progress. 
* Subreddits have their own moderation rules so you WILL run into problems, learn the issue and send it to me and I'll do my best to find a workaround. 

**COMING SOON**: 

* Ability to select delay time between posts (helps prevent hitting any posting limits since reddit can delay for 12 minutes if you post too fast too often.
* A 'current user' profile that can be switched so you can post quickly as different accounts. 
