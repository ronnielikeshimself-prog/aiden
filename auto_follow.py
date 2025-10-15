"""
Multi-site automation script for takipcikrali.com/tools-style websites.
Combined version with all sites from both scripts.

Requirements:
    pip install selenium webdriver-manager

Notes:
 - Uses explicit waits and small sleep pauses.
 - To run headless (without opening the browser), uncomment the headless option in ChromeOptions.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------- CONFIG ----------
USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
TARGET_USERNAME = "_.dym.gaurav_"

# List of all site URLs (keeping the last 2 websites at the end)
SITES = [
    "https://www.takipcikrali.com/login",
    "https://takipcizen.com/login", 
    "https://takipcimx.net/login",
    "https://fastfollow.in/member",
    "https://www.takipcitime.net/login",
    "https://takip88.com/login",
    "https://takipcimx.com/member",      # Last 2 from second script
    "https://takipciking.com/member"     # Last 2 from second script
]

# Number of times to click START for each site (matching order of SITES)
START_COUNTS = [4, 3, 2, 3, 5, 2, 3, 2]

# Common XPaths 
XPATH_USERNAME = '//*[@id="username"]'
XPATH_PASSWORD = '//*[@id="react-root"]/section/main/article/div/div/div[3]/form/div[2]/input'
XPATH_LOGIN_BUTTON = '//*[@id="login_insta"]'
XPATH_FOLLOWER_BUTTON = "/html/body/div[1]/div/div/div[1]/div[2]/a"
XPATH_TARGET_INPUT = "/html/body/div[4]/div[2]/div[1]/div/div[2]/form/div/input"
XPATH_FIND_USER_BUTTON = "/html/body/div[4]/div[2]/div[1]/div/div[2]/form/button"
XPATH_START_BUTTON = '//*[@id="formTakipSubmitButton"]'
XPATH_CANCEL_BUTTON = '//*[@id="loggedAnnouncementModal"]/div/div/div[1]/button'  # For some sites

# Wait times
POST_LOGIN_SLEEP = 3
AFTER_CANCEL_SLEEP = 2
AFTER_FOLLOWER_CLICK_SLEEP = 2
AFTER_FIND_USER_SLEEP = 2
START_SLEEP_SECONDS = 180


# ---------- Helper functions ----------
def wait_and_click(driver, xpath, timeout=20):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    el.click()
    return el

def wait_and_type(driver, xpath, text, timeout=20):
    el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    el.clear()
    el.send_keys(text)
    return el


# ---------- Main flow for one site ----------
def run_site_flow(driver, url, start_count):
    print(f"\n=== Processing site: {url} | START clicks: {start_count} ===")
    driver.get(url)

    try:
        # Login
        wait_and_type(driver, XPATH_USERNAME, USERNAME)
        wait_and_type(driver, XPATH_PASSWORD, PASSWORD)
        wait_and_click(driver, XPATH_LOGIN_BUTTON)
        time.sleep(POST_LOGIN_SLEEP)

        # Try to handle cancel modal (for sites that have it)
        try:
            wait_and_click(driver, XPATH_CANCEL_BUTTON, timeout=5)
            time.sleep(AFTER_CANCEL_SLEEP)
            driver.refresh()
            time.sleep(2)
            print("Cancel modal handled")
        except Exception:
            print("No cancel modal found - continuing...")

        # Navigate to follower tool
        wait_and_click(driver, XPATH_FOLLOWER_BUTTON)
        time.sleep(AFTER_FOLLOWER_CLICK_SLEEP)

        # Enter target user and find
        wait_and_type(driver, XPATH_TARGET_INPUT, TARGET_USERNAME)
        wait_and_click(driver, XPATH_FIND_USER_BUTTON)
        time.sleep(AFTER_FIND_USER_SLEEP)

        # Click START multiple times
        for i in range(start_count):
            print(f"Clicking START ({i+1}/{start_count})...")
            try:
                wait_and_click(driver, XPATH_START_BUTTON)
            except Exception as e:
                print(f"Click failed, retrying after refresh: {e}")
                driver.refresh()
                time.sleep(2)
                wait_and_click(driver, XPATH_START_BUTTON)

            print(f"Sleeping {START_SLEEP_SECONDS}s...")
            time.sleep(START_SLEEP_SECONDS)
            
            # Refresh for next iteration (except on last iteration)
            if i < start_count - 1:
                driver.refresh()
                time.sleep(2)

        print(f"✅ Completed site: {url}")

    except Exception as e:
        print(f"⚠️ Error on {url}: {e}")


# ---------- Main ----------
def main():
    if len(SITES) != len(START_COUNTS):
        raise ValueError("SITES and START_COUNTS must have the same length.")

    options = webdriver.ChromeOptions()
    #options.add_argument("--headless=new")  # uncomment for headless mode
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--test-type")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    # Create a temporary user data dir
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        for site, count in zip(SITES, START_COUNTS):
            run_site_flow(driver, site, count)
            print("Waiting 5s before next site...\n")
            time.sleep(5)

        print("🎯 All sites processed successfully.")

    finally:
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    main()
