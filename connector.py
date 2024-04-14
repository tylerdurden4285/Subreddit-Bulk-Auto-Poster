import requests
import os
import logging

BEARER_TOKEN = os.getenv('BEARER_TOKEN')


# log to app.log file in the same directory
logging.basicConfig(filename='api.log', level=logging.INFO)
logger = logging.getLogger(__name__)


# function to send a post to the fastapi endpoint
def send_post(title, body, flair_id, subreddit):

    url = f"http://localhost:8000/post/{subreddit}"
    payload = {"title": title, "body": body, "flair_id": flair_id}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BEARER_TOKEN}"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises a HTTPError for 4xx, 5xx errors
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {url} failed: {e}")
        return None

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None


def check_flairs(subreddit):
    url = f"http://localhost:8000/subreddit-flairs/{subreddit}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BEARER_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError for 4xx, 5xx errors
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {url} failed: {e}")
        return None

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
