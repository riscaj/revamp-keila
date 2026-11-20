from behave import given, when


@given("halaman sign-in persetujuan dibuka")
def open_approval_sign_in(context):
    page = context.persetujuan_kas_harian_page
    context.driver.get(page.login_url)


@when("saya masuk sebagai pemimpin cabang")
def sign_in_as_branch_manager(context):
    page = context.persetujuan_kas_harian_page
    page.fill_login(context.username, context.password)
    page.wait_for_dashboard()


@when("saya membuka menu dan memproses persetujuan laporan kas harian")
def open_menu_and_approve_pending_daily_cash_reports(context):
    page = context.persetujuan_kas_harian_page
    page.open_approval_menu()
    context.approved_report_count = page.approve_one_pending_report()
