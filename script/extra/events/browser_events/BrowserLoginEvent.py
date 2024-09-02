from time import sleep
from script.extra.exceptions import ChangePasswordError, LoginAppearedAgainError, MultipleSomethingWentWrongError, \
    EnterYourEmailError, AddAPhoneNumberError, ConfirmYouOwnThisAccount
from script.extra.helper import generate_password
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware

import random
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.models.Command import performed_command_count


class BrowserLoginEvent(InstagramMiddleware):
    for_test = False

    def set_for_test(self):
        self.for_test = True
        return self

    def execute(self):
        self.go_to_instagram()
        self.login()

    def go_to_instagram(self):
        self.ig.account.add_cli('Going to Instagram page ...')
        retries = 3
        for attempt in range(retries):
            try:
                self.ig.page.goto('https://www.instagram.com/', timeout=200000)
                break
            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                sleep(2)

        if self.for_test:
            return

        self.ig.account.add_cli('After Instagram loaded and before timeout')
        self.ig.pause(4000, 6000)
        self.ig.account.add_cli('After 4000-6000 timeout')
        self.ig.allow_cookies()
        self.ig.account.add_cli('After allowing cookies')
        self.ig.pause(4000, 6000)
        self.ig.suspect_automate_behavior_handler()
        return self

    def login(self):
        self.pre_login_hook()

        if self.is_not_logged_in():
            self.ig.account.add_cli('User is not logged in before trying to login ...')
            self.fill_username_password()

            self.ig.account.add_cli('after user login ...')
            self.after_filling_username_password_hook()
            self.something_went_wrong_handler()

        # self.handle_2f_authentication()

        self.after_login_hook()
        self.change_password_handler()
        self.ig.allow_cookies()

        self.ig.pause(3000, 4000)
        self.ig.save_info()
        self.ig.pause(3000, 4000)
        self.ig.turn_on_notif()
        self.ig.save_session()
        self.ig.pause(4000, 5000)

        self.follow_suggested()

    def pre_login_hook(self):

        self.ig.account.add_cli(f'Checking for both Enter you mobile or Continue as message ...')

        for i in range(6):

            if self.ig.is_visible_by_text('Enter your mobile number'):
                self.ig.account.set_state('challenging', 'instagram_state', 'Enter your mobile number')
                self.ig.handle_exception('Enter you mobile is visible')

            if self.ig.is_visible_by_text('Continue as'):
                self.ig.account.add_cli('Continue as is visible, Clicking on it')
                try:
                    self.ig.page.locator('//button[span[contains(text(), "Continue as")]]').click()
                except:
                    self.ig.page.locator('.//span[contains(text(), "Continue as")]]').click()
                break

            self.ig.page.wait_for_timeout(1000)

    def is_not_logged_in(self):
        return self.ig.is_visible_by_text('Phone number, username, or email') or self.ig.is_visible_by_text(
            "Don't have an account")

    def enter_your_email(self):
        return self.ig.is_visible_by_text('Enter your email') or self.ig.is_visible_by_text(
            "We’ll send a confirmation code to this email")

    def confirm_you_own_this_account(self):
        return self.ig.is_visible_by_text('confirm that you own this account') or self.ig.is_visible_by_text(
            "You'll need to verify your identity")

    def add_a_phone_number(self):
        return self.ig.is_visible_by_text(
            'Add a phone number to get back into Instagram') or self.ig.is_visible_by_text(
            "We will send a confirmation code via SMS to your phone")

    def fill_username_password(self):

        input1 = self.ig.page.get_by_label("Phone number, username, or email")
        input2 = self.ig.page.get_by_label("Phone number, username or email address")

        try:
            input1.press_sequentially(self.ig.account.username, delay=100, timeout=4500)
        except:
            input2.press_sequentially(self.ig.account.username, delay=100)

        self.ig.pause(1800, 3000)
        self.ig.page.get_by_label("Password").press_sequentially(self.ig.account.password, delay=100)
        self.ig.pause(2000, 3000)
        self.ig.page.get_by_role("button", name="Log in", exact=True).click()

        return self

    def need_2f_authentication(self):

        is_visible = self.ig.is_visible_by_text('Enter the 6-digit code generated by') or self.ig.is_visible_by_text(
            "If you're unable to receive a login code from an authentication app")

        self.ig.account.add_cli('2fa is visible') if is_visible else self.ig.account.add_cli('2fa is not visible')

        return is_visible

    def after_filling_username_password_hook(self):
        for i in range(15):
            self.ig.account.add_cli(f'Checking for 2f authentication for the {i} time ...')
            if self.need_2f_authentication():
                self.ig.two_factor_authentication_process()
                return

            self.ig.not_connect_to_the_internet()
            self.ig.password_is_incorrect_handler()
            self.ig.problem_logging_in_handler()

            self.ig.page.wait_for_timeout(1100)

    def something_went_wrong_handler(self):
        for i in range(8):
            self.ig.account.add_cli(f'Checking Something went wrong for the {i} time ...')
            if self.ig.something_went_wrong():
                self.ig.pause(3000, 4000)
                if self.ig.something_went_wrong():
                    self.ig.pause(3000, 4000)
                    if self.ig.something_went_wrong():
                        raise MultipleSomethingWentWrongError('Multiple something went wrong appeared')

                return
            self.ig.page.wait_for_timeout(1100)

    def after_login_hook(self):
        self.ig.account.add_cli('Processing after login event ...')

        for i in range(8):

            if self.is_not_logged_in():
                raise LoginAppearedAgainError('Login page appeared again')

            if self.ig.unusual_login_detected():
                self.ig.pause(5000, 6000)
                return

            self.ig.suspended_account_handler()

            if self.ig.suspect_automate_behavior_handler():
                self.ig.pause(3000, 4000)
                return

            if self.enter_your_email():
                raise EnterYourEmailError('Enter your email address')

            if self.add_a_phone_number():
                raise AddAPhoneNumberError('Add a phone number to get back into Instagram')

            if self.confirm_you_own_this_account():
                raise ConfirmYouOwnThisAccount('Help us confirm that you own this account')

            self.ig.help_us_confirm_its_you_handler()
            self.please_log_in_to_continue()

            self.ig.page.wait_for_timeout(1100)

    def change_password_handler(self):

        if self.ig.is_visible_by_text('Change your password to secure your account') or self.ig.is_visible_by_text(
                'Someone may have your password') or self.ig.is_visible_by_text(
            'Change Your Password to Secure Your Account'):

            self.ig.account.add_cli("Change password page appeared")

            try:
                repeat_password_input = self.ig.page.get_by_label("New password confirmation")
                password = generate_password()

                self.ig.page.get_by_label("New password", exact=True).press_sequentially(password, delay=100,
                                                                                         timeout=3000)
                self.ig.pause(1800, 3000)

                try:
                    self.ig.page.get_by_label("New password confirmation").press_sequentially(password, delay=100,
                                                                                              timeout=3000)
                except:
                    self.ig.page.get_by_label("Confirm new password").press_sequentially(password, delay=100,
                                                                                         timeout=3000)

                self.ig.pause(2000, 3000)
                self.ig.page.get_by_role("button", name="Next", exact=True).click()
                self.ig.account.set('password', password)
                self.ig.account.add_cli("Password changed successfully")
                self.ig.pause(6000, 8000)

            except Exception as e:
                raise ChangePasswordError(str(e))

        if self.ig.is_visible_by_text('Your account was compromised') or self.ig.is_visible_by_text(
                'you shared your password with a service'):

            self.ig.page.get_by_role("button", name="Change Password", exact=True).click()
            self.ig.pause(1800, 3000)

            try:
                old_password = self.ig.page.get_by_label("Old password")
                password = generate_password()

                old_password.press_sequentially(self.ig.account.password, delay=100, timeout=3000)
                self.ig.pause(1800, 3000)

                self.ig.page.fill('input[name="new_password1"]', password)
                self.ig.pause(1800, 3000)
                self.ig.page.fill('input[name="new_password2"]', password)

                self.ig.pause(2000, 3000)
                self.ig.page.get_by_role("button", name="Change Password", exact=True).click()
                self.ig.account.set('password', password)
                self.ig.pause(6000, 8000)
                self.ig.account.add_cli("Password changed successfully")

            except Exception as e:
                raise ChangePasswordError(str(e))

    def please_log_in_to_continue(self):
        #         Please log in to continue.
        if self.ig.is_visible_by_text('Please log in to continue'):
            self.ig.page.get_by_role("button", name="Log in").click()

    def follow_suggested(self):
        allowed_follows = random.randint(1, SettingAdapter.max_follow())
        command_count = performed_command_count(self.ig.account, ['follow'], 24)

        self.ig.account.add_cli(f"performed follow :{command_count}, and allowed : {allowed_follows}")

        if command_count > allowed_follows:
            self.ig.account.add_cli(f"We are allowed to follow")
            return False

        if self.ig.is_visible_by_text('Suggested for you'):
            random_follow_number = random.randint(2, 4)
            follow_buttons = self.ig.page.query_selector_all('button:has-text("Follow")')
            selected_follow_button = random.sample(follow_buttons, random_follow_number)
            count = 0

            for button in selected_follow_button:
                count += 1
                self.ig.account.add_cli(f"Following suggested user for time : {count}")

                command = self.ig.account.create_command('follow', 'processing')
                try:
                    # Generate a random number between 1 and 5
                    button.click()
                    command.update_cmd('state', 'success')
                    self.ig.account.add_cli("Lead followed successfully")

                except Exception as e:
                    self.ig.account.add_cli(f"Failed to send DM : {str(e)}")
                    command.update_cmd('state', 'fail')
                # Optional: Wait a bit between clicks to mimic human behavior and avoid rate limits
                self.ig.pause(2000, 3500)  # Wait for 1 second0
