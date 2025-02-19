import requests
import csv
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("SCRAPEAPI_KEY")

# ScraperAPI setup
api_url_regionals = "https://ygoprodeck.com/api/tournament/getTournaments.php?&tier=2&format=TCG&_=1739901377602"
api_url_YCS = "https://ygoprodeck.com/api/tournament/getTournaments.php?&tier=3&format=TCG&_=1739901377603"

scraper_url_regionals = f"http://api.scraperapi.com/?api_key={KEY}&url={api_url_regionals}"
scraper_url_YCS = f"http://api.scraperapi.com/?api_key={KEY}&url={api_url_YCS}"

response_regionals = requests.get(scraper_url_regionals)
response_YCS = requests.get(scraper_url_YCS)

tournaments = []

# Function to get tournament data
def get_tournaments(response, tier_label):
    if response.status_code == 200:
        tournament_data = response.json() 
        if 'data' in tournament_data:            
            for tournament in tournament_data['data']:
                tournaments.append({
                    "Date": tournament.get("event_date", ""),
                    "Country": tournament.get("country", ""),
                    "Tournament": tournament.get("name", ""),
                    "Participants": tournament.get("player_count", ""),
                    "Winner": tournament.get("winner", "N/A"),
                    "Tier": tier_label
                })
        else:
            print("No data found")
    else:
        print("Error. Status code:", response.status_code)

# Get tournament data
get_tournaments(response_regionals, "Regional")
get_tournaments(response_YCS, "YCS")

# Combine and write data to CSV
with open('tournament_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["Date", "Country", "Tournament", "Participants", "Winner", "Tier"])
    writer.writeheader()
    writer.writerows(tournaments)
