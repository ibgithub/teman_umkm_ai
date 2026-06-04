from .qwen_client import ask_qwen

def normalize_command(text: str) -> str:
    prompt = f"""
Tugasmu mengubah bahasa kasir menjadi command.

Contoh:

masukin dua kopi
-> tambah 2 kopi

tambahkan satu nasi goreng dan dua es teh
-> tambah 1 nasi goreng dan 2 es teh

masukin dua kopi satu teh
-> tambah 2 kopi dan 1 teh

tambah 2 pete 1 nasi uduk
-> tambah 2 pete dan 1 nasi uduk

2 ayam goreng 3 es teh
-> tambah 2 ayam goreng dan 3 es teh

masukkan dua ayam goreng, 1 pete
-> tambah 2 ayam goreng dan 1 pete

saya ingin membeli 1 pete, 2 nasi uduk
-> tambah 1 pete dan 2 nasi uduk

hapus nasi uduk
-> hapus nasi uduk

buang kopi
-> hapus kopi

saya bayar seratus ribu
-> bayar cash 100000

Jika tidak yakin, balas persis:
UNKNOWN

- Gunakan format:
  tambah <qty> <produk> dan <qty> <produk>

- Jika ada lebih dari satu produk, SELALU gunakan kata "dan".

- Jangan menghasilkan koma.

- Jangan menghasilkan penjelasan.

- Balas command saja.

Input:
{text}
"""

    result = ask_qwen(prompt)

    if result == "UNKNOWN":
        return ""

    return result.strip()