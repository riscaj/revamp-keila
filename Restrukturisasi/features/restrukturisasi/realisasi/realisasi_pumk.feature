@ksr
Feature: Realisasi Restrukturisasi PUMK
  Mengunggah berkas realisasi menggunakan akun kasir.

  Scenario: Mengunggah berkas realisasi pada data pertama
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Realisasi Restrukturisasi PUMK
    And saya memilih semua fasilitas restrukturisasi dan mencari data
    And saya membuka proses realisasi pada data pertama
    Then saya mengunggah berkas perjanjian kredit dan kartu angsuran
