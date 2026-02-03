from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from multiprocessing import Process
import re
import requests

BEGINNER = "https://warrior.uwaterloo.ca/Program/GetProgramDetails?courseId=4646d6f1-8319-4b35-bea4-78d0250fc3b8"
INTERMEDIATE = "https://warrior.uwaterloo.ca/Program/GetProgramDetails?courseId=98197a06-adb4-4785-b383-e5bd428903a0"


def scrape(url: str):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        while True:
            time.sleep(2)
            print(f"Checking: {driver.title}")
            try:
                element = driver.find_element(By.XPATH, '//*[@id="instanceList"]/div/div/div[2]/div/div[1]/div[2]/p')
                spotsLeft(element.text, driver.title)
            except Exception:
                print("Element not found")
            time.sleep(3)
            driver.refresh()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


def spotsLeft(text: str, title: str) -> int:
    m = re.search(r"(?:(\d+)|No)\s+spots?\s+left", text, re.IGNORECASE)
    if not m:
        print(f"Unrecognized spots text: '{text}'")
        return -1
    
    spots = 0 if m.group(1) is None else int(m.group(1))
    print(f"{spots} spots left" if spots else "No spots left")
    if spots > 0:
        notify_discord(title)
    return spots

def notify_discord(title: str):
    webhook_url = "https://discord.com/api/webhooks/1466585583685079060/l5OMi87Bcx00ph3dnONpSBQZiqmqjN8gcECVhaRs08tY0qVyRRn6ih1t3GXg36oHJu92"
    data = {
        "content": f"Tennis class spot available! Sign up now! Title: {title}"
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Discord notification sent successfully.")
    else:
        print(f"Failed to send Discord notification. Status code: {response.status_code}")


# Run beginner and intermediate scrapers in parallel
def run_parallel_scrapers():
    p1 = Process(target=scrape, args=(BEGINNER,))
    p2 = Process(target=scrape, args=(INTERMEDIATE,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == '__main__':
    run_parallel_scrapers()
