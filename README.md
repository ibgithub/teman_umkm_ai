# Teman UMKM AI

CLI chatbot sederhana untuk membuat transaksi penjualan ke API Teman UMKM.

## Struktur

- `main.py` untuk loop CLI
- `agent.py` untuk orkestrasi chatbot
- `cart.py` untuk menyimpan cart sementara di memory
- `context.py` untuk menyimpan konteks percakapan terakhir
- `matcher.py` untuk mencari produk dan menangani kandidat ambigu
- `parser.py` untuk parsing pesan user menjadi command
- `llm.py` untuk membuat response teks AI
- `api.py` untuk client API Teman UMKM
- `config.py` untuk konfigurasi environment

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

Contoh perintah:

```text
tambah 2 kopi
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
