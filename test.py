import requests
from bs4 import BeautifulSoup

def extract_instagram_info(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "Unable to fetch profile. Check the username or try again later."}

    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Extract follower, following, posts info from meta tag
        meta = soup.find("meta", property="og:description")
        summary = meta["content"]
        # Example: "476K Followers, 1 Following, 234 Posts - See Instagram photos and videos from Arsh Goyal (@arshgoyalyt)"

        counts = summary.split(" - ")[0].split(", ")
        followers = counts[0].split(" ")[0]
        following = counts[1].split(" ")[0]
        posts = counts[2].split(" ")[0]

        # Extract bio/description (in script tag)
        bio_tag = soup.find("meta", attrs={"name": "description"})
        bio = bio_tag["content"] if bio_tag else "N/A"

        return {
            "username": username,
            "followers": followers,
            "following": following,
            "posts": posts,
            "bio": bio,
            "summary": f"username: {username}, followers: {followers}, following: {following}, posts: {posts}, bio: {bio}"
        }

    except Exception as e:
        return {"error": f"Parsing failed: {str(e)}"}

# Example usage
if __name__ == "__main__":
    username = "dev.ankeshkumar"
    info = extract_instagram_info(username)
    for k, v in info.items():
        print(f"{k.capitalize()}: {v}")