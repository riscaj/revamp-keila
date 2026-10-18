import time

from src.pages.transactions.restrukturisasi.rekomendasi_page import (
    RekomendasiPage,
)


class PersetujuanPage(RekomendasiPage):
    def _review_section(self, section):
        if section.casefold() != "fasilitas kredit".casefold():
            super()._review_section(section)
            return

        time.sleep(3)
        self._click_button("Simpan")
        self._click_button("Ya, Simpan Data")
        self.wait.until(
            lambda driver: not self._find_visible_button_in(
                driver, "Ya, Simpan Data"
            ),
            "Modal konfirmasi Ya, Simpan Data tidak tertutup pada section "
            "Fasilitas kredit.",
        )
        self.wait.until(
            self._save_success_is_visible,
            "Notifikasi 'Data berhasil disimpan' tidak muncul pada section "
            "Fasilitas kredit.",
        )
        self._click_button("Selanjutnya")
