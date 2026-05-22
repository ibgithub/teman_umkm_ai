import os


BASE_URL = os.getenv("TEMAN_UMKM_BASE_URL", "https://api.teman-umkm.com")
USERNAME = os.getenv("TEMAN_UMKM_USERNAME", "merchant6")
PASSWORD = os.getenv("TEMAN_UMKM_PASSWORD", "merchant6")
DEFAULT_PAYMENT_METHOD = os.getenv("TEMAN_UMKM_PAYMENT_METHOD", "CASH")
REQUEST_TIMEOUT = int(os.getenv("TEMAN_UMKM_REQUEST_TIMEOUT", "15"))
