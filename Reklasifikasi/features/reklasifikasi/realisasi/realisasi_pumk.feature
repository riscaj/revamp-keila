@ksr
Feature: Realisasi Reklasifikasi PUMK
  Menyelesaikan realisasi menggunakan akun kasir.

  Scenario: Menyimpan realisasi pada data pertama
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Realisasi Reklasifikasi PUMK
    And saya memilih Jenis Pengajuan "Kredit Bermasalah Khusus" dan mencari data
    And saya membuka proses realisasi pada data pertama
    Then saya menyimpan dan melanjutkan proses realisasi
