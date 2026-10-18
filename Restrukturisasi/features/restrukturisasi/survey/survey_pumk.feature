Feature: Survey PUMK
  Menyelesaikan survey pada record pertama Survey Restrukturisasi PUMK.

  Scenario: Menyelesaikan dan menyimpan Survey Restrukturisasi PUMK
    Given halaman sign-in aplikasi dibuka
    When saya masuk menggunakan kredensial yang dikonfigurasi
    And saya membuka menu Survey PUMK
    And saya membuka proses survey pada record pertama
    Then saya menyelesaikan survey dan menyimpan catatannya
