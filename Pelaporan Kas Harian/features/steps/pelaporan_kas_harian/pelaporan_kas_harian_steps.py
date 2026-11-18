from behave import given, then, when


@given("halaman sign-in aplikasi dibuka")
def open_sign_in_page(context):
    context.driver.get(context.pelaporan_kas_harian_page.login_url)


@when("saya masuk menggunakan kredensial Pelaporan Kas Harian")
def sign_in(context):
    context.pelaporan_kas_harian_page.fill_login(
        context.username,
        context.password,
    )
    context.pelaporan_kas_harian_page.wait_for_dashboard()


@when("saya membuka menu Pelaporan Harian Kas Dan Bank PUMK")
def open_daily_cash_and_bank_report_menu(context):
    context.pelaporan_kas_harian_page.open_report_menu()


@then(
    "saya memproses data yang belum dilaporkan atau menambah laporan baru"
)
def handle_daily_cash_and_bank_report(context):
    page = context.pelaporan_kas_harian_page
    context.report_action = page.process_pending_or_add_report()
    if context.report_action in {"process", "add_report"}:
        page.complete_bank_balance_report()
