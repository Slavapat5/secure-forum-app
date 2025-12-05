# selenium_login_test.py
# Simple end-to-end test of registration + login on the SECURE branch using Microsoft Edge

import time
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

BASE_URL = "http://127.0.0.1:5000"  # or http://localhost:5000


def main():
    # Generate a unique username each run so registration doesn't clash
    unique_username = "testuser_" + uuid.uuid4().hex[:6]
    password = "Test123!password"

    # Start Edge with WebDriver Manager
    service = EdgeService(r"C:\Users\mama1\WebDrivers\msedgedriver.exe")
    driver = webdriver.Edge(service=service)

    try:
        # 1) Go to register page
        driver.get(BASE_URL + "/secure/register")

        # 2) Fill registration form
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")

        username_input.send_keys(unique_username)
        password_input.send_keys(password)

        # Submit the form (assumes there's only one button on the form)
        submit_button = driver.find_element(By.TAG_NAME, "button")
        submit_button.click()

        time.sleep(1)

        # 3) After successful registration we should be on the login page
        assert "/secure/login" in driver.current_url, "Did not reach login page after registration"

        # 4) Fill login form with same credentials
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")

        username_input.clear()
        password_input.clear()

        username_input.send_keys(unique_username)
        password_input.send_keys(password)

        submit_button = driver.find_element(By.TAG_NAME, "button")
        submit_button.click()

        time.sleep(1)

        # 5) We should now be on the dashboard
        assert "/secure/dashboard" in driver.current_url, "Login did not redirect to dashboard"

        # 6) Check that the page shows the logged-in username somewhere
        page_source = driver.page_source
        assert unique_username in page_source, "Dashboard does not show logged-in username"

        print("[PASS] Selenium test: register + login flow works on secure branch (Edge).")

    except AssertionError as e:
        print(f"[FAIL] Selenium test assertion: {e}")
    except Exception as e:
        print(f"[ERROR] Selenium test encountered an exception: {e}")
    finally:
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    main()
