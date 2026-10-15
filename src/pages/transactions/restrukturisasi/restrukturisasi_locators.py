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
PUMK_SECTION_LOCATOR = (
    By.XPATH,
    "//*[normalize-space(.)='Pasca Kredit PUMK']",
)
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
