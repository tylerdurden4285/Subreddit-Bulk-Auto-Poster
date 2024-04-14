import logging
import os
import traceback
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Security, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import praw
from logger import setup_custom_logger

# Get a custom logger for your application
logger = setup_custom_logger(__name__)
logger.propagate = False

# Use the logger
logger.info("PRAW FastAPI Application started")
print("PRAW FastAPI Application started")

# Load environment variables
load_dotenv()

# Bearer Token
bearer_scheme = HTTPBearer()

# Create FastAPI instance
app = FastAPI(title=os.getenv('REDDIT_USERNAME') + "'s Reddit API Poster", description="A simple API to post to Reddit", version="0.1.2")


# Create Reddit instance using environment variables securely
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    username=os.getenv('REDDIT_USERNAME'),
    password=os.getenv('REDDIT_PASSWORD')
)


####################
# Helper Functions #
####################

def token_required(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if credentials:
        try:
            # Insert token validation logic here
            pass
        except Exception as e:
            logging.error("Token validation error: {}".format(e))
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token credentials")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credentials are missing")


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    base_error = {"error": str(exc)}
    logging.error(f"Unhandled exception: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content=base_error
    )


####################
# Reddit Endpoints #
####################

# home page
@app.get("/")
def home():
    return {"message": "Reddit API Poster is running!",
            "version": "0.1.2",
            "status": "running",
            "status_code": 200}


# Auth check
@app.get("/secure-ping")
def auth_check(credentials: HTTPAuthorizationCredentials = Depends(token_required)):
    # Logic to handle the secure request
    return {"message": "You Are Secure!",
            "status_code": 200}


# Get the specific subreddit available flairs by flair name and flair_id
@app.get("/subreddit-flairs/{subreddit_name}")
def get_subreddit_flairs(subreddit_name: str):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        flairs = subreddit.flair.link_templates
        flairs_list = [{"flair_text": flair['text'], "flair_id": flair['id']} for flair in flairs]
        return {"flairs": flairs_list}
    except Exception as e:
        logging.error("Error getting subreddit flairs: {}".format(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting subreddit flairs")


# Post to a specific subreddit with a title, body and optional flair_id
class PostRequest(BaseModel):
    title: str
    body: Optional[str] = None
    url: Optional[str] = None
    flair_id: Optional[str] = None


# Post to a specific subreddit
@app.post("/post/{subreddit_name}")
def post_to_subreddit(subreddit_name: str, post_request: PostRequest,
                      credentials: HTTPAuthorizationCredentials = Depends(token_required)):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        # Validation for post type
        if post_request.body and post_request.url:
            raise HTTPException(status_code=400, detail="Submit either a text post or a link post, not both.")
        elif post_request.url:
            submission = subreddit.submit(title=post_request.title, url=post_request.url,
                                          flair_id=post_request.flair_id)
        elif post_request.body:
            submission = subreddit.submit(title=post_request.title, selftext=post_request.body,
                                          flair_id=post_request.flair_id)
        else:
            raise HTTPException(status_code=400, detail="A body or URL must be provided for the post.")

        # Get the full post URL
        full_post_url = f"https://www.reddit.com{submission.permalink}"
        return {"message": "Post submitted successfully",
                "post_id": submission.id,
                "post_url": full_post_url}

    except Exception as e:
        logging.error("Error posting to subreddit: {}".format(e))
        raise HTTPException(status_code=400, detail=f"Error posting to subreddit: {e}")

# Post comment to a specific post
# class CommentRequest(BaseModel):
#     comment: str


# Takes a variable input called "comment" and posts it to the specific existing reddit post by it's post_id
# @app.post("/post/comment/{post_id}")
# def post_comment_to_post(post_id: str, comment_request: CommentRequest,
#                          credentials: HTTPAuthorizationCredentials = Depends(token_required)):
#     try:
#         submission = reddit.submission(id=post_id)
#         submission.reply(comment_request.comment)
#         return {"message": "Comment submitted successfully",
#                 "post_id": post_id,
#                 "post_url": submission.url}  # Add this line
#     except Exception as e:
#         logging.error("Error posting comment to post: {}".format(e))
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error posting comment to post")
# # Run with uvicorn hint: uvicorn app:app --reload
