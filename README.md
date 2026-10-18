# Revamp Keila

The repository contains separate automation projects:

- `Reklasifikasi/` runs the Reklasifikasi workflow.
- The repository root runs the Restrukturisasi workflow.

## Local configuration

For Reklasifikasi, copy `Reklasifikasi/credentials.example.py` to
`Reklasifikasi/credentials.py` and fill in credentials locally. Do not commit
`credentials.py`.

The root `credentials.py` has blank role placeholders for Restrukturisasi;
fill them locally and do not commit credential values.

Set the test credit numbers in the environment before running the workflows:

- `REKLASIFIKASI_CREDIT_NUMBER` for Reklasifikasi.
- `RESTRUKTURISASI_CREDIT_NUMBER` for Restrukturisasi.

## Running workflows

Run from the corresponding project directory:

```bash
python3 Reklasifikasi.py --format plain --no-capture
```

```bash
python3 Restrukturisasi.py --format plain --no-capture
```

Each runner writes its PDF report to that project's `Reports/` directory.
Nomor Kredit perlu diubah dan dipastikan jenis kredit dan kolektibilitasnya
Username dan password perlu disesuaikan dengan cabang pada tiap nomor kredit
