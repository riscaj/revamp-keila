import time

from behave import then, when


@when('saya memilih alasan restrukturisasi "{reason}"')
def choose_restructuring_reason(context, reason):
    context.pengajuan_restrukturisasi_page.choose_reason(reason)


@when('saya memilih jangka waktu "{term}"')
def choose_term(context, term):
    context.pengajuan_restrukturisasi_page.choose_term(term)
    print("Pilihan alasan dan jangka waktu sudah diisi; menekan Proses Pengajuan.")


@then("saya mengonfirmasi dan menyelesaikan pengajuan")
def confirm_and_finish_application(context):
    context.pengajuan_restrukturisasi_page.confirm_and_finish()
    print("Kembali ke Daftar sudah diklik. Browser ditutup dalam 5 detik.")
    time.sleep(5)
