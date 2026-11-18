# Revamp Keila

Repository ini berisi tiga proyek otomasi yang terpisah:

- `Reklasifikasi/` untuk alur Reklasifikasi.
- `Restrukturisasi/` untuk alur Restrukturisasi.
- `Monitoring/` untuk alur Monitoring Program UMK.
- `Pelaporan Kas Harian/` untuk alur pelaporan dan persetujuan kas harian.

## Persiapan

Siapkan kredensial lokal untuk proyek yang akan dijalankan:

```bash
cp Reklasifikasi/credentials.example.py Reklasifikasi/credentials.py
cp Restrukturisasi/credentials.example.py Restrukturisasi/credentials.py
cp Monitoring/credentials.example.py Monitoring/credentials.py
cp "Pelaporan Kas Harian/credentials.example.py" "Pelaporan Kas Harian/credentials.py"
```

Isi username dan password sesuai role yang dibutuhkan serta cabang yang
menangani nomor kredit. Jangan commit file `credentials.py`.

Gunakan nomor kredit pengujian yang sesuai dengan jenis kredit dan
kolektibilitas yang dibutuhkan oleh skenario. Atur nomor kredit melalui
environment variable sebelum menjalankan proyek terkait:

```bash
export REKLASIFIKASI_CREDIT_NUMBER="<nomor-kredit-pengujian>"
export RESTRUKTURISASI_CREDIT_NUMBER="<nomor-kredit-pengujian>"
```

## Menjalankan workflow

Pasang dependensi proyek terlebih dahulu jika belum tersedia:

```bash
python3 -m pip install -r Reklasifikasi/requirements.txt
python3 -m pip install -r Restrukturisasi/requirements.txt
python3 -m pip install -r Monitoring/requirements.txt
python3 -m pip install -r "Pelaporan Kas Harian/requirements.txt"
```

Jalankan dari root repository dengan memilih proyek yang diinginkan:

```bash
cd Reklasifikasi
python3 Reklasifikasi.py --format plain --no-capture
```

```bash
cd Restrukturisasi
python3 Restrukturisasi.py --format plain --no-capture
```

```bash
cd Monitoring
python3 Monitoring.py --format plain --no-capture
```

```bash
cd "Pelaporan Kas Harian"
python3 FlowPelaporanKasHarian.py
```

Jalankan `PelaporanKasHarian.py` untuk alur pelaporan saja atau
`PersetujuanKasHarian.py` untuk persetujuan saja. Alur gabungan menjalankan
persetujuan setelah pelaporan berhasil.

Runner menjalankan workflow lengkap bawaan dan menyimpan report PDF di folder
`Reports/` pada proyek masing-masing. Workflow Monitoring membuka data pertama
untuk `Kredit Awal`, `Rescheduling`, `Reconditioning`, dan `Kredit Bermasalah`.
Proyek Pelaporan Kas Harian juga menyimpan report PDF setiap selesai dijalankan,
termasuk saat workflow gagal, di `Pelaporan Kas Harian/Reports/`.
