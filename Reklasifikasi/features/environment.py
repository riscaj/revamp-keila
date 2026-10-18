from selenium import webdriver

from src.pages.transactions.reklasifikasi.pengajuan_kredit_bermasalah_page import (
    PengajuanKreditBermasalahPage,
)
from src.pages.transactions.reklasifikasi.reklasifikasi_page import (
    ReklasifikasiPage,
)
from src.pages.transactions.reklasifikasi.persetujuan_page import PersetujuanPage
from src.pages.transactions.reklasifikasi.realisasi_page import RealisasiPage
from src.pages.transactions.reklasifikasi.rekomendasi_page import RekomendasiPage


def before_scenario(context, scenario):
    if context.config.dry_run:
        return

    if "mbi" in scenario.effective_tags:
        from credentials import PASSWORD_MBI, USERNAME_MBI

        username = USERNAME_MBI
        password = PASSWORD_MBI
        credential_name = "MBI"
    elif "kadp" in scenario.effective_tags:
        from credentials import PASSWORD_KADP, USERNAME_KADP

        username = USERNAME_KADP
        password = PASSWORD_KADP
        credential_name = "KADP"
    elif "ksr" in scenario.effective_tags:
        from credentials import PASSWORD_KSR, USERNAME_KSR

        username = USERNAME_KSR
        password = PASSWORD_KSR
        credential_name = "KSR"
    else:
        from credentials import PASSWORD_AO, USERNAME_AO

        username = USERNAME_AO
        password = PASSWORD_AO
        credential_name = "AO"

    if not username or not password:
        raise RuntimeError(
            f"USERNAME_{credential_name} atau PASSWORD_{credential_name} "
            "belum diisi di credentials.py."
        )

    options = webdriver.ChromeOptions()
    options.page_load_strategy = "none"
    context.driver = webdriver.Chrome(options=options)
    context.username = username
    context.password = password
    context.reklasifikasi_page = ReklasifikasiPage(context.driver)
    context.pengajuan_kredit_bermasalah_page = PengajuanKreditBermasalahPage(
        context.driver
    )
    context.rekomendasi_page = RekomendasiPage(context.driver)
    context.verifikasi_page = RekomendasiPage(context.driver)
    context.persetujuan_page = PersetujuanPage(context.driver)
    context.realisasi_page = RealisasiPage(context.driver)


def after_scenario(context, scenario):
    driver = getattr(context, "driver", None)
    if driver is not None:
        driver.quit()
