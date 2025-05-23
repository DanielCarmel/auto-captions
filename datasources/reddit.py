import requests


def get_datasource_name():
    """
    Returns the name of the data source.
    """
    return "reddit"


def get_reddit_posts(subreddit="entitledparents", time_period="day", limit=20):
    """
    Fetch text posts from a subreddit.

    Args:
        subreddit (str): Subreddit name without 'r/'
        time_period (str): Time period to fetch posts from ('day', 'week', 'month', 'year', 'all')
        limit (int): Maximum number of posts to fetch

    Returns:
        list: List of dictionaries containing post data
    """
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t={time_period}&limit={limit}"

    # Set a proper user agent to avoid 429 Too Many Requests errors
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; RedditTextFetcher/1.0)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        posts = []

        # Extract relevant information from each post
        for post in data.get("data", {}).get("children", []):
            post_data = post.get("data", {})

            # Only include text posts (self posts)
            if post_data.get("is_self", False):
                posts.append({
                    "id": post_data.get("id"),
                    "title": post_data.get("title"),
                    "selftext": post_data.get("selftext"),
                    "author": post_data.get("author"),
                    "score": post_data.get("score"),
                    "url": post_data.get("url"),
                    "permalink": f"https://www.reddit.com{post_data.get('permalink')}"
                })

        return posts

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Reddit posts: {e}")
        return []


# Example usage
if __name__ == "__main__":
    # Get top posts from r/entitledparents for the day with a limit of 20
    posts = get_reddit_posts("entitledparents", "day", 20)
