Feature: Workflow Reklasifikasi PUMK Lengkap
  Menjalankan pengajuan, verifikasi, rekomendasi, persetujuan, dan realisasi.

  @ao
  Scenario: Pengajuan Reklasifikasi Kredit Bermasalah
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Pengajuan Reklas Kredit Bermasalah PUMK
    And saya memasukkan nomor kredit yang dikonfigurasi
    And saya memilih Jenis Pengajuan "Kredit Bermasalah Khusus"
    And saya klik Cari Nomor Kredit
    And saya mencentang opsi Kriteria Pinjaman Bermasalah "Kerusuhan"
    And saya mengisi Catatan Pinjaman Bermasalah "Ingin diajukan kredit bermasalah"
    And saya mengunggah PDF dengan nama dokumen "Dokumen Pendukung"
    Then saya memproses dan menyelesaikan pengajuan Kredit Bermasalah

  @kadp
  Scenario: Verifikasi Reklas Kredit Bermasalah sebelum rekomendasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Verifikasi Reklas Kredit Bermasalah PUMK
    And saya membuka proses verifikasi pada record pertama
    Then saya menyetujui dan menyimpan verifikasi Reklas Kredit Bermasalah

  @mbi
  Scenario: Rekomendasi Reklasifikasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Rekomendasi Reklasifikasi PUMK
    And saya membuka proses rekomendasi pada record pertama
    Then saya menyetujui dan menyimpan rekomendasi reklasifikasi

  @mbi
  Scenario: Persetujuan Reklasifikasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Persetujuan Reklasifikasi PUMK
    And saya membuka proses persetujuan pada record pertama
    Then saya menyetujui dan menyimpan persetujuan reklasifikasi

  @ksr
  Scenario: Realisasi Reklasifikasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Realisasi Reklasifikasi PUMK
    And saya memilih Jenis Pengajuan "Kredit Bermasalah Khusus" dan mencari data
    And saya membuka proses realisasi pada data pertama
    Then saya menyimpan dan melanjutkan proses realisasi
