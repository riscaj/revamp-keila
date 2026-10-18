@mbi
Feature: Rekomendasi Reklasifikasi PUMK
  Menyetujui rekomendasi reklasifikasi PUMK melalui akun MBI.

  Scenario: Menyetujui rekomendasi pada record pertama
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Rekomendasi Reklasifikasi PUMK
    And saya membuka proses rekomendasi pada record pertama
    Then saya menyetujui dan menyimpan rekomendasi reklasifikasi
