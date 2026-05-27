"""Verified Vinted automation patch with photo processing, category attempt, and 40% price rule."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

from playwright.sync_api import sync_playwright

from agents.photo_agent import PhotoAgent


class VintedAgent:

    SELL_URL = "https://www.vinted.com/items/new"

    TITLE_SELECTORS = [
        'input[name="title"]',
        'input[placeholder*="title" i]',
        'input[aria-label*="title" i]',
        'input[type="text"]',
    ]

    DESCRIPTION_SELECTORS = [
        'textarea[name="description"]',
        'textarea[data-testid*="description" i]',
        'textarea',
    ]

    PRICE_SELECTORS = [
        'input[name="price"]',
        'input[data-testid*="price" i]',
        'input[inputmode="decimal"]',
        'input[type="number"]',
    ]

    CATEGORY_SELECTORS = [
        'button[data-testid*="category" i]',
        'div[data-testid*="category" i]',
        'input[placeholder*="category" i]',
        'button:has-text("Category")',
        'div:has-text("Select a category")',
    ]

    def __init__(
        self,
        cdp_endpoint: str = "http://127.0.0.1:9222",
        chrome_path: str = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        user_data_dir: str = r"D:\chrome-debug",
        process_photos: bool = True,
    ):

        self.cdp_endpoint = cdp_endpoint
        self.chrome_path = chrome_path
        self.user_data_dir = user_data_dir
        self.process_photos = process_photos

        self.browser = None
        self.context = None
        self.page = None
        self._playwright = None
        self.photo_agent = PhotoAgent()

        Path("screenshots").mkdir(exist_ok=True)

    def __enter__(self):

        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass

    def launch_chrome_debug(self):

        cmd = [
            self.chrome_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        print("Launching Chrome...")
        print(cmd)

        subprocess.Popen(cmd, shell=False)

        time.sleep(10)

    def connect(self):

        self._playwright = sync_playwright().start()

        connected = False

        try:

            self.browser = self._playwright.chromium.connect_over_cdp(
                self.cdp_endpoint
            )

            connected = True

            print("Connected to existing Chrome.")

        except Exception as e:

            print("Initial CDP failed.")
            print(e)

            self.launch_chrome_debug()

        if not connected:

            for attempt in range(10):

                try:

                    print(f"Retry {attempt + 1}/10")

                    self.browser = self._playwright.chromium.connect_over_cdp(
                        self.cdp_endpoint
                    )

                    connected = True

                    break

                except Exception as retry_error:

                    print(retry_error)

                    time.sleep(2)

        if not connected:
            raise RuntimeError("Failed to connect to Chrome CDP.")

        for _ in range(10):

            if self.browser.contexts:
                break

            time.sleep(1)

        self.context = self.browser.contexts[0]

        self.page = None

        if self.context.pages:

            for p in self.context.pages:

                try:

                    if "vinted" in p.url.lower():
                        self.page = p
                        break

                except Exception:
                    pass

        if self.page is None:
            self.page = self.context.new_page()

        self.page.bring_to_front()

    def _locator(self, selectors: Iterable[str]):

        for selector in selectors:

            try:

                locator = self.page.locator(selector).first

                if locator.count() > 0:
                    return locator

            except Exception:
                pass

        return None

    def ensure_logged_in(self):

        self.page.goto(
            self.SELL_URL,
            wait_until="domcontentloaded"
        )

        self.page.wait_for_timeout(4000)

        url = self.page.url.lower()

        blocked_terms = [
            "login",
            "auth",
            "captcha",
            "challenge",
        ]

        if any(term in url for term in blocked_terms):

            raise RuntimeError(
                "Vinted requires login."
            )

    def open_sell_page(self):

        self.page.goto(
            self.SELL_URL,
            wait_until="domcontentloaded"
        )

        self.page.wait_for_timeout(4000)

    def upload_images(self, image_paths: list[str]):

        upload_input = self.page.locator('input[type="file"]').first

        if upload_input.count() == 0:
            self.page.screenshot(path="screenshots/debug_no_file_input.png")
            raise RuntimeError("Could not find upload input.")

        print("Uploading these images:")
        for path in image_paths:
            print(path)

        upload_input.set_input_files(image_paths)

        self.page.wait_for_timeout(8000)

        self.page.screenshot(path="screenshots/debug_after_upload.png")

    def fill_title(self, title: str):

        locator = self._locator(self.TITLE_SELECTORS)

        if locator is None:
            return False

        locator.click()
        locator.fill(title)

        return True

    def fill_description(self, description: str):

        locator = self._locator(self.DESCRIPTION_SELECTORS)

        if locator is None:
            return False

        locator.click()
        locator.fill(description)

        return True

    def apply_discounted_price(self, price):

        try:
            numeric_price = float(price)
        except Exception:
            return price

        discounted_price = round(numeric_price * 0.60, 2)

        print(f"Original price: {numeric_price}")
        print(f"Discounted price: {discounted_price}")

        return discounted_price

    def fill_price(self, price):

        locator = self._locator(self.PRICE_SELECTORS)

        if locator is None:
            return False

        discounted_price = self.apply_discounted_price(price)

        locator.click()
        locator.fill(str(discounted_price))

        return True

    def select_category(self, category_name: str):

        print(f"Selecting category: {category_name}")

        if not category_name:
            return False

        try:

            category_button = self._locator(self.CATEGORY_SELECTORS)

            if category_button is None:

                print("Category button not found.")
                self.page.screenshot(path="screenshots/debug_category_button_not_found.png")
                return False

            category_button.click()

            self.page.wait_for_timeout(2000)

            search_selectors = [
                'input[type="search"]',
                'input[placeholder*="search" i]',
                'input'
            ]

            search_input = self._locator(search_selectors)

            if search_input is None:

                print("Category search not found.")
                self.page.screenshot(path="screenshots/debug_category_search_not_found.png")
                return False

            search_input.fill(category_name)

            self.page.wait_for_timeout(3000)

            result_selectors = [
                '[role="option"]',
                '[data-testid*="option" i]',
                'li'
            ]

            first_result = self._locator(result_selectors)

            if first_result is None:

                print("Category results not found.")
                self.page.screenshot(path="screenshots/debug_category_results_not_found.png")
                return False

            first_result.click()

            self.page.wait_for_timeout(2000)

            print("Category selected.")

            return True

        except Exception as e:

            print("Category selection failed.")
            print(e)

            self.page.screenshot(path="screenshots/debug_category_failed.png")

            return False

    def _process_photos_from_image_paths(self, image_paths: list[str]) -> list[str]:
        """Process all images using the folder of the first source image."""

        if not self.process_photos:
            return image_paths

        if not image_paths:
            return image_paths

        item_folder = Path(image_paths[0]).parent

        print("Processing photos before upload...")

        processed = self.photo_agent.process_folder(item_folder)

        if processed:
            print("Using processed photos for upload.")
            return processed

        print("Photo processing returned no files; using originals.")
        return image_paths

    def create_draft(
        self,
        image_paths: list[str],
        listing: dict[str, Any]
    ):

        title = str(listing.get("title", "")).strip()
        description = str(listing.get("description", "")).strip()
        price = listing.get("price")
        category = str(listing.get("category", "")).strip()

        upload_paths = self._process_photos_from_image_paths(image_paths)

        self.ensure_logged_in()
        self.open_sell_page()
        self.upload_images(upload_paths)
        self.fill_title(title)
        self.select_category(category)
        self.fill_description(description)
        self.fill_price(price)

        print("Draft created.")

        return True, True
