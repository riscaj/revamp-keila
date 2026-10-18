import os
import time

from behave import given, when
from selenium.common.exceptions import StaleElementReferenceException


@given("halaman sign-in aplikasi dibuka")
def open_sign_in_page(context):
    context.driver.get(context.restrukturisasi_page.login_url)


@when("saya masuk menggunakan kredensial yang dikonfigurasi")
def sign_in(context):
    context.restrukturisasi_page.fill_login(context.username, context.password)
    context.pumk_section = context.restrukturisasi_page.wait_for_dashboard()


@when("saya membuka menu Pengajuan Restrukturisasi PUMK")
def open_restructuring_menu(context):
    context.restrukturisasi_page.open_restructuring_menu(context.pumk_section)
    print("Popup Pasca Kredit PUMK dibuka; memilih Pengajuan Restrukturisasi PUMK.")


@when('saya mencari nomor kredit "{credit_number}"')
def search_credit_number(context, credit_number):
    _enter_credit_number(context, credit_number)


@when("saya mencari nomor kredit yang dikonfigurasi")
def search_configured_credit_number(context):
    credit_number = os.environ.get("RESTRUKTURISASI_CREDIT_NUMBER")
    if not credit_number:
        raise RuntimeError(
            "RESTRUKTURISASI_CREDIT_NUMBER belum diatur pada environment."
        )
    _enter_credit_number(context, credit_number)


def _enter_credit_number(context, credit_number):
    page = context.restrukturisasi_page
    credit_number_input = page.find_visible(page.credit_number_locator)
    while True:
        try:
            credit_number_input.clear()
            credit_number_input.send_keys(credit_number)
            break
        except StaleElementReferenceException:
            credit_number_input = page.find_visible(page.credit_number_locator)

    page.search_credit_number()
    time.sleep(5)
    print("Nomor kredit dicari; memilih alasan restrukturisasi.")
