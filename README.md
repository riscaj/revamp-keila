# Revamp Keila

The repository contains separate automation projects:

- `Reklasifikasi/` runs the Reklasifikasi workflow.
- `Restrukturisasi/` runs the Restrukturisasi workflow.

## Local configuration

For Reklasifikasi, copy `Reklasifikasi/credentials.example.py` to
`Reklasifikasi/credentials.py` and fill in credentials locally. Do not commit
`credentials.py`.

For Restrukturisasi, copy `Restrukturisasi/credentials.example.py` to
`Restrukturisasi/credentials.py` and fill in credentials locally. Do not commit
`credentials.py`.

Set the test credit numbers in the environment before running the workflows:

- `REKLASIFIKASI_CREDIT_NUMBER` for Reklasifikasi.
- `RESTRUKTURISASI_CREDIT_NUMBER` for Restrukturisasi.

## Running workflows

Run from the corresponding project directory:

```bash
cd Reklasifikasi
python3 Reklasifikasi.py --format plain --no-capture
```

```bash
cd Restrukturisasi
python3 Restrukturisasi.py --format plain --no-capture
```

Each runner writes its PDF report to that project's `Reports/` directory.
Nomor Kredit perlu diubah dan dipastikan jenis kredit dan kolektibilitasnya
Username dan password perlu disesuaikan dengan cabang pada tiap nomor kredit
