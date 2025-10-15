"""
Multi-site automation script for takipcikrali.com/tools-style websites.
Combined version with all sites from both scripts.

Requirements:
    pip install selenium webdriver-manager

Notes:
 - Uses explicit waits and small sleep pauses.
 - Runs in normal mode (non-headless) to ensure full JS functionality.
 - Avoids user data directory conflicts by using a temporary profile.
"""

import os
import tempfile
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

SITES = [
    "https://www.takipcikrali.com/login",
    "https://takipcizen.com/login",
    "https://takipcimx.net/login",
    "https://fastfollow.in/member",
    "https://www.takipcitime.net/login",
    "https://takip88.com/login",
    "https://takipcimx.com/member",
    "https://takipciking.com/member"
]

START_COUNTS = [4, 3, 2, 3, 5, 2, 3, 2]

# ---------- XPaths ----------
XPATHS = {
    "username": '//*[@id="username"]',
    "password": '//*[@id="react-root"]/section/main/article/div/div/div[3]/form/div[2]/input',
    "login_button": '//*[@id="login_insta"]',
    "follower_button": "/html/body/div[1]/div/div/div[1]/div[2]/a",
    "target_input": "/html/body/div[4]/div[2]/div[1]/div/div[2]/form/div/input",
    "find_user_button": "/html/body/div[4]/div[2]/div[1]/div/div[2]/form/button",
    "start_button": '//*[@id="formTakipSubmitButton"]',
    "cancel_button": '//*[@id="loggedAnnouncementModal"]/div/div/div[1]/button'
}

# ---------- Wait times ----------
WAIT_TIMES = {
    "post_login": 3,
    "after_cancel": 2,
    "after_follower_click": 2,
    "after_find_user": 2,
    "start_interval": 180
}

# ---------- Helper Functions ----------
def wait_and_click(driver, xpath, timeout=20):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    element.click()
    return element

def wait_and_type(driver, xpath, text, timeout=20):
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    element.clear()
    element.send_keys(text)
    return element

# ---------- Site Flow ----------
def run_site_flow(driver, url, start_count):
    print(f"\n=== Processing site: {url} | START clicks: {start_count} ===")
    driver.get(url)
    try:
        # Login
        wait_and_type(driver, XPATHS["username"], USERNAME)
        wait_and_type(driver, XPATHS["password"], PASSWORD)
        wait_and_click(driver, XPATHS["login_button"])
        time.sleep(WAIT_TIMES["post_login"])

        # Handle optional cancel modal
        try:
            wait_and_click(driver, XPATHS["cancel_button"], timeout=5)
            time.sleep(WAIT_TIMES["after_cancel"])
            driver.refresh()
            time.sleep(2)
            print("Cancel modal handled")
        except Exception:
            print("No cancel modal found, continuing...")

        # Navigate to follower tool
        wait_and_click(driver, XPATHS["follower_button"])
        time.sleep(WAIT_TIMES["after_follower_click"])

        # Enter target user and find
        wait_and_type(driver, XPATHS["target_input"], TARGET_USERNAME)
        wait_and_click(driver, XPATHS["find_user_button"])
        time.sleep(WAIT_TIMES["after_find_user"])

        # Click START multiple times
        for i in range(start_count):
            print(f"Clicking START ({i+1}/{start_count})...")
            try:
                wait_and_click(driver, XPATHS["start_button"])
            except Exception as e:
                print(f"Click failed, retrying after refresh: {e}")
                driver.refresh()
                time.sleep(2)
                wait_and_click(driver, XPATHS["start_button"])

            print(f"Sleeping {WAIT_TIMES['start_interval']}s...")
            time.sleep(WAIT_TIMES["start_interval"])

            # Refresh for next iteration except last
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
    # Non-headless to ensure full functionality
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--test-type")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

    # Use a temporary user profile to avoid conflicts
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

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
