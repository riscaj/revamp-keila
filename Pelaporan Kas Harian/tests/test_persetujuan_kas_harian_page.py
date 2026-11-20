import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from features.steps.pelaporan_kas_harian.persetujuan.persetujuan_kas_harian_steps import (
    open_menu_and_approve_pending_daily_cash_reports,
)
from src.pages.transactions.pelaporan_kas_harian.persetujuan_kas_harian_page import (
    PersetujuanKasHarianPage,
)


class PersetujuanKasHarianPageTests(unittest.TestCase):
    def test_approval_workflow_finishes_in_menu_step(self):
        page = Mock()
        page.approve_one_pending_report.return_value = 1
        context = SimpleNamespace(persetujuan_kas_harian_page=page)

        open_menu_and_approve_pending_daily_cash_reports(context)

        page.open_approval_menu.assert_called_once_with()
        page.approve_one_pending_report.assert_called_once_with()
        self.assertEqual(context.approved_report_count, 1)

    def test_approves_only_first_pending_report_and_finishes_after_acknowledgement(self):
        page = object.__new__(PersetujuanKasHarianPage)
        pending_row = object()
        process_button = object()
        page._first_pending_report_across_pages = Mock(return_value=pending_row)
        page._find_row_action = Mock(return_value=process_button)
        page._click_centered = Mock()
        page._complete_approval_form = Mock()

        result = page.approve_one_pending_report()

        self.assertEqual(result, 1)
        page._first_pending_report_across_pages.assert_called_once_with()
        page._click_centered.assert_called_once_with(process_button)
        page._complete_approval_form.assert_called_once_with()

    def test_returns_zero_when_no_pending_report_exists(self):
        page = object.__new__(PersetujuanKasHarianPage)
        page._first_pending_report_across_pages = Mock(return_value=None)
        page._click_centered = Mock()

        result = page.approve_one_pending_report()

        self.assertEqual(result, 0)
        page._click_centered.assert_not_called()

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
            ("element", understood_button),
            True,
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
            "pelaporan_kas_harian_page.sleep",
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
        self.assertEqual(page.wait.until.call_count, 12)
        self.assertEqual(sleep_mock.call_args_list, [call(5)])
        self.assertEqual(
            events[-2:],
            [("click", understood_button), ("sleep", 5)],
        )

    def test_stops_searching_after_first_pending_report_is_found(self):
        page = object.__new__(PersetujuanKasHarianPage)
        page._approval_page_numbers = Mock(return_value=[1, 2])
        page._go_to_approval_page = Mock()
        pending_row = SimpleNamespace(text="Menunggu Persetujuan")
        page._visible_report_rows = Mock(
            return_value=[SimpleNamespace(text="Disetujui"), pending_row]
        )

        self.assertIs(page._first_pending_report_across_pages(), pending_row)
        page._go_to_approval_page.assert_called_once_with(1)
        page._visible_report_rows.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
