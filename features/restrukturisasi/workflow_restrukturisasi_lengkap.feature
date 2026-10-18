Feature: Workflow Restrukturisasi PUMK Lengkap
  Menjalankan pengajuan, survey, rekomendasi, persetujuan, dan realisasi secara berurutan.

  @ao
  Scenario: Pengajuan dan survey restrukturisasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Pengajuan Restrukturisasi PUMK
    And saya mencari nomor kredit "13114260905465"
    And saya memilih alasan restrukturisasi "Dampak kondisi ekonomi"
    And saya memilih jangka waktu "12 Bulan"
    Then saya mengonfirmasi dan menyelesaikan pengajuan
    And dashboard beranda tampil kembali
    When saya membuka menu Survey PUMK
    And saya membuka proses survey pada record pertama
    Then saya menyelesaikan survey dan menyimpan catatannya

  @mbi
  Scenario: Rekomendasi dan persetujuan restrukturisasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Rekomendasi Restrukturisasi PUMK
    And saya membuka proses rekomendasi pada record pertama
    Then saya menyetujui dan menyimpan rekomendasi restrukturisasi
    When saya kembali ke beranda setelah rekomendasi
    And saya membuka menu Persetujuan Restrukturisasi PUMK
    And saya membuka proses persetujuan pada record pertama
    Then saya menyetujui dan menyimpan persetujuan restrukturisasi

  @ksr
  Scenario: Realisasi restrukturisasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Realisasi Restrukturisasi PUMK
    And saya memilih semua fasilitas restrukturisasi dan mencari data
    And saya membuka proses realisasi pada data pertama
    Then saya mengunggah berkas perjanjian kredit dan kartu angsuran
