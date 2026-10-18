from behave import then, when


@when("saya membuka menu Realisasi Restrukturisasi PUMK")
def open_realisasi_menu(context):
    context.restrukturisasi_page.open_realisasi_menu(context.pumk_section)


@when("saya memilih semua fasilitas restrukturisasi dan mencari data")
def search_all_realisasi(context):
    context.realisasi_page.filter_all_facilities()


@when("saya membuka proses realisasi pada data pertama")
def open_first_realisasi(context):
    context.realisasi_page.open_first_record()


@then("saya mengunggah berkas perjanjian kredit dan kartu angsuran")
def upload_realisasi_files(context):
    context.realisasi_page.upload_agreement_files()
