from selenium import webdriver

from credentials import (
    PASSWORD_PERSETUJUAN_KAS_HARIAN,
    USERNAME_PERSETUJUAN_KAS_HARIAN,
)
from src.pages.transactions.pelaporan_kas_harian.persetujuan_kas_harian_page import (
    PersetujuanKasHarianPage,
)


def main():
    if not USERNAME_PERSETUJUAN_KAS_HARIAN or not PASSWORD_PERSETUJUAN_KAS_HARIAN:
        raise RuntimeError(
            "USERNAME_PERSETUJUAN_KAS_HARIAN atau "
            "PASSWORD_PERSETUJUAN_KAS_HARIAN belum diisi di "
            "credentials.py."
        )

    options = webdriver.ChromeOptions()
    options.page_load_strategy = "none"
    driver = webdriver.Chrome(options=options)
    try:
        page = PersetujuanKasHarianPage(driver)
        driver.get(page.login_url)
        page.fill_login(
            USERNAME_PERSETUJUAN_KAS_HARIAN,
            PASSWORD_PERSETUJUAN_KAS_HARIAN,
        )
        page.wait_for_dashboard()
        page.open_approval_menu()
        approved_count = page.approve_all_pending_reports()
        print(
            "Persetujuan selesai. "
            f"Jumlah laporan yang disetujui: {approved_count}."
        )
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
