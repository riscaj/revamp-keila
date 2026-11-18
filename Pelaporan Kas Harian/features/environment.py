from selenium import webdriver

from src.pages.transactions.pelaporan_kas_harian.pelaporan_kas_harian_page import (
    PelaporanKasHarianPage,
)


def before_scenario(context, scenario):
    if context.config.dry_run:
        return

    from credentials import (
        PASSWORD_PELAPORAN_KAS_HARIAN,
        PASSWORD_PERSETUJUAN_KAS_HARIAN,
        USERNAME_PELAPORAN_KAS_HARIAN,
        USERNAME_PERSETUJUAN_KAS_HARIAN,
    )

    is_approval_scenario = "persetujuan_kas_harian" in scenario.tags
    if is_approval_scenario:
        username = USERNAME_PERSETUJUAN_KAS_HARIAN
        password = PASSWORD_PERSETUJUAN_KAS_HARIAN
        if not username or not password:
            raise RuntimeError(
                "Kredensial pemimpin cabang P82647 belum diisi di credentials.py."
            )
    else:
        username = USERNAME_PELAPORAN_KAS_HARIAN
        password = PASSWORD_PELAPORAN_KAS_HARIAN
        if not username or not password:
            raise RuntimeError(
                "Kredensial kasir P89967 belum diisi di credentials.py."
            )

    options = webdriver.ChromeOptions()
    options.page_load_strategy = "none"
    context.driver = webdriver.Chrome(options=options)
    context.username = username
    context.password = password
    if is_approval_scenario:
        from src.pages.transactions.pelaporan_kas_harian.persetujuan_kas_harian_page import (
            PersetujuanKasHarianPage,
        )

        context.persetujuan_kas_harian_page = PersetujuanKasHarianPage(
            context.driver
        )
    else:
        context.pelaporan_kas_harian_page = PelaporanKasHarianPage(
            context.driver
        )


def after_scenario(context, scenario):
    driver = getattr(context, "driver", None)
    if driver is not None:
        driver.quit()
