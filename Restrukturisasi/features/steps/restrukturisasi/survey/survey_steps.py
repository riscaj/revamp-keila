from behave import then, when


@when("saya membuka menu Survey PUMK")
def open_survey_menu(context):
    context.restrukturisasi_page.open_survey_menu(context.pumk_section)


@when("saya membuka proses survey pada record pertama")
def open_first_survey_record(context):
    context.survey_page.open_first_record()


@then("saya menyelesaikan survey dan menyimpan catatannya")
def complete_survey(context):
    context.survey_page.complete_first_survey()
