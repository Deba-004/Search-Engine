# backend/scraper.py
import requests
from bs4 import BeautifulSoup
import json

def scrape_codeforces():
    url = 'https://codeforces.com/problemset'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    problems = []

    table = soup.find('table', class_='problems')
    if not table:
        return problems

    rows = table.find_all('tr')[1:20]  # get top 20 for demo
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue
        title = cols[1].text.strip()
        link = "https://codeforces.com" + cols[1].find('a')['href']
        difficulty = cols[-1].text.strip() or "Unknown"
        problems.append({
            'title': title,
            'link': link,
            'difficulty': difficulty,
            'platform': 'Codeforces',
            'language': 'C++'  # placeholder
        })
    return problems

def scrape_all():
    all_problems = scrape_codeforces()
    with open('../data/problems.json', 'w') as f:
        json.dump(all_problems, f, indent=2)

if __name__ == "__main__":
    scrape_all()