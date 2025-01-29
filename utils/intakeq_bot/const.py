import os, sys
import string


_lowercase_text = f"translate(normalize-space(),'{string.ascii_uppercase}','{string.ascii_lowercase}')"


def _lowercase_attr(value: str):
    return f"translate(@{value},'{string.ascii_uppercase}','{string.ascii_lowercase}')"


_curr_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.getcwd()


def curr_dir(*paths: str):
    return os.path.join(_curr_dir, *paths)


class Xpath:

    class Input:
        @staticmethod
        def id(id: str):
            return f"//*[@id='{id}']"

        @staticmethod
        def label_complete(text: str):
            return f"//label[./span[{_lowercase_text} = '{text.lower().strip()}']]"

        @staticmethod
        def label(text: str):
            return f"//label[./span[contains({_lowercase_text},'{text.lower().strip()}')]]"

        @staticmethod
        def table_radio(value: str, idx: int):
            return f"//tbody/tr[{idx}]/td[contains({_lowercase_attr('title')},'{value.lower()}')]/label"

        @staticmethod
        def sibling(value: str):
            return f"//label[contains(text(),'{value}')]/following-sibling::input"

        graduation_year = "//input[@ng-model='question.Answer']"
        therapy_time = "//textarea[@ng-model='question.Answer']"
        state = "//select"
        referred_by_someone = "//textarea[@ng-model='question.FurtherExplanation']"
        promo_code = "//input[@ng-model='question.Answer']"

        tc = "//*[@id='mdqa']/label"

    class Button:
        submit = "//*[@type='submit']"
        next_page = "//*[@id='next-page']"

        submit_form = "//button[@id='btnSubmit']"

        sign_out = "//button[contains(text(),'Sign Out')]"
