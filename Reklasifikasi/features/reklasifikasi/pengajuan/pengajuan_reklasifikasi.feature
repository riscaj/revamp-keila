Feature: Pengajuan Reklas Kredit Bermasalah PUMK
  Mengajukan kredit bermasalah khusus melalui dashboard Pasca Kredit PUMK.

  @ao
  Scenario: Mengajukan kredit bermasalah khusus dengan dokumen pendukung
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
