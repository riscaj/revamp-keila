from behave import then, when


@when("saya membuka menu Persetujuan Restrukturisasi PUMK")
def open_approval_menu(context):
    context.restrukturisasi_page.open_approval_menu(context.pumk_section)


@when("saya membuka proses persetujuan pada record pertama")
def open_first_approval(context):
    context.persetujuan_page.open_first_record()


@then("saya menyetujui dan menyimpan persetujuan restrukturisasi")
def approve_restructuring(context):
    context.persetujuan_page.complete_first_recommendation()
