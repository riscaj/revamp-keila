from behave import then, when


@when("saya membuka menu Verifikasi Reklas Kredit Bermasalah PUMK")
def open_verification_menu(context):
    context.reklasifikasi_page.open_verification_menu(context.pumk_section)


@when("saya membuka proses verifikasi pada record pertama")
def open_first_verification(context):
    context.verifikasi_page.open_first_record()


@then("saya menyetujui dan menyimpan verifikasi Reklas Kredit Bermasalah")
def approve_verification(context):
    context.verifikasi_page.complete_first_recommendation(return_to_list=True)
