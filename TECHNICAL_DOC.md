# Dokumen Teknis Teman UMKM AI

Dokumen ini menjelaskan cara kerja source code `teman_umkm_ai` dari sudut pandang belajar AI agent sederhana.

Project ini belum memakai LLM sungguhan. Namun, strukturnya sudah mulai mengikuti pola agentic AI:

- menerima pesan user
- memahami intent
- menyimpan state percakapan
- mengeksekusi action
- memberi response

## 1. Flow Utama

Alur utama dimulai dari `main.py`.

```text
User input
  -> main.py
  -> agent.process()
  -> parser.py
  -> agent.py
  -> api.py / cart.py / context.py / matcher.py
  -> llm.py
  -> output ke user
```

Contoh:

```text
You: tambah 2 kopi
```

Flow-nya:

```text
main.py menerima input
  -> agent.process("tambah 2 kopi")
  -> parser.py mengubah input menjadi AddItemCommand(qty=2, product_keyword="kopi")
  -> agent.py mencari produk via api.py
  -> matcher.py mencocokkan keyword dengan daftar produk
  -> cart.py menambahkan item ke cart
  -> context.py menyimpan produk terakhir
  -> llm.py membuat response teks
```

## 2. Architecture

Project dibagi menjadi beberapa file kecil supaya tiap bagian punya tanggung jawab jelas.

### `main.py`

Entry point aplikasi CLI.

Tugasnya:

- membuat `TemanUmkmClient`
- membuat `TemanUmkmAgent`
- login ke API
- menjalankan loop input user
- menampilkan response agent

`main.py` tidak berisi business logic. Ia hanya menjadi pintu masuk program.

### `api.py`

Lapisan komunikasi ke backend Teman UMKM.

Tugasnya:

- login
- ambil merchant
- ambil outlet
- ambil produk
- create sales

File ini memakai `requests.Session()` supaya token Authorization bisa disimpan dan dipakai ulang.

### `parser.py`

Lapisan intent parser.

Tugasnya mengubah teks user menjadi command object.

Contoh:

```text
"tambah 2 kopi"
```

menjadi:

```python
AddItemCommand(qty=2, product_keyword="kopi")
```

Command yang didukung:

- `AddItemCommand`
- `AddLastItemCommand`
- `RemoveItemCommand`
- `ShowCartCommand`
- `ClearCartCommand`
- `PayCommand`

Ini adalah bentuk paling sederhana dari intent parsing.

### `matcher.py`

Lapisan product matching.

Tugasnya:

- mencari exact match
- mencari contains match
- resolve pilihan user saat ada banyak kandidat

Contoh:

```text
User: tambah 1 ayam
```

Kalau produk yang ditemukan:

```text
Ayam Utuh
Ayam Geprek
Ayam Bakar
```

maka agent tidak langsung memilih. Agent akan menyimpan pending action dan bertanya ke user.

### `cart.py`

Lapisan cart state.

Tugasnya:

- menyimpan item sementara sebelum pembayaran
- merge qty kalau produk sama ditambahkan lagi
- menghitung subtotal
- menghapus item
- mengosongkan cart
- mengubah cart menjadi payload sales

Object penting:

```python
CartSession
CartItem
```

### `context.py`

Lapisan conversational context.

Tugasnya menyimpan konteks percakapan terakhir.

Saat ini konteks yang disimpan:

```python
last_product
last_action
```

Contoh:

```text
You: tambah 2 kopi
AI: Kopi masuk cart

You: tambah 1 lagi
AI: Kopi ditambah 1 lagi
```

Agent bisa memahami `lagi` karena `context.py` menyimpan produk terakhir.

### `agent.py`

Otak orkestrasi.

Tugasnya:

- menerima pesan user
- cek apakah ada pending action
- memanggil parser
- memutuskan command harus diproses ke mana
- memakai matcher untuk mencari produk
- memakai cart untuk menyimpan item
- memakai context untuk mengingat produk terakhir
- memakai api untuk create sales
- memakai llm untuk membuat response

`agent.py` adalah pusat koordinasi, bukan tempat semua logic ditumpuk.

### `llm.py`

Lapisan response generator.

Walaupun namanya `llm.py`, saat ini belum memanggil API LLM sungguhan.

Tugasnya:

- membuat response teks untuk user
- menampilkan cart
- membuat pertanyaan klarifikasi
- memberi pesan error yang ramah

Nanti kalau ingin pakai LLM sungguhan, file ini bisa dikembangkan.

## 3. State

State adalah data yang disimpan sementara supaya agent bisa mengingat kondisi percakapan.

Project ini punya beberapa jenis state.

### 3.1 Cart State

Disimpan di:

```python
self.cart = CartSession(session_id="cli")
```

Cart menyimpan item yang belum dibayar.

Contoh isi cart:

```python
CartSession(
    session_id="cli",
    items=[
        CartItem(
            product_id=1,
            product_name="Kopi Susu",
            qty=3,
            price=12000,
        )
    ],
)
```

### 3.2 Pending Action State

Disimpan di:

```python
self.pending_action
```

