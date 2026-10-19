from selenium.webdriver.common.by import By


LOGIN_URL = "https://exa-host-core-exa-dev.apps.ocp-dev.pegadaian.co.id/sign-in"
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
MONITORING_SECTION_TEXT = "Monitoring"
MONITORING_PROGRAM_TEXT = "Monitoring Program UMK"
CREDIT_TYPE_LABEL = "Jenis Kredit"
SEARCH_BUTTON_TEXT = "Cari"
DETAIL_BUTTON_TEXT = "Lihat Detail"
