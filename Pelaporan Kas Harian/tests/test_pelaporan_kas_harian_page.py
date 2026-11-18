import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from features.steps.pelaporan_kas_harian.pelaporan_kas_harian_steps import (
    handle_daily_cash_and_bank_report,
)
from src.pages.transactions.pelaporan_kas_harian.pelaporan_kas_harian_page import (
    PelaporanKasHarianPage,
)


class PelaporanKasHarianPageTests(unittest.TestCase):
    def setUp(self):
        self.page = object.__new__(PelaporanKasHarianPage)
        self.page._visible_report_rows = Mock()
        self.page._find_row_action = Mock()
        self.page._find_exact_visible_text = Mock(side_effect=lambda text: text)
        self.page._click_centered = Mock()
        self.page._fill_first_row_sheet_count = Mock()
        self.page._scroll_to_page_bottom = Mock()

    def test_processes_first_unreported_row(self):
        row = SimpleNamespace(text="Status: Belum Dilaporkan")
        process_button = object()
        self.page._visible_report_rows.return_value = [row]
        self.page._find_row_action.return_value = process_button

        result = self.page.process_pending_or_add_report()

        self.assertEqual(result, "process")
        self.page._find_row_action.assert_called_once_with(row, "proses")
        self.assertEqual(
            self.page._click_centered.call_args_list,
            [
                call(process_button),
                call("Hitung"),
                call("Selanjutnya"),
            ],
        )
        self.page._fill_first_row_sheet_count.assert_called_once_with()
        self.page._scroll_to_page_bottom.assert_called_once_with()

    def test_retries_when_report_rows_rerender_during_status_read(self):
        row = SimpleNamespace(text="Status: Belum Dilaporkan")
        process_button = object()
        self.page._visible_report_rows.side_effect = [
            StaleElementReferenceException(),
            [row],
        ]
        self.page._find_row_action.return_value = process_button
        self.page._complete_cash_denominations = Mock()

        result = self.page.process_pending_or_add_report()

        self.assertEqual(result, "process")
        self.assertEqual(self.page._visible_report_rows.call_count, 2)
        self.page._find_row_action.assert_called_once_with(row, "proses")
        self.page._complete_cash_denominations.assert_called_once_with()

    def test_waits_until_visible_report_rows_have_status(self):
        status_cell = SimpleNamespace(text="")
        row = Mock()
        row.is_displayed.return_value = True
        row.find_elements.return_value = [status_cell]
        header = SimpleNamespace(text="Status")
        table = Mock()
        table.find_elements.return_value = [header]
        driver = Mock()
        driver.find_element.return_value = table
        driver.find_elements.return_value = [row]

        self.assertFalse(self.page._loaded_report_rows(driver))

        status_cell.text = "Belum Dilaporkan"
        self.assertEqual(self.page._loaded_report_rows(driver), [row])

    def test_adds_report_when_all_rows_are_approved(self):
        self.page._visible_report_rows.return_value = [
            SimpleNamespace(text="Disetujui"),
            SimpleNamespace(text="Telah Disetujui"),
        ]

        result = self.page.process_pending_or_add_report()

        self.assertEqual(result, "add_report")
        self.page._fill_first_row_sheet_count.assert_called_once_with()
        self.page._scroll_to_page_bottom.assert_called_once_with()
        self.assertEqual(
            self.page._click_centered.call_args_list,
            [
                call("Tambah Laporan"),
                call("Hitung"),
                call("Selanjutnya"),
            ],
        )

    def test_fails_when_rows_are_neither_pending_nor_all_approved(self):
        self.page._visible_report_rows.return_value = [
            SimpleNamespace(text="Dalam Proses"),
            SimpleNamespace(text="Disetujui"),
        ]

        with self.assertRaisesRegex(
            AssertionError,
            "belum berstatus Disetujui",
        ):
            self.page.process_pending_or_add_report()

        self.page._click_centered.assert_not_called()
        self.page._fill_first_row_sheet_count.assert_not_called()

    def test_completes_bank_report_after_adding_report(self):
        page = Mock()
        page.process_pending_or_add_report.return_value = "add_report"
        context = SimpleNamespace(pelaporan_kas_harian_page=page)

        handle_daily_cash_and_bank_report(context)

        page.complete_bank_balance_report.assert_called_once_with()
        self.assertEqual(context.report_action, "add_report")

    def test_completes_bank_report_after_processing_pending_report(self):
        page = Mock()
        page.process_pending_or_add_report.return_value = "process"
        context = SimpleNamespace(pelaporan_kas_harian_page=page)

        handle_daily_cash_and_bank_report(context)

        page.complete_bank_balance_report.assert_called_once_with()
        self.assertEqual(context.report_action, "process")

    def test_resolves_the_cms_bank_pdf_from_upload_folder(self):
        page = object.__new__(PelaporanKasHarianPage)

        pdf_path = page._cms_bank_pdf_path()

        self.assertEqual(pdf_path.parent.name, "Upload_CMS_Bank")
        self.assertEqual(pdf_path.suffix.casefold(), ".pdf")
        self.assertTrue(pdf_path.is_file())

    def test_checks_cms_bank_upload_by_filename(self):
        driver = Mock()
        driver.execute_script.return_value = True

        selected = PelaporanKasHarianPage._cms_bank_file_is_selected(
            driver,
            "Pdf test file.pdf",
        )

        self.assertTrue(selected)
        driver.execute_script.assert_called_once()
        self.assertEqual(
            driver.execute_script.call_args.args[1],
            "Pdf test file.pdf",
        )

    def test_completes_bank_balance_in_order(self):
        page = object.__new__(PelaporanKasHarianPage)
        page.ACTION_PAUSE_SECONDS = 0
        page.driver = Mock()
        page.wait = Mock()
        upload_path = Path("/tmp/cms-bank.pdf")
        upload_input = Mock()
        saldo_input = Mock()
        confirmation_button = Mock()
        understood_button = Mock()
        saldo_input.get_property.return_value = "0"
        page.wait.until.side_effect = [
            upload_input,
            True,
            saldo_input,
            True,
            confirmation_button,
            understood_button,
        ]
        page._cms_bank_pdf_path = Mock(return_value=upload_path)
        page._cms_bank_file_is_selected = Mock(return_value=True)
        page._scroll_to_page_bottom = Mock()
        page._find_exact_visible_text = Mock(side_effect=lambda text: text)
        page._click_centered = Mock()
        events = []
        page._click_centered.side_effect = lambda element: events.append(
            ("click", element)
        )

        with patch(
            "src.pages.transactions.pelaporan_kas_harian."
            "pelaporan_kas_harian_page.sleep",
            side_effect=lambda seconds: events.append(("sleep", seconds)),
        ) as sleep_mock:
            page.complete_bank_balance_report()

        upload_input.send_keys.assert_called_once_with(str(upload_path))
        upload_confirmation = page.wait.until.call_args_list[1].args[0]
        self.assertTrue(upload_confirmation(page.driver))
        page._cms_bank_file_is_selected.assert_called_once_with(
            page.driver,
            upload_path.name,
        )
        saldo_input.click.assert_called_once_with()
        saldo_input.clear.assert_called_once_with()
        self.assertEqual(
            saldo_input.send_keys.call_args_list,
            [call("0"), call(Keys.TAB)],
        )
        page._scroll_to_page_bottom.assert_called_once_with()
        self.assertEqual(
            page._click_centered.call_args_list,
            [
                call("Hitung"),
                call("Kirim Laporan"),
                call(confirmation_button),
                call(understood_button),
            ],
        )
        confirmation_wait = page.wait.until.call_args_list[4]
        confirmation_wait_driver = Mock()
        confirmation_wait_driver.find_element.return_value = confirmation_button
        confirmation_button.is_displayed.return_value = True
        confirmation_button.is_enabled.return_value = True
        self.assertIs(
            confirmation_wait.args[0](confirmation_wait_driver),
            confirmation_button,
        )
        confirmation_wait_driver.find_element.assert_called_once_with(
            By.XPATH,
            '//button[normalize-space(.)="Ya, Lanjutkan"]',
        )
        understood_wait = page.wait.until.call_args_list[5]
        understood_wait_driver = Mock()
        understood_wait_driver.find_element.return_value = understood_button
        understood_button.is_displayed.return_value = True
        understood_button.is_enabled.return_value = True
        self.assertIs(
            understood_wait.args[0](understood_wait_driver),
            understood_button,
        )
        understood_wait_driver.find_element.assert_called_once_with(
            By.XPATH,
            '//button[normalize-space(.)="Mengerti"]',
        )
        self.assertEqual(sleep_mock.call_args_list[-1], call(5))
        self.assertEqual(
            events[-2:],
            [("click", understood_button), ("sleep", 5)],
        )
        sleep_mock.assert_called_with(5)


if __name__ == "__main__":
    unittest.main()
