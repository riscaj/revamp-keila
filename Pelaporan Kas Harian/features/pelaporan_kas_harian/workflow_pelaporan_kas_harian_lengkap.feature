Feature: Pelaporan dan Persetujuan Harian Kas Dan Bank PUMK
  Mengirim laporan kas harian lalu menyetujui satu laporan yang menunggu persetujuan.

  @pelaporan_kas_harian
  Scenario: Mengirim laporan kas dan bank PUMK
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial Pelaporan Kas Harian
    And saya membuka menu Pelaporan Harian Kas Dan Bank PUMK
    Then saya mengirim laporan kas harian

  @persetujuan_kas_harian
  Scenario: Menyetujui satu laporan kas dan bank PUMK
    Given halaman sign-in persetujuan dibuka
    When saya masuk sebagai pemimpin cabang
    And saya membuka menu dan memproses persetujuan laporan kas harian
