Feature: Pengajuan restrukturisasi PUMK
  Mengajukan restrukturisasi kredit melalui dashboard Pasca Kredit PUMK.

  Scenario: Mengajukan restrukturisasi dengan dampak kondisi ekonomi
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Pengajuan Restrukturisasi PUMK
    And saya mencari nomor kredit yang dikonfigurasi
    And saya memilih alasan restrukturisasi "Dampak kondisi ekonomi"
    And saya memilih jangka waktu "12 Bulan"
    Then saya mengonfirmasi dan menyelesaikan pengajuan
