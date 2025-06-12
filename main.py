from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class InvalidCorrectOption(Exception):
    pass

class LoginError(Exception):
    pass

class InvalidFileFormat(Exception):
    pass

class Question:
    def __init__(self, title):
        self.title = title

class TrueOrFalseOpts(Question):
    def __init__(self, title, correct_option):
        self.type = "TOF"
        if correct_option > 1 or correct_option < 0:
            raise InvalidCorrectOption("Options in true or false have to either 0 (true) or 1 (false)")
        self.opt = correct_option
        super().__init__(title)

class MultipleOption(Question):
    def __init__(self, title, correct_options: list[int], option0, option1, option2, option3):
        correct_options = set(correct_options)
        self.type = "MO"
        self.option0 = option0
        self.option1 = option1
        self.option2 = option2
        self.option3 = option3
        if len(correct_options) > 4 or len(correct_options) < 1:
            raise InvalidCorrectOption("The max amount of correct options is 4 and the minimun is 1")
        for cor_opt in correct_options:
            if cor_opt > 3 or cor_opt < 0:
                raise InvalidCorrectOption("Options in multiple option have to be from 0 to 3")
        self.opt = correct_options
        super().__init__(title)

class KahootCreator:
    def __init__(self, headless = False):
        """
        Creates a kahoot creator class. continue with kc.login().
        Args:
            headless (bool): Shows you the browser window if false, else does it hidden.
        """
        self.headless = headless
    def login(self, user, password, wait_for_login_confirm = 15):
        """
        Brings you to the Kahoot creator page, ready to continue with kc.create_kahoot.
        Args:
            user (str): Username to log in with.
            password (str): Password to log in with.
            wait_for_login_confirm (int): Login confirmation timeout to find a 'settings' button
                that verifies login if it exists. Defaults to 15.
        Raises:
            LoginError: If login failed (didn't find settings button in time).
        """
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--start-maximized")
        options.add_argument("--lang=en-US")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)
        self.driver = driver
        driver.get("https://kahoot.com/")
        time.sleep(2)
        self._cookies_banner()
        time.sleep(1.5)
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
        )
        button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h1.card__WideCardTitle-sc-1rk0phi-2.inltmI")
            )
        )
        time.sleep(1.2)
        user_input = driver.find_element(By.ID, "username")
        pass_input = driver.find_element(By.ID, "password")
        user_input.send_keys(user)
        time.sleep(1.2)
        pass_input.send_keys(password)
        self._cookies_banner()
        login_button = driver.find_element(By.ID, "login-submit-btn")
        login_button.click()
        try:
            settings_button = WebDriverWait(driver, wait_for_login_confirm).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-functional-selector="top-bar__settings-button"]'))
            )
            print("Settings found, login successful.")
            self._on_login_success()
        except:
            print(f"Settings not found within {wait_for_login_confirm} seconds.")
            if driver.current_url == "https://create.kahoot.it/discover":
                self._on_login_success()
            raise LoginError("No setting button found")
    def _on_login_success(self):
        driver = self.driver
        driver.get("https://create.kahoot.it/creator")
        try:
            create_kahoot = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button.button__Button-sc-c6mvr2-0.gouxOk.blank-template-card__CreateButton-sc-160pecy-5.iSpa-dW')
                )
            )
            create_kahoot.click()
        except:
            print("Didnt find a create kahoot button")
    def _enter_create_question_menu(self):
        button = self.driver.find_element(By.CSS_SELECTOR, '[data-functional-selector="add-question-button"]')
        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-functional-selector="teacher-dialog__close-button"]')
            close_button.click()
        except:
            pass
        button.click()
        print("Clicked select question menu")
    def _write_question_title(self, title):
        title_div = self.driver.find_element(By.CLASS_NAME, "styles__ContentEditable-sc-q5rqnn-2")
        title_div.click()
        title_div.send_keys(title)
    def select_question(self, question_index):
        if question_index != 0:
            question_index += 1
        try:
            question_div = self.driver.find_element(By.CSS_SELECTOR, f'[data-functional-selector="sidebar-block__kahoot-block-{question_index}"]')
            question_div.click()
        except:
            print("Failed clicking div element of question index " + str(question_index))
    def get_question_indexes(self, max = 100):
        indexes = []
        for i in range(max + 1):
            try:
                question_div = self.driver.find_element(By.CSS_SELECTOR, f'[data-functional-selector="sidebar-block__kahoot-block-{i}"]')
                if question_div:
                    indexes.append(i)
            except:
                pass
        return indexes
    def delete_question(self, question_index, timeout=10):
        self.select_question(question_index)
        delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-functional-selector="sidebar__remove"]')
        if delete_buttons:
            try:
                button = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(delete_buttons[question_index])
                )
                print(f"deleting button index {question_index} and length is {len(delete_buttons)}")
                button.click()
                confirm_delete = self.driver.find_element("css selector", 'button[data-functional-selector="dialog-confirm-delete-question__accept-button"]')
                confirm_delete.click()
            except:
                print(f"Button at index {question_index} is not clickable after {timeout} seconds.")
    def get_current_question_count(self):
        delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-functional-selector="sidebar__remove"]')
        if not delete_buttons:
            return 0
        return len(delete_buttons)
    def create_question(self, question_opts):
        """
        Reminder: the multiple questions order is top left = 0, bottom left = 2, top right = 1 and bottom right = 3.
        """
        self._enter_create_question_menu()
        time.sleep(1)
        if isinstance(question_opts, TrueOrFalseOpts):
            title = question_opts.title
            choice = question_opts.opt
            print("Creating true or false")
            try:
                button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-functional-selector="create-button__true-false"]'))
                )
                button.click()
            except StaleElementReferenceException:
                button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-functional-selector="create-button__true-false"]'))
                )
                button.click()
            self._write_question_title(title)
            if choice == 1:
                self._click_false()
            else:
                self._click_true()
        elif isinstance(question_opts, MultipleOption):
            title = question_opts.title
            choices = question_opts.opt
            print("Creating multiple choice")
            time.sleep(1)
            button = self.driver.find_element(By.CSS_SELECTOR, '[data-functional-selector="create-button__quiz"]')
            button.click()
            self._write_question_title(title)
            self._slide_button()
            for i in range(0, 4):
                question_i = getattr(question_opts, "option" + str(i))
                editable_div = self.driver.find_element(By.ID, "question-choice-" + str(i))
                editable_div.click()
                editable_div.send_keys(question_i)
            for i in choices:
                if i == 0:
                    set_correct_button = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'button.icon-button__IconButton-sc-12q2f5v-0[data-onboarding-step]'
                    )
                    set_correct_button.click()
                    continue
                set_correct_button = self.driver.find_element(By.XPATH, f'//button[@data-onboarding-step="{i}"]')
                set_correct_button.click()
    def _click_false(self):
        button = self.driver.find_element("id", "1")
        self.driver.execute_script("arguments[0].click();", button)
    def _click_true(self):
        button = self.driver.find_element("css selector", "button.selected-tick__CheckIcon-sc-119fb5m-0")
        self.driver.execute_script("arguments[0].click();", button)
    def _slide_button(self):
        try:
            button = self.driver.find_element(By.CLASS_NAME, 'fZkuwo')
            button.click()
        except:
            pass
    def save(self, title, description = None):
        time.sleep(5)
        save_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-functional-selector="top-bar__save-button"]')
        save_button.click()
        title_input = self.driver.find_element(By.ID, "kahoot-title")
        title_input.send_keys(title)
        description_input = self.driver.find_element(By.ID, "description")
        if description:
            description_input.send_keys(description)
        continue_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-functional-selector="dialog-add-title__continue"]')
        continue_button.click()
        time.sleep(1.5)
        done_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-functional-selector="dialog-complete-kahoot__finish-button"]')
        done_button.click()
    def add_media(self, image_path, extra_wait = 0):
        if not self._is_format_acceptable(image_path):
            raise InvalidFileFormat(f"This file format isnt accepted by kahoot. Accepted formats: {', '.join(["jpeg", "jpg", "png", "gif", "webp"])}.")
        time.sleep(extra_wait)
        image_path = os.path.abspath(image_path)
        if not os.path.exists(image_path):
            raise FileNotFoundError("File wasnt found.")
        add_button = self.driver.find_element(By.CSS_SELECTOR, '[data-functional-selector="media-library-info-view__add-media-button"]')
        add_button.click()
        time.sleep(1)
        upload_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-functional-selector='open-upload-media-dialog-button']")))
        upload_button.click()
        time.sleep(2)
        file_input = self.driver.find_element(By.ID, "media-upload")
        file_input.send_keys(image_path)
    def _is_format_acceptable(self, path: str):
        good_formats = set(["jpeg", "jpg", "png", "gif", "webp"])
        split = path.split(".")
        frmat = split[len(split) - 1]
        if frmat in good_formats:
            return True
        return False
    def _cookies_banner(self):
        try:
            accept_cookies = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_cookies.click()
        except:
            print("No cookie banner appeared.")
