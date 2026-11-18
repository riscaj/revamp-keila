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
PROGRAM_UMK_TEXT = "Program UMK"
FEATURE_LIST_BUTTON_ID = "btn_see_all_feature"
FEATURE_DIALOG_ID = "modal-see-all-feature-body"
REPORT_MENU_TEXT = "Pelaporan Harian Kas Dan Bank PUMK"
REPORT_PAGE_TITLE = "Pelaporan Harian Kas Dan Bank PUMK"
REPORT_TABLE_LOCATOR = (By.CSS_SELECTOR, 'table[aria-label="table data"]')
REPORT_ROWS_LOCATOR = (
    By.CSS_SELECTOR,
    'table[aria-label="table data"] tbody tr',
)
