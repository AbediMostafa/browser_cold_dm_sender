from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
import random


class BrowserScrollAndLikeEvent(InstagramMiddleware):

    def execute(self):
        self.go_to_home()
        self.scroll_and_like()

    def go_to_home(self):
        self.ig.account.add_cli('Going to home page ...')
        retries = 3
        for attempt in range(retries):
            try:
                try:
                    self.ig.page.get_by_role("link", name="Home Home").click(timeout=3000)
                except:
                    self.ig.page.get_by_role("link", name="Home").click()
                break

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                sleep(2)
        self.ig.pause(4000, 6000)
        return self

    def scroll_and_like(self):

        for i in range(random.randint(8, 14)):
            self.ig.account.add_cli(f'Scroll down for the {i} time ...')
            self.ig.page.mouse.wheel(0, random.randint(450, 650))
            self.ig.pause(2000, 4000)

