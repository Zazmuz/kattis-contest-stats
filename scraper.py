import requests
import json
import time
import schedule
from bs4 import BeautifulSoup
from datetime import datetime

# example url: "https://polong25.kattis.com/contests/polong25/standings"
URL = contest_standing_url
DATA_FILE = "standings_data.json"
USER_EMAIL = name@mail.com

# get the scoreboard and update DATA_FILE if correctly fetched
def fetch_and_save_data():
    response = requests.get(URL, headers={"User-Agent": f"Scoreboard-Scraper-zazmuz/1.0 (mailto:{USER_EMAIL})"})

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        standings_table = soup.find("table", class_="table2 sticky-header standings-table")

        if not standings_table:
            print("Standings table not found.")
            return

        results = {}
        timestamp = datetime.now().isoformat()

        for row in standings_table.find_all("tr")[1:]:
            columns = row.find_all("td")
            if len(columns) < 2:
                continue

            team_name = columns[1].text.strip()
            print(f"Processing team: {team_name}")
            team_scores = {}

            for i in range(2, len(columns) - 1):
                problem_cell = columns[i]
                problem_result = problem_cell.find("span", class_="standings-table-result-cell-text")

                if problem_result:
                    print(problem_result.text.strip().split("\n"))
                    score = problem_result.text.strip().split("\n")[0]
                    tries = problem_result.find("span", class_="standings-table-result-cell-time").text.strip()
                    team_scores[f"Problem {chr(ord('A') + i - 2)}"] = {
                        "score": score,
                        "tries": tries,
                    }

            results[team_name] = team_scores

        # append or create
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        data.append({"timestamp": timestamp, "results": results})

        # dump new
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"Data saved at {timestamp}")

    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

# fetch once per min
often = 59
schedule.every(often).seconds.do(fetch_and_save_data)

if __name__ == "__main__":
    print(f"Scraping started every {often} seconds")
    fetch_and_save_data()
    while True:
        schedule.run_pending()
        time.sleep(1)