from .qwen_client import ask_qwen

def normalize_command(text: str) -> str:
    prompt = f"""
Tugasmu mengubah bahasa kasir menjadi command.

Contoh:

masukin dua kopi
-> tambah 2 kopi

tambahkan satu nasi goreng dan dua es teh
-> tambah 1 nasi goreng dan 2 es teh

hapus nasi uduk
-> hapus nasi uduk

buang kopi
-> hapus kopi

saya bayar seratus ribu
-> bayar cash 100000

Jika tidak yakin, balas persis:
UNKNOWN

Input:
{text}
"""

    result = ask_qwen(prompt)

    if result == "UNKNOWN":
        return ""

    return result.strip()