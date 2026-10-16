from selenium import webdriver

from src.pages.transactions.restrukturisasi.pengajuan_restrukturisasi_page import (
    PengajuanRestrukturisasiPage,
)
from src.pages.transactions.restrukturisasi.restrukturisasi_page import (
    RestrukturisasiPage,
)
from src.pages.transactions.restrukturisasi.survey_page import SurveyPage


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
    context.restrukturisasi_page = RestrukturisasiPage(context.driver)
    context.pengajuan_restrukturisasi_page = PengajuanRestrukturisasiPage(
        context.driver
    )
    context.survey_page = SurveyPage(context.driver)


def after_scenario(context, scenario):
    driver = getattr(context, "driver", None)
    if driver is not None:
        driver.quit()
