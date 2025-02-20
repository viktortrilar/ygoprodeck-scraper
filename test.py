import requests
import csv
import os
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
import time

load_dotenv()
KEY = os.getenv("SCRAPEAPI_KEY")

# ScraperAPI setup
api_url_regionals = "https://ygoprodeck.com/api/tournament/getTournaments.php?&tier=2&format=TCG&_=1739901377602"
api_url_YCS = "https://ygoprodeck.com/api/tournament/getTournaments.php?&tier=3&format=TCG&_=1739901377603"

scraper_url_regionals = f"http://api.scraperapi.com/?api_key={KEY}&url={api_url_regionals}"
scraper_url_YCS = f"http://api.scraperapi.com/?api_key={KEY}&url={api_url_YCS}"

start_time = time.time()

response_regionals = requests.get(scraper_url_regionals)
response_YCS = requests.get(scraper_url_YCS)

tournaments = []
existing_tournaments = set()

# Load existing tournaments from CSV to avoid duplication
if os.path.exists('tournament_data.csv'):
    with open('tournament_data.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_tournaments.add(row["Tournament"])

# Get only tournaments from this date onward
cutoff_date = datetime(2024, 12, 9)

# Function to get tournament data
def get_tournaments(response, tier_label):
    if response.status_code == 200:
        tournament_data = response.json()
        if 'data' in tournament_data:
            for tournament in tournament_data['data']:
                tournament_name = tournament.get("name", "")
                # Skip tournament if it already exists in CSV
                if tournament_name in existing_tournaments:
                    continue 
                
                og_date = tournament.get("event_date", "")
                if og_date:
                    tournament_date = datetime.strptime(og_date, "%Y-%m-%d")
                    if tournament_date >= cutoff_date:
                        format_date = tournament_date.strftime("%d-%m-%Y")
                        slug = tournament.get("slug", "")
                        
                        tournaments.append({
                            "Date": format_date,
                            "Country": tournament.get("country", ""),
                            "Tournament": tournament_name,
                            "Participants": tournament.get("player_count", ""),
                            "Winner": tournament.get("winner", "N/A"),
                            "Tier": tier_label,
                            "Slug": slug
                        })
        else:
            print("No data found")
    else:
        print("Error. Status code:", response.status_code)

# Function to get detailed tournament data from specific tournaments
def tournament_details(tournament_slug, tournament_name, tournament_date, country, tier):
    tournament_url = f"https://ygoprodeck.com/tournament/{tournament_slug}"
    scraper_url = f"http://api.scraperapi.com/?api_key={KEY}&url={tournament_url}"

    response = requests.get(scraper_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("#tournament_table .tournament_table_row")

        tournament_results = []

        for row in rows:

            # Get tournament placement
            placement = row.select_one(".as-tablecell b")
            placement = placement.text.strip() if placement else "N/A"

            # Get player name
            player_name = row.select_one(".player-name")
            player_name = player_name.text.strip() if player_name else "Unknown"

            # Get the archetype
            archetype = row.select(".arch-link span.badge")
            archetype = archetype[0].text.strip() if archetype else "Unknown"

            # Get engine names from <img> elements
            engines = []
            engine_imgs = row.select("img.archetype-tournament-img")
            for img in engine_imgs:
                engine_name = img.get('title', '') or img.get('alt', '')
                if engine_name:
                    engines.append(engine_name.strip())
            engine_column = ", ".join(engines) if engines else "N/A"

            # Get deck price
            deck_price_ele = row.select(".as-tablecell")[-1]
            deck_price = deck_price_ele.text.strip().replace("$", "") if deck_price_ele else "N/A"

            tournament_results.append({
                "Date": tournament_date,
                "Tournament": tournament_name,
                "Country": country,
                "Tier": tier,
                "Placement": placement,
                "Player Name": player_name,
                "Archetype": archetype,
                "Engine Used": engine_column,
                "Deck Price ($)": deck_price
            })
        return tournament_results
    else:
        print("Failed to scrape")
        return []

# Get basic tournament data for each tournament
get_tournaments(response_regionals, "Regional")
get_tournaments(response_YCS, "YCS")

# Get detailed tournament data for each tournament
detailed_tournaments = []
for tournament in tournaments:
    tournament_name = tournament["Tournament"]
    
    # Skip tournament if it has already been processed
    if tournament_name in existing_tournaments:
        print(f"Skipping details for tournament {tournament_name}")
        continue 

    tournament_slug = tournament["Slug"]
    tournament_date = tournament["Date"]
    country = tournament["Country"]
    tier = tournament["Tier"]
    
    detailed_results = tournament_details(tournament_slug, tournament_name, tournament_date, country, tier)
    detailed_tournaments.extend(detailed_results)
    
    existing_tournaments.add(tournament_name) # Mark tournament as processed

# Combine everything and add to CSV 
with open('tournament_data.csv', mode='a', newline='', encoding='utf-8') as file:
    fieldnames = ["Date", "Country", "Tournament", "Participants", "Winner", "Tier", "Placement", "Player Name", "Archetype", "Engine Used", "Deck Price ($)"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    # Write header only if file is empty
    if file.tell() == 0:
        writer.writeheader()

    writer.writerows(detailed_tournaments)

# Print confirmation
end_time = time.time()
elapsed = end_time - start_time
print("Saved to CSV")
print(f"Completed in {elapsed:.2f} seconds")
