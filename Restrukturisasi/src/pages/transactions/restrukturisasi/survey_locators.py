from selenium.webdriver.common.by import By


SURVEY_ROWS = (
    By.CSS_SELECTOR,
    "table tbody tr",
)
ACTION_BUTTONS = (
    By.CSS_SELECTOR,
    'button, [role="button"], input[type="button"], input[type="submit"]',
)
