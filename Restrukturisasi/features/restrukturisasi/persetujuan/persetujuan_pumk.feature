@mbi
Feature: Persetujuan Restrukturisasi PUMK
  Menyetujui persetujuan restrukturisasi PUMK melalui akun MBI.

  Scenario: Menyetujui persetujuan pada record pertama
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Persetujuan Restrukturisasi PUMK
    And saya membuka proses persetujuan pada record pertama
    Then saya menyetujui dan menyimpan persetujuan restrukturisasi
