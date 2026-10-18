import os

from behave import given, then, when


@given("halaman sign-in aplikasi dibuka")
def open_sign_in_page(context):
    context.driver.get(context.reklasifikasi_page.login_url)


@when("saya masuk menggunakan kredensial yang dikonfigurasi")
def sign_in(context):
    context.reklasifikasi_page.fill_login(context.username, context.password)
    context.pumk_section = context.reklasifikasi_page.wait_for_dashboard()


@when("saya membuka menu Pengajuan Reklas Kredit Bermasalah PUMK")
def open_problem_credit_menu(context):
    context.reklasifikasi_page.open_pengajuan_reklasifikasi_menu(
        context.pumk_section
    )


@when('saya memasukkan nomor kredit "{credit_number}"')
def enter_problem_credit_number(context, credit_number):
    context.pengajuan_kredit_bermasalah_page.enter_credit_number(credit_number)


@when("saya memasukkan nomor kredit yang dikonfigurasi")
def enter_configured_problem_credit_number(context):
    credit_number = os.environ.get("REKLASIFIKASI_CREDIT_NUMBER")
    if not credit_number:
        raise RuntimeError(
            "REKLASIFIKASI_CREDIT_NUMBER belum diatur pada environment."
        )
    context.pengajuan_kredit_bermasalah_page.enter_credit_number(credit_number)


@when('saya memilih Jenis Pengajuan "{application_type}"')
def choose_problem_application_type(context, application_type):
    context.pengajuan_kredit_bermasalah_page.choose_application_type(
        application_type
    )


@when("saya klik Cari Nomor Kredit")
def search_problem_credit_number(context):
    context.pengajuan_kredit_bermasalah_page.search_credit_number()


@when('saya mencentang opsi Kriteria Pinjaman Bermasalah "{criterion}"')
def choose_problem_criterion(context, criterion):
    context.pengajuan_kredit_bermasalah_page.choose_problem_criterion(criterion)


@when('saya mengisi Catatan Pinjaman Bermasalah "{note}"')
def fill_problem_note(context, note):
    context.pengajuan_kredit_bermasalah_page.fill_problem_note(note)


@when('saya mengunggah PDF dengan nama dokumen "{document_name}"')
def upload_problem_supporting_document(context, document_name):
    context.pengajuan_kredit_bermasalah_page.upload_supporting_document(
        document_name
    )


@then("saya memproses dan menyelesaikan pengajuan Kredit Bermasalah")
def submit_problem_credit_application(context):
    context.pengajuan_kredit_bermasalah_page.submit_and_finish()
