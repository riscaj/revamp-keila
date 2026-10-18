import time

from src.pages.transactions.restrukturisasi import (
    pengajuan_restrukturisasi_locators as locators,
)


class PengajuanRestrukturisasiPage:
    def __init__(self, driver):
        self.driver = driver

    def click_visible_text(self, text, case_insensitive=False):
        while True:
            clicked = self.driver.execute_script(
                """
                const expected = arguments[0];
                const ignoreCase = arguments[1];
                const preferButton = arguments[2];
                const normalize = value => value.trim().replace(/\\s+/g, ' ');
                const matchesText = element => {
                    const actual = normalize(element.innerText || element.textContent || '');
                    return ignoreCase
                        ? actual.toLocaleLowerCase() === expected.toLocaleLowerCase()
                        : actual === expected;
                };
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                let candidates = [...document.querySelectorAll('body *')]
                    .filter(element => visible(element) && matchesText(element));
                if (preferButton) {
                    const buttons = [...document.querySelectorAll(
                        'button, [role="button"], input[type="button"], input[type="submit"]'
                    )].filter(element => visible(element) && matchesText(element));
                    if (buttons.length) candidates = buttons;
                } else {
                    const leaves = candidates.filter(element =>
                        ![...element.children].some(child => matchesText(child))
                    );
                    if (leaves.length) candidates = leaves;
                }
                candidates.sort((left, right) => {
                    const leftRect = left.getBoundingClientRect();
                    const rightRect = right.getBoundingClientRect();
                    return leftRect.width * leftRect.height - rightRect.width * rightRect.height;
                });
                const target = candidates[0];
                if (!target) return false;
                target.scrollIntoView({block: 'center', inline: 'center'});
                target.click();
                return true;
                """,
                text,
                case_insensitive,
                text == locators.PROCESS_BUTTON,
            )
            if clicked:
                return
            time.sleep(0.5)

    def click_button_by_text(self, text):
        while True:
            clicked = self.driver.execute_script(
                """
                const expected = arguments[0].trim().replace(/\\s+/g, ' ');
                const normalize = value => (value || '').trim().replace(/\\s+/g, ' ');
                const buttons = [...document.querySelectorAll(
                    'button, [role="button"], input[type="button"], input[type="submit"]'
                )];
                const target = buttons.find(element => {
                    const label = normalize(element.innerText || element.value || '');
                    const style = getComputedStyle(element);
                    return label === expected &&
                        element.getClientRects().length > 0 &&
                        style.visibility !== 'hidden' &&
                        style.display !== 'none' &&
                        !element.disabled &&
                        element.getAttribute('aria-disabled') !== 'true';
                });
                if (!target) return false;
                target.scrollIntoView({block: 'center', inline: 'center'});
                target.click();
                return true;
                """,
                text,
            )
            if clicked:
                return
            time.sleep(0.5)

    def choose_reason(self, reason):
        self.click_visible_text(locators.REASON_PLACEHOLDER)
        self.click_visible_text(reason)

    def choose_term(self, term):
        self.click_visible_text(locators.TERM_PLACEHOLDER)
        self.click_visible_text(term, case_insensitive=True)

    def confirm_and_finish(self):
        self.click_button_by_text(locators.PROCESS_BUTTON)
        self.click_button_by_text(locators.CONFIRM_BUTTON)
        self.click_button_by_text(locators.FINISH_BUTTON)