Dipakai saat agent butuh klarifikasi.

Contoh:

```text
You: tambah 1 ayam
AI: Saya menemukan beberapa produk:
1. Ayam Utuh
2. Ayam Geprek
3. Ayam Bakar
```

Saat itu agent menyimpan:

```python
PendingAction(
    action_type="add_item",
    qty=1,
    candidates=[...],
)
```

Lalu saat user menjawab:

```text
geprek
```

agent memakai `pending_action` untuk menyelesaikan action sebelumnya.

### 3.3 Conversation Context State

Disimpan di:

```python
self.context = ConversationContext()
```

Saat ini dipakai untuk menyimpan:

```python
last_product
last_action
```

Contoh:

```text
You: tambah 2 kopi
You: tambah 1 lagi
```

Kalimat `tambah 1 lagi` bisa diproses karena agent tahu produk terakhir adalah `kopi`.

### 3.4 Cached Merchant dan Outlet

Disimpan di:

```python
self.merchant_id
self.outlet_id
```

Tujuannya agar agent tidak perlu request merchant dan outlet berulang kali.

## 4. Orchestration

Orchestration adalah cara agent mengatur beberapa komponen untuk menyelesaikan tugas user.

Contoh command normal:

```text
You: tambah 2 kopi
```

Orchestration:

```text
agent.process()
  -> parse_user_message()
  -> _handle_command()
  -> _add_item()
  -> api.get_products()
  -> matcher.match_products()
  -> cart.add_item()
  -> context.remember_product()
  -> llm.item_added()
```

Contoh command ambigu:

```text
You: tambah 1 ayam
```

Orchestration:

```text
agent.process()
  -> parser menghasilkan AddItemCommand
  -> agent ambil produk
  -> matcher menemukan banyak kandidat
  -> agent menyimpan PendingAction
  -> llm.clarify_product()
```

User menjawab:

```text
You: geprek
```

Orchestration:

```text
agent.process()
  -> pending_action ada
  -> _resolve_pending_action()
  -> matcher.resolve_candidate()
  -> cart.add_item()
  -> context.remember_product()
  -> pending_action dikosongkan
  -> llm.item_added()
```

Contoh context reference:

```text
You: tambah 2 kopi
You: tambah 1 lagi
```

Orchestration:

```text
agent.process("tambah 1 lagi")
  -> parser menghasilkan AddLastItemCommand(qty=1)
  -> agent membaca context.last_product
  -> cart.add_item(last_product, 1)
  -> context.remember_product()
  -> llm.item_added()
```

Contoh payment:

```text
You: bayar cash 50000
```

Orchestration:

```text
agent.process()
  -> parser menghasilkan PayCommand
  -> agent cek cart kosong atau tidak
  -> agent cek uang cukup atau tidak
  -> api.create_sale()
  -> cart.clear()
  -> llm.sale_created()
```

## 5. Kenapa Struktur Ini Penting untuk Belajar AI

Project ini mengajarkan beberapa konsep penting AI agent tanpa perlu langsung memakai LLM.

### Intent Parsing

Agent perlu mengerti maksud user.

Di project ini, parsing masih rule-based:

```text
tambah 2 kopi -> AddItemCommand
cart -> ShowCartCommand
bayar cash 50000 -> PayCommand
```

### Tool Use

Dalam agentic AI, agent biasanya memakai tools.

Di project ini, tools-nya adalah:

- API client
- cart session
- product matcher
- context memory
- response generator

### Memory

Agent tidak hanya menjawab input saat ini, tapi juga mengingat keadaan sebelumnya.

Memory yang sudah ada:

- cart
- pending action
- last product
- merchant id
- outlet id

### Clarification

Agent tidak asal mengeksekusi saat input ambigu.

Ini penting karena user sering memberi instruksi tidak lengkap.

Contoh:

```text
tambah ayam
```

Agent perlu bertanya:

```text
Ayam yang mana?
```

### Multi-Step Workflow

Agent mulai bisa menangani alur beberapa langkah.

Contoh:

```text
tambah ayam
geprek
cart
bayar cash 50000
```

Ini bukan lagi script satu command satu action. Ini sudah mulai menjadi workflow percakapan.

## 6. Batasan Saat Ini

Beberapa hal yang masih sederhana:

- state masih in-memory, hilang kalau program ditutup
- hanya cocok untuk satu user CLI
- belum ada database lokal
- belum ada Redis
- belum memakai LLM sungguhan
- product matching belum fuzzy
- payment baru mendukung `CASH`

## 7. Next Improvement

Peningkatan yang masuk akal berikutnya:

1. Tambahkan fuzzy matching dengan RapidFuzz.
2. Pindahkan gabungan cart, context, dan pending action ke `session.py`.
3. Tambahkan command `kurangi 1 kopi`.
4. Tambahkan command `ubah kopi jadi 3`.
5. Tambahkan unit test untuk parser, matcher, cart, dan agent.
6. Tambahkan integrasi LLM sungguhan di `llm.py`.
7. Simpan session ke Redis kalau nanti jadi backend multi-user.
