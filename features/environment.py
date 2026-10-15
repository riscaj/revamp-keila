from selenium import webdriver

from src.pages.transactions.restrukturisasi.pengajuan_restrukturisasi_page import (
    PengajuanRestrukturisasiPage,
)
from src.pages.transactions.restrukturisasi.restrukturisasi_page import (
    RestrukturisasiPage,
)


def before_scenario(context, scenario):
    if context.config.dry_run:
        return

    from credentials import PASSWORD, USERNAME

    if not USERNAME or not PASSWORD:
        raise RuntimeError("USERNAME atau PASSWORD belum diisi di credentials.py.")

    options = webdriver.ChromeOptions()
    options.page_load_strategy = "none"
    context.driver = webdriver.Chrome(options=options)
    context.username = USERNAME
    context.password = PASSWORD
    context.restrukturisasi_page = RestrukturisasiPage(context.driver)
    context.pengajuan_restrukturisasi_page = PengajuanRestrukturisasiPage(
        context.driver
    )


def after_scenario(context, scenario):
    driver = getattr(context, "driver", None)
    if driver is not None:
        driver.quit()
