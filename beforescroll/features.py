"""Sızıntısız zaman serisi özellikleri: karar anı = oturum başlangıcı - ufuk."""
import numpy as np
import pandas as pd

from config import WINDOWS

META = ("user_id", "start_time", "risk_label")


def build_features(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Yalnızca karar anına dek BİTMİŞ geçmiş oturumlar + takvim + güncel sorumluluk durumu kullanılır.
    (Oturumun kendi notification/usage/app/trigger değerleri oturum öncesinde bilinemez -> girdi değil.)"""
    t_ref, out = df.start_time.min(), []
    for uid, g in df.groupby("user_id"):
        s = ((g.start_time - t_ref).dt.total_seconds() / 60).to_numpy()
        use = g.usage_minutes.to_numpy()
        e = s + use                                            # oturumlar çakışmaz -> artan
        cols = dict(n=np.ones(len(g)), use=use, notif=g.notifications.to_numpy(),
                    opens=g.times_opened.to_numpy(),
                    addict=g.is_addictive_app.to_numpy(float),
                    ntrig=(g.trigger_type == "Notification_Triggered").to_numpy(float),
                    risk=g.risk_label.to_numpy(float),
                    pend_add=(g.is_addictive_app & (g.responsibilities_met == 0)).to_numpy(float))
        for i in range(len(g)):
            cut = s[i] - horizon
            k = np.searchsorted(e, cut, side="right")          # cut'a dek bitmiş oturum sayısı
            r = dict(user_id=uid, start_time=g.start_time.iloc[i], risk_label=int(cols["risk"][i]))
            for w in WINDOWS:
                sl = slice(np.searchsorted(e, cut - w, side="right"), k)
                n = sl.stop - sl.start
                for name in ("n", "use", "notif", "opens"):
                    r[f"{name}_{w}"] = cols[name][sl].sum()
                if w == 120:                                   # oranlar + kişisel sapma
                    for name in ("addict", "ntrig", "risk", "pend_add"):
                        r[f"{name}_120"] = cols[name][sl].sum() if name in ("risk", "pend_add") \
                            else (cols[name][sl].mean() if n else 0.0)
                    r["mean_use_120"] = use[sl].mean() if n else 0.0
            r["mins_since_last"] = min(cut - e[k - 1], 720) if k else 720
            # kişisel baseline ("senin normalin")
            if k >= 5:
                hrs = max((cut - s[0]) / 60, 1.0)
                r["usage_dev_z"] = (r["mean_use_120"] - use[:k].mean()) / (use[:k].std() + 1) if r["n_120"] else 0.0
                r["rate_dev_120"] = r["n_120"] - 2 * k / hrs
                r["base_risk_rate"] = cols["risk"][:k].mean()
            else:
                r["usage_dev_z"] = r["rate_dev_120"] = r["base_risk_rate"] = 0.0
            h = g.hour_of_day.iloc[i]                          # takvim + görev durumu (to-do'dan bilinir)
            r.update(hour_sin=np.sin(2 * np.pi * h / 24), hour_cos=np.cos(2 * np.pi * h / 24),
                     is_evening=int(18 <= h <= 23), is_weekend=int(g.start_time.iloc[i].dayofweek >= 5),
                     responsibilities_met=int(g.responsibilities_met.iloc[i]))
            out.append(r)
    return pd.DataFrame(out)


def feature_cols(f: pd.DataFrame):
    return [c for c in f.columns if c not in META]