import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service


def save_credentials(username, password):
    with open('credentials.txt', 'w') as file:
        file.write(f"{username}\n{password}")


def load_credentials():
    if not os.path.exists('credentials.txt'):
        return None

    with open('credentials.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()

    return None


def prompt_credentials():
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password)
    return username, password


def login(bot, username, password):
    bot.get('https://www.instagram.com/accounts/login/')
    time.sleep(1)

    # Check if cookies need to be accepted
    try:
        element = bot.find_element(By.XPATH, "/html/body/div[4]/div/div/div[3]/div[2]/button")
        element.click()
    except NoSuchElementException:
        print("[Info] - Instagram did not require to accept cookies this time.")

    print("[Info] - Logging in...")
    try:
        username_input = WebDriverWait(bot, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))

        password_input = WebDriverWait(bot, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

        username_input.clear()
        username_input.send_keys(username)
        time.sleep(1)
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(1)

        login_button = WebDriverWait(bot, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

        login_button.click()
        time.sleep(5)

    except TimeoutException:
        print("[Error] - Timeout while trying to log in. Check if Instagram changed the login flow.")
        bot.quit()
        exit()


def scrape_followers(bot, username, user_input):
    bot.get(f'https://www.instagram.com/{username}/')
    time.sleep(3.5)
    
    try:
        followers_link = WebDriverWait(bot, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]")))

        followers_link.click()
        time.sleep(2)
        print(f"[Info] - Scraping followers for {username}...")

        users = set()

        while len(users) < user_input:
            followers = bot.find_elements(By.XPATH, "//a[contains(@href, '/')]")

            for i in followers:
                if i.get_attribute('href'):
                    users.add(i.get_attribute('href').split("/")[3])
                else:
                    continue

            ActionChains(bot).send_keys(Keys.END).perform()
            time.sleep(1)

        users = list(users)[:user_input]  # Trim the user list to match the desired number of followers

        print(f"[Info] - Followers for {username}:")
        # Output as JSON to terminal
        followers_json = json.dumps({username: users}, indent=4)
        print(followers_json)

    except TimeoutException:
        print(f"[Error] - Timeout while trying to scrape followers for {username}.")
        return


def scrape():
    start_time = time.time()  # Start the timer

    credentials = load_credentials()

    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    user_input = int(input('[Required] - How many followers do you want to scrape (100-2000 recommended): '))

    usernames = input("Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")

    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(service=service, options=options)
    bot.set_page_load_timeout(15)  # Set the page load timeout to 15 seconds

    login(bot, username, password)

    for user in usernames:
        user = user.strip()
        scrape_followers(bot, user, user_input)

    bot.quit()

    end_time = time.time()  # End the timer
    total_time = end_time - start_time  # Calculate the total time taken
    print(f"[Info] - Total time taken: {total_time:.2f} seconds")


if __name__ == '__main__':
    TIMEOUT = 15  # Timeout for loading pages or elements
    scrape()
