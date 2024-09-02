from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.models.Template import get_a, delete
from pathlib import Path
import os
import platform
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.helper import image_manipulator


class BrowserChangeAvatarEvent(InstagramMiddleware):
    base = None
    command = 0
    template = 0

    def execute(self):

        if self.ig.account.avatar_changed:
            return self.ig.account.add_cli(f"{self.ig.account.username}'s avatar has been changed already")

        self.template = self.ig.account.get_a_free_template('avatar')

        if not self.template:
            self.ig.account.add_cli(f"We don't have an avatar for : {self.ig.account.username}")

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem changing avatar : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000,4000)

    def get_avatar_path(self, template_path):

        project_path = Path(__file__).parent.parent.parent.parent.parent if platform.system() == 'Windows' else Path(
            __file__).parent.parent.parent.parent
        return os.path.join(project_path, 'backend', 'storage', 'app', 'public', template_path)

    def before_change_hook(self):

        self.base = BrowserBaseEvent(self.ig)
        self.ig.account.set_state('set avatar', 'app_state')
        self.command = self.ig.account.create_command('set avatar', 'processing')

    def change_hook(self):
        self.base.go_to_profile_page()
        self.ig.page.get_by_label(f"{self.ig.account.username} Instagram").click()
        self.ig.page.locator('a[aria-label="Profile picture"]').click()
        self.ig.pause(2000, 2500)

        avatar_path = self.get_avatar_path(self.template.text)
        self.ig.account.add_cli(
            f"We selected : {self.template.text} avatar for the : {self.ig.account.username}")

        self.ig.page.locator("input[accept='image/png,image/jpg,image/heif,image/heic']").nth(0).set_input_files(
            image_manipulator(avatar_path))
        self.ig.pause(4000, 5000)

        try:
            self.ig.page.locator(f"button[name='Save']").click()
        except:
            self.ig.page.locator('div[role="button"] span:text("Save")').first.click(force=True)

        self.ig.pause(10000, 12000)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('avatar_changed', 1)
        self.ig.account.attach_template(self.template)
        self.ig.account.add_cli("Avatar changed successfully")
