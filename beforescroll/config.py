"""Tüm sabitler ve kurallar tek yerde (tekrarı önlemek için)."""
from dataclasses import dataclass

import numpy as np


@dataclass
class Config:
    n_users: int = 40
    n_days: int = 28
    horizon_min: int = 10          # erken uyarı ufku (dk)
    seed: int = 42
    label_noise: float = 0.03
    # --- Risk kuralları (sorumluluk bağlamı) ---
    risk_quantile: float = 0.60    # kişisel "normal" eşik: bağımlılık yapıcı oturum süresi persentili
    min_risk_minutes: float = 15.0
    pending_min: float = 5.0       # responsibilities_met==0 iken bu süre bile risklidir
    tolerance: float = 1.25        # responsibilities_met==1 iken eşik bu çarpanla esner
    out_dir: str = "output"


# kategori, taban süre (dk), bildirim yoğunluğu, bağımlılık yapıcı mı
APPS = {
    "Instagram": ("social", 7, 1.6, True),
    "TikTok": ("social", 11, 1.0, True),
    "X": ("social", 8, 1.8, True),
    "YouTube": ("video", 12, 0.4, True),
    "PUBG": ("game", 22, 0.3, True),
    "Slack": ("productivity", 3, 2.5, False),
    "WhatsApp": ("messaging", 3, 2.2, False),
}
NAMES = list(APPS)
ADDICTIVE = np.array([v[3] for v in APPS.values()])

# oturum/saat yoğunluğu: akşam 18-23 yüksek
HOURLY_RATE = np.array([0.03] * 6 + [0.40] * 3 + [0.35] * 9 + [0.75] * 6)
WINDOWS = (30, 120, 360)  # özellik pencereleri (dk)