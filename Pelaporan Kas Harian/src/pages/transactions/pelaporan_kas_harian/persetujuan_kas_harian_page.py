from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.pages.transactions.pelaporan_kas_harian import (
    pelaporan_kas_harian_locators as locators,
)
from src.pages.transactions.pelaporan_kas_harian.pelaporan_kas_harian_page import (
    PelaporanKasHarianPage,
)


class PersetujuanKasHarianPage(PelaporanKasHarianPage):
    APPROVAL_MENU_TEXT = "Persetujuan Laporan Harian Kas Dan Bank PUMK"
    APPROVAL_NOTE = "Pemimpin cabang telah menyetujui ini"
    PENDING_STATUS = "menunggu persetujuan"

    def open_approval_menu(self):
        self.wait.until(
            lambda _driver: self._scroll_to_program_umk(),
            "Bagian Program UMK tidak ditemukan setelah login.",
        )
        menu_item = self._find_exact_visible_text(self.APPROVAL_MENU_TEXT)
        self._click_centered(menu_item)
        self._visible_report_rows()

    def approve_all_pending_reports(self):
        approved_count = 0
        while True:
            pending_count = self._count_pending_reports_across_pages()
            if pending_count == 0:
                return approved_count

            pending_row = self._first_pending_report_across_pages()
            if pending_row is None:
                raise AssertionError(
                    "Jumlah laporan Menunggu Persetujuan berubah saat daftar "
                    "dibaca; tidak ada laporan yang dapat diproses."
                )

            self._click_centered(self._find_row_action(pending_row, "proses"))
            self._complete_approval_form()
            self._wait_for_approval_list()

            remaining_count = self._count_pending_reports_across_pages()
            if remaining_count != pending_count - 1:
                raise AssertionError(
                    "Persetujuan tidak mengurangi jumlah laporan Menunggu "
                    "Persetujuan tepat satu; "
                    f"sebelum: {pending_count}, sesudah: {remaining_count}."
                )
            approved_count += 1

    def _complete_approval_form(self):
        self._confirm_review_step("Pelaporan Denominasi Bank")
        self._confirm_review_step("Keputusan Persetujuan")

        approval_radio = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'input[type="radio"][name="keputusan_persetujuan"]'
                    '[value="APPROVED"]',
                )
            ),
            "Pilihan Setujui tidak ditemukan pada halaman Keputusan Persetujuan.",
        )
        self._click_centered(approval_radio)
        self.wait.until(
            lambda _driver: approval_radio.get_property("checked"),
            "Pilihan Setujui belum terpilih.",
        )

        note_input = self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'textarea[placeholder="Masukkan catatan"]')
            ),
            "Field Catatan tidak ditemukan pada halaman Keputusan Persetujuan.",
        )
        note_input.clear()
        note_input.send_keys(self.APPROVAL_NOTE)
        self.wait.until(
            lambda _driver: note_input.get_property("value")
            == self.APPROVAL_NOTE,
            "Catatan persetujuan belum terisi dengan benar.",
        )

        self._click_centered(self._find_exact_visible_text("Proses"))
        approval_confirmation = self._find_exact_visible_text("Ya, Setujui")
        self._click_centered(approval_confirmation)
        understood_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[normalize-space(.)="Mengerti"]')
            ),
            "Tombol 'Mengerti' tidak muncul setelah persetujuan.",
        )
        self._click_centered(understood_button)
        sleep(5)

    def _confirm_review_step(self, next_heading):
        review_checkbox = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//label[normalize-space(.)="Saya telah memeriksa data ini."]',
                )
            ),
            "Checkbox 'Saya telah memeriksa data ini' tidak ditemukan.",
        )
        self._click_centered(review_checkbox)

        next_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[normalize-space(.)="Selanjutnya"]')
            ),
            "Tombol Selanjutnya belum aktif setelah checklist diperiksa.",
        )
        self._click_centered(next_button)
        self.wait.until(
            lambda driver: driver.execute_script(
                """
                const normalize = value =>
                    (value || '').trim().replace(/\\s+/g, ' ');
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).display !== 'none' &&
                    getComputedStyle(element).visibility !== 'hidden';
                return [...document.querySelectorAll(
                    'h1, h2, h3, h4, [role="heading"]'
                )].some(element =>
                    visible(element) &&
                    normalize(element.innerText) === arguments[0]
                );
                """,
                next_heading,
            ),
            f"Halaman {next_heading} tidak terbuka setelah memilih Selanjutnya.",
        )

    def _wait_for_approval_list(self):
        self.wait.until(
            lambda driver: (
                "page=process" not in driver.current_url
                and bool(
                    driver.find_elements(*locators.REPORT_TABLE_LOCATOR)
                )
            ),
            "Daftar persetujuan tidak terbuka kembali setelah konfirmasi.",
        )
        self._visible_report_rows()

    def _count_pending_reports_across_pages(self):
        total = 0
        for page_number in self._approval_page_numbers():
            self._go_to_approval_page(page_number)
            total += sum(
                self.PENDING_STATUS in self._normalized_text(row.text)
                for row in self._visible_report_rows()
            )
        return total

    def _first_pending_report_across_pages(self):
        for page_number in self._approval_page_numbers():
            self._go_to_approval_page(page_number)
            for row in self._visible_report_rows():
                if self.PENDING_STATUS in self._normalized_text(row.text):
                    return row
        return None

    def _approval_page_numbers(self):
        return self.wait.until(
            lambda driver: driver.execute_script(
                """
                const nav = document.querySelector(
                    'nav[aria-label="Pagination"]'
                );
                if (!nav) return [1];
                return [...nav.querySelectorAll(
                    'li.page-item span.page-link'
                )]
                    .map(element => (element.innerText || '').trim())
                    .filter(text => /^\\d+$/.test(text))
                    .map(Number);
                """
            ),
            "Navigasi halaman daftar persetujuan tidak ditemukan.",
        )

    def _go_to_approval_page(self, page_number):
        current_page = self.driver.execute_script(
            """
            const active = document.querySelector(
                'nav[aria-label="Pagination"] li.page-item.active span.page-link'
            );
            return active ? Number((active.innerText || '').trim()) : 1;
            """
        )
        if current_page == page_number:
            return

        page_link = self.wait.until(
            lambda driver: driver.execute_script(
                """
                const nav = document.querySelector(
                    'nav[aria-label="Pagination"]'
                );
                if (!nav) return false;
                return [...nav.querySelectorAll(
                    'li.page-item span.page-link'
                )].find(element =>
                    (element.innerText || '').trim() ===
                    String(arguments[0])
                ) || false;
                """,
                page_number,
            ),
            f"Halaman persetujuan {page_number} tidak ditemukan.",
        )
        self._click_centered(page_link)
        self.wait.until(
            lambda driver: driver.execute_script(
                """
                const active = document.querySelector(
                    'nav[aria-label="Pagination"] '
                    + 'li.page-item.active span.page-link'
                );
                return active &&
                    (active.innerText || '').trim() === String(arguments[0]);
                """,
                page_number,
            ),
            f"Daftar persetujuan tidak berpindah ke halaman {page_number}.",
        )
