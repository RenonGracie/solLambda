from time import sleep
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.items import ChromiumElement


class Web:
    __timeout = 20
    web: ChromiumPage

    def __init__(self):
        options = ChromiumOptions()

        options.auto_port()
        options.headless()
        options.set_argument("--no-sandbox")

        self.web = ChromiumPage(options)

    def get(self, url: str):
        self.web.get(url)

    def js(self, script: str, *args):
        return self.web.run_js(script, *args)

    def wait_for_element(self, path: str, seconds=__timeout):
        self.web.wait.eles_loaded(("xpath", path), seconds, True)

    def wait_for_element_display(self, path: str, seconds=__timeout):
        self.web.wait.ele_displayed(("xpath", path), seconds, True)

    def wait_for_element_not_display(self, path: str, seconds=__timeout):
        self.web.wait.ele_hidden(("xpath", path), seconds, True)

    def wait_for_element_deleted(self, path: str):
        self.web.wait.ele_hidden(("xpath", path), 10, True)

    def select_option(self, value: str, path: str):
        self.wait_for_element_display(path)
        self.web.ele(("xpath", path)).select(value)  # type: ignore
        sleep(1)

    def input_value(self, value: str, path: str, js=False):
        self.wait_for_element_display(path)
        self.web.ele(("xpath", path)).input(value, clear=True, by_js=js)
        sleep(1)

    def elements(self, path: str) -> list[ChromiumElement]:
        return self.web.eles(("xpath", path), 0)

    def element(self, path: str):
        return self.web.ele(("xpath", path), timeout=0)

    def click(self, path: str):
        self.wait_for_element_display(path)
        self.element(path).click()

    def quit(self):
        try:
            self.web.quit()
        except Exception:
            pass
