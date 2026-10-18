@kadp
Feature: Verifikasi Reklas Kredit Bermasalah PUMK
  Memverifikasi Reklas Kredit Bermasalah sebelum proses rekomendasi.

  Scenario: Menyetujui verifikasi pada record pertama
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Verifikasi Reklas Kredit Bermasalah PUMK
    And saya membuka proses verifikasi pada record pertama
    Then saya menyetujui dan menyimpan verifikasi Reklas Kredit Bermasalah
