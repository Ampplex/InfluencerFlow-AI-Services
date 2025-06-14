from google_play_scraper import reviews

# Replace with your app's package name
APP_ID = "com.kofluence"

# Fetch the latest 200 reviews
result, _ = reviews(
    APP_ID,
    lang='en',
    country='us',
    count=200
)

# Filter and print only 1-star review content
one_star_reviews = [r["content"] for r in result if r["score"] == 1]

print(f"\n🟠 Total 1-star reviews: {len(one_star_reviews)}\n")
for i, content in enumerate(one_star_reviews, 1):
    print(f"[{i}] {content}\n")