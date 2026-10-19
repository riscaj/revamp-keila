from behave import given, then, when


@given("halaman sign-in aplikasi dibuka")
def open_sign_in_page(context):
    context.monitoring_page.driver.get(context.monitoring_page.login_url)


@when("saya masuk menggunakan kredensial AO yang dikonfigurasi")
def sign_in_as_account_officer(context):
    context.monitoring_page.fill_login(context.username, context.password)
    context.monitoring_page.wait_for_dashboard()
    context.viewed_credit_types = []
    context.current_credit_type = None


@when("saya memilih Lihat Semua pada menu Monitoring")
def open_monitoring_feature_list(context):
    context.monitoring_page.open_monitoring_menu()


@when("saya membuka menu Monitoring Program UMK")
def open_monitoring_program(context):
    context.monitoring_page.wait_for_monitoring_list()


@then("halaman Monitoring Program UMK tampil")
def verify_monitoring_program_page(context):
    context.monitoring_page.wait_for_monitoring_list()


@when('saya mencari data pertama berdasarkan jenis kredit "{credit_type}"')
def search_first_record_by_credit_type(context, credit_type):
    context.monitoring_page.search_by_credit_type(credit_type)
    context.current_credit_type = credit_type


@when("saya membuka detail data pertama")
def open_first_record_detail(context):
    if not context.current_credit_type:
        raise AssertionError("Jenis kredit harus dicari sebelum detail dibuka.")
    context.monitoring_page.open_first_record_detail()
    context.viewed_credit_types.append(context.current_credit_type)


@when("saya kembali ke Beranda melalui breadcrumb")
def return_to_home_dashboard(context):
    context.monitoring_page.return_to_home_dashboard()


@then("detail data pertama untuk semua jenis kredit berhasil dibuka")
def verify_all_credit_type_details_opened(context):
    expected = [
        "Kredit Awal",
        "Rescheduling",
        "Reconditioning",
        "Kredit Bermasalah",
    ]
    assert context.viewed_credit_types == expected, (
        "Detail data pertama tidak dibuka untuk semua jenis kredit. "
        f"Expected: {expected}; actual: {context.viewed_credit_types}"
    )
