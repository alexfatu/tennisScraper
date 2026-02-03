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
            print(f"Page title: {driver.title}")
            try:
                element = driver.find_element(By.XPATH, '//*[@id="instanceList"]/div/div/div[2]/div/div[1]/div[2]/p')
                print("Element text:", element.text)
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
    if "No spots left" in text:
        print("No spots left")
        return 0

    m = re.search(r"(\d+)\s+spots left", text)
    if m:
        spots = int(m.group(1))
        print(f"{spots} spots left")
        notify_discord(title)
        return spots

    print(f"Unrecognized spots text: '{text}'")
    return -1

def notify_discord(title: str):
    # webhook_url = "https://discord.com/api/webhooks/xxxx"
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
