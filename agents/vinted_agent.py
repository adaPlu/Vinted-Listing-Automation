from playwright.sync_api import sync_playwright

class VintedAgent:

    def __enter__(self):
        self.playwright = sync_playwright().start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.playwright.stop()

    def create_draft(self, image_paths, listing):
        print("Creating draft...")
        return True, True
