Feature: Pelaporan dan Persetujuan Harian Kas Dan Bank PUMK
  Mengirim laporan kas harian lalu menyetujui laporan yang menunggu persetujuan.

  @pelaporan_kas_harian
  Scenario: Mengirim laporan kas dan bank PUMK
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial Pelaporan Kas Harian
    And saya membuka menu Pelaporan Harian Kas Dan Bank PUMK
    Then saya memproses data yang belum dilaporkan atau menambah laporan baru

  @persetujuan_kas_harian
  Scenario: Menyetujui laporan yang menunggu persetujuan
    Given halaman sign-in persetujuan dibuka
    When saya masuk sebagai pemimpin cabang
    And saya membuka menu persetujuan laporan kas harian
    Then saya menyetujui semua laporan yang menunggu persetujuan
