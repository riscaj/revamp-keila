import time

from credentials import PASSWORD, USERNAME
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchWindowException,
    StaleElementReferenceException,
)


LOGIN_URL = "https://exa-host-core-exa-dev.apps.ocp-dev.pegadaian.co.id/sign-in"
NOMOR_KREDIT = "13741260904108"
USERNAME_LOCATOR = (
    By.CSS_SELECTOR,
    'input[placeholder="Username HCMS / Aralia"], '
    'input[aria-label="Username HCMS / Aralia"]',
)
PASSWORD_LOCATOR = (
    By.CSS_SELECTOR,
    'input[placeholder="Password"], input[aria-label="Password"]',
)
SUBMIT_LOCATOR = (By.XPATH, '//button[normalize-space()="Masuk"]')
PUMK_SECTION_LOCATOR = (
    By.XPATH,
    "//*[normalize-space(.)='Pasca Kredit PUMK']",
)
SEE_ALL_LOCATOR = (By.ID, "btn_see_all_feature")
RESTRUCTURING_LOCATOR = (
    By.ID,
    "btn_dash_feature_PengajuanRestrukturisasiPUMK",
)
CREDIT_NUMBER_LOCATOR = (
    By.XPATH,
    "//input["
    "contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'nomor') "
    "or contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'kredit') "
    "or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'nomor') "
    "or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'kredit')"
    "]",
)
SEARCH_CREDIT_LOCATOR = (
    By.XPATH,
    "//button[normalize-space()='Cari Nomor Kredit' or normalize-space()='Cari']"
    " | //*[@role='button' and (normalize-space(.)='Cari Nomor Kredit' or normalize-space(.)='Cari')]",
)


def find_visible_and_enabled(locator):
    while True:
        try:
            for element in driver.find_elements(*locator):
                if element.is_displayed() and element.is_enabled():
                    return element
        except StaleElementReferenceException:
            time.sleep(0.2)
            continue
        time.sleep(0.5)


def wait_for_dashboard():
    while True:
        try:
            handles = driver.window_handles
        except NoSuchWindowException as error:
            raise RuntimeError(
                "Jendela Chrome tertutup sebelum dashboard ditemukan."
            ) from error
        if not handles:
            raise RuntimeError(
                "Semua jendela Chrome tertutup sebelum dashboard ditemukan."
            )

        for handle in handles:
            try:
                driver.switch_to.window(handle)
                for element in driver.find_elements(*PUMK_SECTION_LOCATOR):
                    if element.is_displayed() and element.is_enabled():
                        return element
            except (NoSuchWindowException, StaleElementReferenceException):
                continue
        time.sleep(1)


def click_centered(element):
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
        element,
    )
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", element)


def click_visible_text(text, case_insensitive=False):
    while True:
        clicked = driver.execute_script(
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
            text == "Proses Pengajuan",
        )
        if clicked:
            return
        time.sleep(0.5)


def click_process_application():
    while True:
        clicked = driver.execute_script(
            """
            const normalize = value => value.trim().replace(/\\s+/g, ' ');
            const buttons = [...document.querySelectorAll(
                'button, [role="button"], input[type="button"], input[type="submit"]'
            )];
            const target = buttons.find(element => {
                const text = normalize(element.innerText || element.value || '');
                const style = getComputedStyle(element);
                return text === 'Proses Pengajuan' &&
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
            """
        )
        if clicked:
            return
        time.sleep(0.5)


def click_button_by_text(text):
    while True:
        clicked = driver.execute_script(
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


def find_visible(locator):
    while True:
        try:
            for element in driver.find_elements(*locator):
                if element.is_displayed():
                    return element
        except StaleElementReferenceException:
            time.sleep(0.2)
            continue
        time.sleep(0.5)


def find_pumk_see_all():
    while True:
        try:
            button = driver.execute_script(
                """
                const visible = element =>
                    element.getClientRects().length > 0 &&
                    getComputedStyle(element).visibility !== 'hidden' &&
                    getComputedStyle(element).display !== 'none';
                const headings = [...document.querySelectorAll('body *')]
                    .filter(element =>
                        element.textContent.trim() === 'Pasca Kredit PUMK' &&
                        visible(element)
                    );
                for (const heading of headings) {
                    let parent = heading.parentElement;
                    while (parent && parent !== document.body) {
                        const buttons = [...parent.querySelectorAll(
                            '[id="btn_see_all_feature"]'
                        )].filter(visible);
                        if (buttons.length === 1) return buttons[0];
                        parent = parent.parentElement;
                    }
                }
                return null;
                """
            )
            if button is not None:
                return button
        except StaleElementReferenceException:
            pass
        time.sleep(0.5)


def fill_login():
    username_input = find_visible(USERNAME_LOCATOR)
    password_input = find_visible(PASSWORD_LOCATOR)
    submit_button = find_visible_and_enabled(SUBMIT_LOCATOR)

    username_input.clear()
    username_input.send_keys(USERNAME)
    password_input.clear()
    password_input.send_keys(PASSWORD)
    submit_button.click()
    return True


options = webdriver.ChromeOptions()
options.page_load_strategy = "none"
driver = webdriver.Chrome(options=options)

try:
    if not USERNAME or not PASSWORD:
        raise RuntimeError("USERNAME atau PASSWORD belum diisi di credentials.py.")

    driver.get(LOGIN_URL)
    if fill_login():
        pumk_section = wait_for_dashboard()
        driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);"
        )
        time.sleep(0.5)
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            pumk_section,
        )
        see_all = find_pumk_see_all()
        click_centered(see_all)
        print("Popup Pasca Kredit PUMK dibuka; memilih Pengajuan Restrukturisasi PUMK.")
        modal_item = find_visible_and_enabled(
            (By.ID, "btn_dash_feature_PengajuanRestrukturisasiPUMK")
        )
        click_centered(modal_item)
        print("Menu pengajuan terbuka; mencari kolom nomor kredit.")
        credit_number_input = find_visible(CREDIT_NUMBER_LOCATOR)
        while True:
            try:
                credit_number_input.clear()
                credit_number_input.send_keys(NOMOR_KREDIT)
                break
            except StaleElementReferenceException:
                credit_number_input = find_visible(CREDIT_NUMBER_LOCATOR)

        search_button = find_visible_and_enabled(SEARCH_CREDIT_LOCATOR)
        click_centered(search_button)
        print("Nomor kredit dicari; memilih alasan restrukturisasi.")
        click_visible_text("Pilih alasan restrukturisasi")
        click_visible_text("Dampak kondisi ekonomi")
        click_visible_text("Pilih jangka waktu")
        click_visible_text("12 Bulan", case_insensitive=True)
        print("Pilihan alasan dan jangka waktu sudah diisi; menekan Proses Pengajuan.")
        click_process_application()
        click_button_by_text("Ya, Proses Pengajuan")
        click_button_by_text("Selesai")
        print("Kembali ke Daftar sudah diklik. Browser ditutup dalam 5 detik.")
        time.sleep(5)
finally:
    driver.quit()
