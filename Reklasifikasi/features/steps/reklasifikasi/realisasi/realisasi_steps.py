from behave import then, when


@when("saya membuka menu Realisasi Reklasifikasi PUMK")
def open_realisasi_menu(context):
    context.reklasifikasi_page.open_realisasi_menu(context.pumk_section)


@when(
    'saya memilih Jenis Pengajuan "Kredit Bermasalah Khusus" dan mencari data'
)
def search_problem_credit_realisasi(context):
    context.realisasi_page.filter_problem_credit_application()


@when("saya membuka proses realisasi pada data pertama")
def open_first_realisasi(context):
    context.realisasi_page.open_first_record()


@then("saya menyimpan dan melanjutkan proses realisasi")
def complete_first_realisasi(context):
    context.realisasi_page.complete_first_record()
