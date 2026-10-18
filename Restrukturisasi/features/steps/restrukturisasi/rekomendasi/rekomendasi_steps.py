from behave import then, when


@when("saya membuka menu Rekomendasi Restrukturisasi PUMK")
def open_recommendation_menu(context):
    context.restrukturisasi_page.open_recommendation_menu(context.pumk_section)


@when("saya membuka proses rekomendasi pada record pertama")
def open_first_recommendation(context):
    context.rekomendasi_page.open_first_record()


@then("saya menyetujui dan menyimpan rekomendasi restrukturisasi")
def approve_recommendation(context):
    context.rekomendasi_page.complete_first_recommendation()


@when("saya kembali ke beranda setelah rekomendasi")
def return_home_after_recommendation(context):
    context.pumk_section = (
        context.restrukturisasi_page.return_to_home_dashboard()
    )
