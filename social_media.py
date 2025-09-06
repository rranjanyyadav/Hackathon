
import spacy
from geopy.geocoders import Nominatim
import time
import tweepy
from textblob import TextBlob

# === CONFIGURATION ===
# IMPORTANT: Replace "YOUR_BEARER_TOKEN" with your actual Twitter API Bearer Token.
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAOnS3wEAAAAAAYVNy0cKH%2FdLmyZIfNFs76Y%2BPmI%3Dd7TFqbMScFTpvyrg7oxvDQ0VrFgtuKhyweointfslpbAGifWnq"

# Load spaCy English model for Named Entity Recognition
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Initialize geolocator with a custom user_agent
geolocator = Nominatim(user_agent="ocean_hazard_app")

def is_location_in_india(location_name):
    """
    Checks if a given location name is in India using geopy.
    Returns True if the location is in India, else False.
    """
    try:
        # Use a timeout to prevent the script from hanging on a slow request.
        location = geolocator.geocode(location_name, exactly_one=True, timeout=10)
        if location and 'India' in location.address:
            return True
        return False
    except Exception as e:
        print(f"Geocoding error for '{location_name}': {e}")
        return False

def extract_location_from_text(text):
    """
    Extracts location entities (GPE or LOC) from text using spaCy NER.
    Returns the first location entity found or None.
    """
    doc = nlp(text)
    for ent in doc.ents:
        # GPE = Geopolitical Entity (e.g., countries, cities, states)
        # LOC = Location (e.g., mountains, bodies of water)
        if ent.label_ in ("GPE", "LOC"):
            return ent.text
    return None

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text using TextBlob.
    Returns 'Positive', 'Negative', or 'Neutral'.
    """
    analysis = TextBlob(text)
    # Classify the polarity of the sentiment
    if analysis.sentiment.polarity > 0.1:
        return 'Positive'
    elif analysis.sentiment.polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

def search_tweets_by_keywords_india(keywords, max_results=50):
    """
    Searches recent tweets containing the provided keywords, filters to those
    located in India, and analyzes their sentiment.
    
    Returns a list of dictionaries, each containing the tweet text and sentiment.
    """
    # Create the Tweepy client
    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    except Exception as e:
        print(f"Error creating Tweepy client: {e}")
        print("Please ensure your TWITTER_BEARER_TOKEN is valid.")
        return []

    # Construct the search query
    query = " OR ".join(keywords) + " -is:retweet lang:en"
    
    try:
        # Request geo info and place fields for filtering
        tweets_response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            expansions=['geo.place_id'],
            place_fields=['country', 'country_code', 'full_name', 'name', 'place_type'],
            tweet_fields=['geo', 'text']
        )
        
        if not tweets_response.data:
            print("No tweets found for the given keywords.")
            return []
        
        # Map place_id to place info for efficient lookup
        places = {place.id: place for place in tweets_response.includes.get('places', [])}
        
        filtered_results = []
        for tweet in tweets_response.data:
            in_india = False
            
            # 1. Check if the tweet's geo info is available and in India
            place = places.get(tweet.geo.get('place_id')) if tweet.geo else None
            if place and place.country_code == "IN":
                in_india = True
            else:
                # 2. If no geo info, try to extract a location from the tweet text
                location_name = extract_location_from_text(tweet.text)
                if location_name:
                    # 3. Use geopy to check if the extracted location is in India
                    # Adding a delay to avoid hitting geocoding API rate limits
                    in_india = is_location_in_india(location_name)
                    time.sleep(1) # Be a good citizen, don't spam the API
            
            if in_india:
                sentiment = analyze_sentiment(tweet.text)
                filtered_results.append({'text': tweet.text, 'sentiment': sentiment})
        
        return filtered_results
    
    except tweepy.errors.TooManyRequests as e:
        print(f"Rate limit exceeded. Please wait a few minutes before trying again.")
        return []
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    keywords = ["ocean pollution", "plastic waste", "oil spill", "marine life threat"]
    print(f"Searching for tweets in India related to: {', '.join(keywords)}")
    
    indian_tweets = search_tweets_by_keywords_india(keywords)
    
    if indian_tweets:
        print("\nFound tweets from India:")
        for tweet in indian_tweets:
            print(f"Text: {tweet['text']}")
            print(f"Sentiment: {tweet['sentiment']}\n")
    else:
        print("\nNo relevant tweets found or an error occurred.")
