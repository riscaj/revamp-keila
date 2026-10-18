from behave import then, when


@when("saya membuka menu Rekomendasi Reklasifikasi PUMK")
def open_recommendation_menu(context):
    context.reklasifikasi_page.open_recommendation_menu(context.pumk_section)


@when("saya membuka proses rekomendasi pada record pertama")
def open_first_recommendation(context):
    context.rekomendasi_page.open_first_record()


@then("saya menyetujui dan menyimpan rekomendasi reklasifikasi")
def approve_recommendation(context):
    context.rekomendasi_page.complete_first_recommendation()
