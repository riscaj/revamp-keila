from selenium import webdriver

from src.pages.transactions.monitoring.monitoring_page import MonitoringPage


def before_scenario(context, scenario):
    if context.config.dry_run:
        return

    from credentials import PASSWORD_AO, USERNAME_AO

    if not USERNAME_AO or not PASSWORD_AO:
        raise RuntimeError(
            "USERNAME_AO atau PASSWORD_AO belum diisi di credentials.py."
        )

    options = webdriver.ChromeOptions()
    options.page_load_strategy = "none"
    context.driver = webdriver.Chrome(options=options)
    context.username = USERNAME_AO
    context.password = PASSWORD_AO
    context.monitoring_page = MonitoringPage(context.driver)


def after_scenario(context, scenario):
    driver = getattr(context, "driver", None)
    if driver is not None:
        driver.quit()
