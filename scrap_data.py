import requests
import time
import pandas as pd
import html
import html5lib
from bs4 import BeautifulSoup

def mergeData(matches_table, soup, name_data, col_names, name_table):
    links = [l.get("href") for l in soup.find_all('a')]
    links = [l for l in links if l and f'all_comps/{name_data}/' in l]
    data = requests.get(f"https://fbref.com{links[0]}")
    table_need_merge = pd.read_html(data.text, match=f"{name_table}")[0]
    table_need_merge.columns = table_need_merge.columns.droplevel()
    try:
        team_data = matches_table.merge(table_need_merge[col_names], on="Date")
    except ValueError:
        return None
    team_data = team_data[team_data["Comp"] == "Premier League"]
    return team_data

def run():
    data_url = "https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats"

    years = [2023, 2022, 2021, 2020]
    all_matches = []
    for year in years:
        data = requests.get(data_url)
        soup = BeautifulSoup(data.text, features='html.parser')
        standings_table = soup.select('table.stats_table')[0]
        links = [l.get('href') for l in standings_table.find_all('a')]
        links = [l for l in links if "/squads/" in l]
        team_urls = [f"https://fbref.com{l}" for l in links]
        previous_season = soup.select("a.prev")[0].get("href")
        data_url = f"https://fbref.com{previous_season}"
        for team_url in team_urls:
            team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
            data = requests.get(team_url)
            matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
            soup = BeautifulSoup(data.text, features='html.parser')
            # Shooting
            column_names = ["Date", "Sh", "SoT", "SoT%", "G/Sh", "G/SoT"]
            team_data = mergeData(matches, soup, "shooting", column_names, "Shooting")
            print("shooting")
            # Passing
            column_names = ["Date", "Cmp", "Cmp%"]
            team_data = mergeData(team_data, soup, "passing", column_names, "Passing")
            print("passing")
            #Shot and Creation
            column_names = ["Date", "SCA", "GCA"]
            team_data = mergeData(team_data, soup, "gca", column_names, "Goal and Shot Creation")
            print("GCA")
            #Possesion
            column_names = ["Date", "Touches", "Succ%", "Tkld%"]
            team_data = mergeData(team_data, soup, "possession", column_names, "Possession")
            team_data["Season"] = year
            team_data["Team"] = team_name
            all_matches.append(team_data)
            print("STT: ", len(all_matches))
            print("Tên đội: ", team_name)
            print("Mùa: ", year)
            time.sleep(5)
    len(all_matches)
    match_df = pd.concat(all_matches)
    match_df.columns = [c.lower() for c in match_df.columns]
    match_df.to_csv("matches.csv")

run()




