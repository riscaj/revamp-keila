@mbi
Feature: Persetujuan Reklasifikasi PUMK
  Menyetujui persetujuan reklasifikasi PUMK melalui akun MBI.

  Scenario: Menyetujui persetujuan pada record pertama
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Persetujuan Reklasifikasi PUMK
    And saya membuka proses persetujuan pada record pertama
    Then saya menyetujui dan menyimpan persetujuan reklasifikasi
