import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from src.pages.transactions.pelaporan_kas_harian.persetujuan_kas_harian_page import (
    PersetujuanKasHarianPage,
)


class PersetujuanKasHarianPageTests(unittest.TestCase):
    def test_completes_both_checklists_and_submits_approval_confirmation(self):
        page = object.__new__(PersetujuanKasHarianPage)
        page.wait = Mock()
        page.driver = Mock()
        checkbox_one = Mock()
        checkbox_two = Mock()
        next_one = Mock()
        next_two = Mock()
        approval_radio = Mock()
        approval_radio.get_property.return_value = True
        note_input = Mock()
        note_input.get_property.return_value = (
            PersetujuanKasHarianPage.APPROVAL_NOTE
        )
        process_button = "Proses"
        approve_button = "Ya, Setujui"
        understood_button = Mock()
        page.wait.until.side_effect = [
            checkbox_one,
            next_one,
            True,
            checkbox_two,
            next_two,
            True,
            approval_radio,
            True,
            note_input,
            True,
            understood_button,
        ]
        page._click_centered = Mock()
        events = []
        page._click_centered.side_effect = lambda element: events.append(
            ("click", element)
        )
        page._find_exact_visible_text = Mock(
            side_effect=lambda text: text
        )

        with patch(
            "src.pages.transactions.pelaporan_kas_harian."
            "persetujuan_kas_harian_page.sleep",
            side_effect=lambda seconds: events.append(("sleep", seconds)),
        ) as sleep_mock:
            page._complete_approval_form()

        self.assertEqual(
            page._click_centered.call_args_list,
            [
                call(checkbox_one),
                call(next_one),
                call(checkbox_two),
                call(next_two),
                call(approval_radio),
                call(process_button),
                call(approve_button),
                call(understood_button),
            ],
        )
        note_input.clear.assert_called_once_with()
        note_input.send_keys.assert_called_once_with(
            "Pemimpin cabang telah menyetujui ini"
        )
        self.assertEqual(
            page._find_exact_visible_text.call_args_list,
            [call("Proses"), call("Ya, Setujui")],
        )
        self.assertEqual(page.wait.until.call_count, 11)
        self.assertEqual(sleep_mock.call_args_list, [call(5)])
        self.assertEqual(
            events[-2:],
            [("click", understood_button), ("sleep", 5)],
        )

    def test_counts_pending_reports_across_all_pages(self):
        page = object.__new__(PersetujuanKasHarianPage)
        page._approval_page_numbers = Mock(return_value=[1, 2])
        page._go_to_approval_page = Mock()
        page._visible_report_rows = Mock(
            side_effect=[
                [
                    SimpleNamespace(
                        text="Belum Dilaporkan - Menunggu Persetujuan"
                    )
                ],
                [
                    SimpleNamespace(text="Disetujui"),
                    SimpleNamespace(text="Menunggu Persetujuan"),
                ],
            ]
        )

        self.assertEqual(page._count_pending_reports_across_pages(), 2)
        self.assertEqual(
            page._go_to_approval_page.call_args_list,
            [call(1), call(2)],
        )


if __name__ == "__main__":
    unittest.main()
