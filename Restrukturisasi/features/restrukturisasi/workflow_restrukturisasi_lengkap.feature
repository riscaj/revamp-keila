Feature: Workflow Restrukturisasi PUMK Lengkap
  Menjalankan pengajuan, survey, rekomendasi, persetujuan, dan realisasi secara berurutan.

  @ao
  Scenario: Pengajuan restrukturisasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Pengajuan Restrukturisasi PUMK
    And saya mencari nomor kredit yang dikonfigurasi
    And saya memilih alasan restrukturisasi "Dampak kondisi ekonomi"
    And saya memilih jangka waktu "12 Bulan"
    Then saya mengonfirmasi dan menyelesaikan pengajuan

  @ao
  Scenario: Survey restrukturisasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Survey PUMK
    And saya membuka proses survey pada record pertama
    Then saya menyelesaikan survey dan menyimpan catatannya

  @mbi
  Scenario: Rekomendasi restrukturisasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Rekomendasi Restrukturisasi PUMK
    And saya membuka proses rekomendasi pada record pertama
    Then saya menyetujui dan menyimpan rekomendasi restrukturisasi

  @mbi
  Scenario: Persetujuan restrukturisasi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
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
