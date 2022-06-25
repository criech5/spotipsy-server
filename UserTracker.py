import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def edit_users(login, password, email):
    options = webdriver.ChromeOptions()
    # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get('https://developer.spotify.com/dashboard/login')
    driver.implicitly_wait(0.5)
    login_button = driver.find_element(by=By.CSS_SELECTOR, value="button[data-ng-click='login()']")
    login_button.click()
    driver.implicitly_wait(0.5)
    # Switch to the login popup window and select facebook
    WebDriverWait(driver, 10).until(
        ExpectedConditions.number_of_windows_to_be(2)
    )
    windows = driver.window_handles
    driver.switch_to.window(windows[1])
    driver.implicitly_wait(0.5)
    facebook_button = driver.find_element(by=By.CSS_SELECTOR, value="button[data-testid='facebook-login']")
    facebook_button.click()
    driver.implicitly_wait(0.5)
    # Grab facebook login elements and input my login info
    email_box = driver.find_element(by=By.NAME, value='email')
    password_box = driver.find_element(by=By.NAME, value='pass')
    facebook_login_button = driver.find_element(by=By.NAME, value='login')
    email_box.send_keys(login)
    password_box.send_keys(password)
    facebook_login_button.click()
    continue_button = driver.find_element(by=By.CSS_SELECTOR, value="div[aria-label='Continue']")
    if continue_button:
        continue_button.click()
    # Switch back to the other window, which should now be logged in, and close banner notif
    driver.implicitly_wait(1)
    driver.switch_to.window(windows[0])
    driver.implicitly_wait(10)
    cookie_close_button = driver.find_element(by=By.ID, value="onetrust-close-btn-container")
    driver.implicitly_wait(1)
    cookie_close_button.click()
    driver.implicitly_wait(1)

    # Click on the app
    spotipsy_link = driver.find_element(by=By.CSS_SELECTOR, value="a[title='SpotiPsy']")
    spotipsy_link.click()
    users_button = WebDriverWait(driver, 15).until(
        ExpectedConditions.element_to_be_clickable((By.CSS_SELECTOR, "button[ng-click='showUsersAndAccess()']"))
    )
    users_button.click()
    driver.implicitly_wait(1)

    table_rows = driver.find_elements(by=By.XPATH, value="//table/tbody/tr")
    users = []
    for row in table_rows:
        user = row.find_elements(by=By.TAG_NAME, value='td')[1].text
        users.append(user)
    if email in users:
        print(f'User {email} already registered; no action taken.')
        return
    elif len(users) < 25:
        add_user(driver, email)
    else:
        delete_button = table_rows[len(table_rows) - 1].find_element(by=By.TAG_NAME, value='i')
        delete_button.click()
        driver.implicitly_wait(1)
        add_user(driver, email)


def add_user(driver, new_email):
    add_link = driver.find_element(by=By.CSS_SELECTOR, value="a[data-target='#add-user-modal']")
    add_link.click()

    # Input user information
    name_box = driver.find_element(by=By.CSS_SELECTOR, value="input[ng-model='userName']")
    new_email_box = driver.find_element(by=By.CSS_SELECTOR, value="input[ng-model='userEmail']")
    name_box.send_keys('New User')
    new_email_box.send_keys(new_email)

    # Add user
    add_button = driver.find_element(by=By.CSS_SELECTOR, value="button[ng-click='addUser()']")
    add_button.click()
    print(f'User {new_email} has been added.')


if __name__ == '__main__':
    edit_users('@gmail.com', '', 'userXX@gmail.com')

