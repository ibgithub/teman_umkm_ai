# Teman UMKM AI

CLI chatbot sederhana untuk membuat transaksi penjualan ke API Teman UMKM.

## Struktur

- `main.py` sebagai wrapper untuk menjalankan CLI lama
- `app/cli.py` untuk loop CLI
- `app/agent.py` untuk orkestrasi chatbot
- `app/cart.py` untuk menyimpan cart sementara di memory
- `app/context.py` untuk menyimpan konteks percakapan terakhir
- `app/matcher.py` untuk mencari produk dan menangani kandidat ambigu
- `app/parser.py` untuk parsing pesan user menjadi command
- `app/llm.py` untuk membuat response teks AI
- `app/api.py` untuk client API Teman UMKM
- `app/config.py` untuk konfigurasi environment
- `tests/` untuk unit test parser dan agent behavior

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Konfigurasi

Default credential masih sama seperti script awal:

- `TEMAN_UMKM_USERNAME=merchant6`
- `TEMAN_UMKM_PASSWORD=merchant6`
- `TEMAN_UMKM_BASE_URL=https://api.teman-umkm.com`
- `TEMAN_UMKM_PAYMENT_METHOD=CASH`

Credential bisa dioverride lewat environment variable.

## Jalankan

```bash
python main.py
```

Atau:

```bash
python -m app.cli
```

Contoh perintah:

```text
tambah 2 kopi
beli kopi dan gula
beli 2 kopi, 1 gula, 3 teh
tambah lagi
tambah 1 lagi
cart
hapus kopi
clear cart
bayar cash 50000
exit
```

Catatan: command `jual 2 kopi` masih didukung sebagai alias dari `tambah 2 kopi`.

Catatan: command `tambah lagi` dan `tambah 1 lagi` memakai produk terakhir yang berhasil masuk cart.

## Test

```bash
python -m unittest discover -s tests
```

Contoh alur ambigu:

```text
You: tambah 1 ayam
AI: Saya menemukan beberapa produk:
1. Ayam Utuh
2. Ayam Geprek
3. Ayam Bakar

Mau yang mana? Balas dengan nomor atau nama produk.

You: geprek
AI:
Item berhasil ditambahkan ke cart.
```
