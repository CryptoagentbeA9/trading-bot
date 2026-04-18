"""
Social Platform Integrations
Handles posting to Binance Square, Twitter, and Telegram
"""

import time
import logging
from typing import Optional, Dict, List
from datetime import datetime
import requests

# Selenium for Binance Square
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Twitter API
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class BinanceSquarePoster:
    """Post to Binance Square using web automation"""

    def __init__(self, email: str, password: str, headless: bool = True):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium not installed. Run: pip install selenium")

        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None
        self.logged_in = False

    def _init_driver(self):
        """Initialize Chrome driver"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def login(self) -> bool:
        """Login to Binance Square"""
        try:
            if not self.driver:
                self._init_driver()

            self.driver.get('https://www.binance.com/en/square')
            time.sleep(3)

            # Click login button
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log In')]")
            login_btn.click()
            time.sleep(2)

            # Enter credentials
            email_input = self.driver.find_element(By.ID, 'email')
            email_input.send_keys(self.email)

            password_input = self.driver.find_element(By.ID, 'password')
            password_input.send_keys(self.password)

            # Submit
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            time.sleep(5)

            self.logged_in = True
            logger.info("Logged in to Binance Square")
            return True

        except Exception as e:
            logger.error(f"Binance Square login failed: {e}")
            return False

    def post(self, content: str, image_path: Optional[str] = None) -> bool:
        """
        Post content to Binance Square

        Args:
            content: Text content
            image_path: Optional path to image

        Returns:
            True if successful
        """
        try:
            if not self.logged_in:
                if not self.login():
                    return False

            # Navigate to create post
            self.driver.get('https://www.binance.com/en/square/create')
            time.sleep(2)

            # Enter content
            text_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Share']"))
            )
            text_area.send_keys(content)

            # Upload image if provided
            if image_path:
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(image_path)
                time.sleep(3)

            # Click post button
            post_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
            post_btn.click()
            time.sleep(3)

            logger.info("Posted to Binance Square")
            return True

        except Exception as e:
            logger.error(f"Binance Square post failed: {e}")
            return False

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None


class TwitterPoster:
    """Post to Twitter/X using API"""

    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        if not TWEEPY_AVAILABLE:
            raise ImportError("Tweepy not installed. Run: pip install tweepy")

        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth)
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

    def post(self, content: str, image_path: Optional[str] = None) -> bool:
        """
        Post tweet

        Args:
            content: Tweet text (max 280 chars)
            image_path: Optional image path

        Returns:
            True if successful
        """
        try:
            if len(content) > 280:
                content = content[:277] + "..."

            if image_path:
                media = self.api.media_upload(image_path)
                self.client.create_tweet(text=content, media_ids=[media.media_id])
            else:
                self.client.create_tweet(text=content)

            logger.info("Posted to Twitter")
            return True

        except Exception as e:
            logger.error(f"Twitter post failed: {e}")
            return False


class TelegramPoster:
    """Post to Telegram channel"""

    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def post(self, content: str, image_path: Optional[str] = None) -> bool:
        """
        Send message to Telegram channel

        Args:
            content: Message text
            image_path: Optional image path

        Returns:
            True if successful
        """
        try:
            if image_path:
                # Send photo with caption
                with open(image_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {
                        'chat_id': self.channel_id,
                        'caption': content,
                        'parse_mode': 'HTML'
                    }
                    response = requests.post(
                        f"{self.base_url}/sendPhoto",
                        files=files,
                        data=data
                    )
            else:
                # Send text message
                data = {
                    'chat_id': self.channel_id,
                    'text': content,
                    'parse_mode': 'HTML'
                }
                response = requests.post(
                    f"{self.base_url}/sendMessage",
                    json=data
                )

            if response.status_code == 200:
                logger.info("Posted to Telegram")
                return True
            else:
                logger.error(f"Telegram post failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Telegram post failed: {e}")
            return False
