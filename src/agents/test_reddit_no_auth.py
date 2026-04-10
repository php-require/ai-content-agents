# test_reddit_no_auth.py

import requests


def fetch_posts():
    url = "https://www.reddit.com/r/gamedev/top.json"

    params = {
        "t": "day",
        "limit": 10
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    posts = data["data"]["children"]

    for i, item in enumerate(posts, 1):
        post = item["data"]

        print("=" * 80)
        print(f"{i}. {post['title']}")
        print(f"Score: {post['score']}")
        print(f"Comments: {post['num_comments']}")
        print(f"Link: https://reddit.com{post['permalink']}")
        print("=" * 80)


if __name__ == "__main__":
    fetch_posts()