import requests
import csv
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("SCRAPEAPI_KEY")

# ScraperAPI setup
api_url = "https://ygoprodeck.com/api/tournament/getTournaments.php?&tier=2&format=TCG&_=1739901377602"
scraper_url = f"http://api.scraperapi.com/?api_key={KEY}&url={api_url}"
response = requests.get(scraper_url)

# Check if request was successful
if response.status_code == 200:
   
    # Load the JSON data
    tournament_data = response.json() 
    
    # Check if the 'data' key is present then loop through the data and save it to a CSV file
    if 'data' in tournament_data:

        with open('tournament_data.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Date", "Country", "Tournament", "Participants", "Winner"])
            writer.writeheader()
            
            
            for tournament in tournament_data['data']:
                writer.writerow({
                    "Date": tournament.get("event_date", ""),
                    "Country": tournament.get("country", ""),
                    "Tournament": tournament.get("name", ""),
                    "Participants": tournament.get("player_count", ""),
                    "Winner": tournament.get("winner", "N/A")
                })

        print("Data saved to tournament_data.csv")
    else:
        print("No data found")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
