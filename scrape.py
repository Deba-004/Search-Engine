import time
import json
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CodingProblemScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome driver options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.problems = []
        
    def scrape_leetcode_problems(self, topic=None, limit=50):
        """Scrape problems from LeetCode"""
        logger.info(f"Scraping LeetCode problems for topic: {topic}")
        
        try:
            # LeetCode problems page
            if topic:
                url = f"https://leetcode.com/problemset/all/?topicSlugs={topic.lower()}"
            else:
                url = "https://leetcode.com/problemset/all/"
            
            self.driver.get(url)
            time.sleep(3)
            
            # Wait for problems to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='row']"))
            )
            
            # Scroll to load more problems
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find problem rows
            problem_rows = soup.find_all('div', {'role': 'row'})
            
            count = 0
            for row in problem_rows[:limit]:
                if count >= limit:
                    break
                    
                try:
                    # Extract problem details
                    title_elem = row.find('a', href=True)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        problem_url = "https://leetcode.com" + title_elem['href']
                        
                        # Extract difficulty
                        difficulty_elem = row.find('span', class_=lambda x: x and 'text-difficulty' in str(x))
                        difficulty = difficulty_elem.get_text(strip=True) if difficulty_elem else "Unknown"
                        
                        # Extract acceptance rate
                        acceptance_elem = row.find('span', string=lambda x: x and '%' in str(x))
                        acceptance = acceptance_elem.get_text(strip=True) if acceptance_elem else "N/A"
                        
                        problem_data = {
                            'platform': 'LeetCode',
                            'title': title,
                            'url': problem_url,
                            'difficulty': difficulty,
                            'acceptance_rate': acceptance,
                            'topic': topic or 'General'
                        }
                        
                        self.problems.append(problem_data)
                        count += 1
                        
                except Exception as e:
                    logger.warning(f"Error parsing LeetCode problem: {e}")
                    continue
                    
            logger.info(f"Scraped {count} problems from LeetCode")
            
        except Exception as e:
            logger.error(f"Error scraping LeetCode: {e}")
    
    def scrape_codeforces_problems(self, topic=None, limit=50):
        """Scrape problems from Codeforces"""
        logger.info(f"Scraping Codeforces problems for topic: {topic}")
        
        try:
            # Codeforces problemset
            if topic:
                url = f"https://codeforces.com/problemset?tags={topic.lower()}"
            else:
                url = "https://codeforces.com/problemset"
            
            self.driver.get(url)
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find problem table
            problem_table = soup.find('table', class_='problems')
            if not problem_table:
                logger.warning("Could not find problems table on Codeforces")
                return
            
            rows = problem_table.find_all('tr')[1:]  # Skip header row
            
            count = 0
            for row in rows[:limit]:
                if count >= limit:
                    break
                    
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Problem ID and title
                        problem_link = cells[1].find('a')
                        if problem_link:
                            title = problem_link.get_text(strip=True)
                            problem_url = "https://codeforces.com" + problem_link['href']
                            
                            # Extract rating/difficulty
                            rating_elem = cells[-1] if len(cells) > 2 else None
                            rating = rating_elem.get_text(strip=True) if rating_elem else "Unrated"
                            
                            # Extract solved count
                            solved_elem = cells[-2] if len(cells) > 3 else None
                            solved_count = solved_elem.get_text(strip=True) if solved_elem else "N/A"
                            
                            problem_data = {
                                'platform': 'Codeforces',
                                'title': title,
                                'url': problem_url,
                                'difficulty': rating,
                                'solved_count': solved_count,
                                'topic': topic or 'General'
                            }
                            
                            self.problems.append(problem_data)
                            count += 1
                            
                except Exception as e:
                    logger.warning(f"Error parsing Codeforces problem: {e}")
                    continue
                    
            logger.info(f"Scraped {count} problems from Codeforces")
            
        except Exception as e:
            logger.error(f"Error scraping Codeforces: {e}")
    
    def scrape_hackerrank_problems(self, domain="algorithms", limit=50):
        """Scrape problems from HackerRank"""
        logger.info(f"Scraping HackerRank problems from domain: {domain}")
        
        try:
            url = f"https://www.hackerrank.com/domains/{domain}"
            self.driver.get(url)
            time.sleep(3)
            
            # Scroll to load problems
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find problem links
            problem_links = soup.find_all('a', href=lambda x: x and '/challenges/' in str(x))
            
            count = 0
            seen_problems = set()
            
            for link in problem_links[:limit * 2]:  # Get more to filter duplicates
                if count >= limit:
                    break
                    
                try:
                    href = link.get('href')
                    if href and '/challenges/' in href and href not in seen_problems:
                        seen_problems.add(href)
                        
                        title = link.get_text(strip=True)
                        if title and len(title) > 3:  # Filter out short/empty titles
                            problem_url = "https://www.hackerrank.com" + href
                            
                            # Extract difficulty from parent elements
                            difficulty = "Medium"  # Default
                            parent = link.find_parent()
                            if parent:
                                difficulty_elem = parent.find('span', class_=lambda x: x and 'difficulty' in str(x).lower())
                                if difficulty_elem:
                                    difficulty = difficulty_elem.get_text(strip=True)
                            
                            problem_data = {
                                'platform': 'HackerRank',
                                'title': title,
                                'url': problem_url,
                                'difficulty': difficulty,
                                'domain': domain,
                                'topic': domain
                            }
                            
                            self.problems.append(problem_data)
                            count += 1
                            
                except Exception as e:
                    logger.warning(f"Error parsing HackerRank problem: {e}")
                    continue
                    
            logger.info(f"Scraped {count} problems from HackerRank")
            
        except Exception as e:
            logger.error(f"Error scraping HackerRank: {e}")
    
    def scrape_codechef_problems(self, limit=50):
        """Scrape problems from CodeChef"""
        logger.info("Scraping CodeChef problems")
        
        try:
            url = "https://www.codechef.com/problems/school"
            self.driver.get(url)
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find problem table
            problem_rows = soup.find_all('tr')
            
            count = 0
            for row in problem_rows[:limit]:
                if count >= limit:
                    break
                    
                try:
                    problem_link = row.find('a', href=lambda x: x and '/problems/' in str(x))
                    if problem_link:
                        title = problem_link.get_text(strip=True)
                        problem_url = "https://www.codechef.com" + problem_link['href']
                        
                        # Extract difficulty
                        difficulty_cell = row.find('td', class_=lambda x: x and 'num' in str(x))
                        difficulty = difficulty_cell.get_text(strip=True) if difficulty_cell else "School"
                        
                        problem_data = {
                            'platform': 'CodeChef',
                            'title': title,
                            'url': problem_url,
                            'difficulty': difficulty,
                            'topic': 'School'
                        }
                        
                        self.problems.append(problem_data)
                        count += 1
                        
                except Exception as e:
                    logger.warning(f"Error parsing CodeChef problem: {e}")
                    continue
                    
            logger.info(f"Scraped {count} problems from CodeChef")
            
        except Exception as e:
            logger.error(f"Error scraping CodeChef: {e}")
    
    def save_problems(self, filename="coding_problems.json"):
        """Save scraped problems to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.problems, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.problems)} problems to {filename}")
        except Exception as e:
            logger.error(f"Error saving problems: {e}")
    
    def save_to_csv(self, filename="coding_problems.csv"):
        """Save scraped problems to CSV file"""
        try:
            df = pd.DataFrame(self.problems)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Saved {len(self.problems)} problems to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    def get_problems_by_platform(self, platform):
        """Get problems filtered by platform"""
        return [p for p in self.problems if p['platform'] == platform]
    
    def get_problems_by_topic(self, topic):
        """Get problems filtered by topic"""
        return [p for p in self.problems if topic.lower() in p.get('topic', '').lower()]
    
    def print_summary(self):
        """Print summary of scraped problems"""
        if not self.problems:
            print("No problems scraped yet.")
            return
        
        platforms = {}
        topics = {}
        difficulties = {}
        
        for problem in self.problems:
            platform = problem['platform']
            topic = problem.get('topic', 'Unknown')
            difficulty = problem.get('difficulty', 'Unknown')
            
            platforms[platform] = platforms.get(platform, 0) + 1
            topics[topic] = topics.get(topic, 0) + 1
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        print(f"\n=== SCRAPING SUMMARY ===")
        print(f"Total problems scraped: {len(self.problems)}")
        print(f"\nBy Platform:")
        for platform, count in platforms.items():
            print(f"  {platform}: {count}")
        print(f"\nBy Topic:")
        for topic, count in list(topics.items())[:10]:  # Show top 10 topics
            print(f"  {topic}: {count}")
        print(f"\nBy Difficulty:")
        for difficulty, count in difficulties.items():
            print(f"  {difficulty}: {count}")
    
    def close(self):
        """Close the webdriver"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function to demonstrate the scraper"""
    scraper = CodingProblemScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Define topics to scrape
        topics = ['array', 'string', 'dynamic-programming', 'tree', 'graph']
        
        # Scrape from different platforms
        print("Starting to scrape coding problems...")
        
        # LeetCode
        for topic in topics[:2]:  # Scrape 2 topics from LeetCode
            scraper.scrape_leetcode_problems(topic=topic, limit=20)
            time.sleep(2)
        
        # Codeforces
        scraper.scrape_codeforces_problems(topic='dp', limit=25)
        time.sleep(2)
        
        # HackerRank
        scraper.scrape_hackerrank_problems(domain='algorithms', limit=30)
        time.sleep(2)
        
        # CodeChef
        scraper.scrape_codechef_problems(limit=20)
        
        # Print summary
        scraper.print_summary()
        
        # Save results
        scraper.save_problems("coding_problems.json")
        scraper.save_to_csv("coding_problems.csv")
        
        print("\nScraping completed! Check 'coding_problems.json' and 'coding_problems.csv' files.")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
