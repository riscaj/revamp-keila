from behave import given, then, when


@given("halaman sign-in persetujuan dibuka")
def open_approval_sign_in(context):
    page = context.persetujuan_kas_harian_page
    context.driver.get(page.login_url)


@when("saya masuk sebagai pemimpin cabang")
def sign_in_as_branch_manager(context):
    page = context.persetujuan_kas_harian_page
    page.fill_login(context.username, context.password)
    page.wait_for_dashboard()


@when("saya membuka menu persetujuan laporan kas harian")
def open_daily_cash_report_approval_menu(context):
    context.persetujuan_kas_harian_page.open_approval_menu()


@then("saya menyetujui semua laporan yang menunggu persetujuan")
def approve_all_pending_daily_cash_reports(context):
    context.approved_report_count = (
        context.persetujuan_kas_harian_page.approve_all_pending_reports()
    )
