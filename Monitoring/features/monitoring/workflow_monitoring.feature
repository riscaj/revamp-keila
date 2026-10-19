Feature: Monitoring Program UMK
  Account Officer dapat melihat detail data pertama untuk setiap jenis kredit.

  @ao
  Scenario: Melihat detail semua jenis kredit pada Monitoring Program UMK
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial AO yang dikonfigurasi
    And saya memilih Lihat Semua pada menu Monitoring
    And saya membuka menu Monitoring Program UMK
    Then halaman Monitoring Program UMK tampil
    When saya mencari data pertama berdasarkan jenis kredit "Kredit Awal"
    And saya membuka detail data pertama
    And saya kembali ke Beranda melalui breadcrumb
    And saya memilih Lihat Semua pada menu Monitoring
    And saya membuka menu Monitoring Program UMK
    When saya mencari data pertama berdasarkan jenis kredit "Rescheduling"
    And saya membuka detail data pertama
    And saya kembali ke Beranda melalui breadcrumb
    And saya memilih Lihat Semua pada menu Monitoring
    And saya membuka menu Monitoring Program UMK
    When saya mencari data pertama berdasarkan jenis kredit "Reconditioning"
    And saya membuka detail data pertama
    And saya kembali ke Beranda melalui breadcrumb
    And saya memilih Lihat Semua pada menu Monitoring
    And saya membuka menu Monitoring Program UMK
    When saya mencari data pertama berdasarkan jenis kredit "Kredit Bermasalah"
    And saya membuka detail data pertama
    And saya kembali ke Beranda melalui breadcrumb
    Then detail data pertama untuk semua jenis kredit berhasil dibuka
