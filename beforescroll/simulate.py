"""Kurallı sentetik veri üretimi (her satır = bir uygulama oturumu)."""
import numpy as np
import pandas as pd

from  config import ADDICTIVE, APPS, HOURLY_RATE, NAMES, Config


def _app_probs(hour, weekday, vuln, met):
    w = np.array([1.0, 1.0, 0.8, 0.8, 0.5, 0.5, 1.2])
    if 9 <= hour < 18 and weekday:                    # mesai: Slack baskın
        w[NAMES.index("Slack")] *= 4.0
        w[ADDICTIVE] *= 0.4
    if 18 <= hour <= 23:                              # akşam: bağımlılık yapıcılar artar
        w[ADDICTIVE] *= 2.2 + 0.5 * vuln
    if hour < 6:                                      # gece
        for a in ("TikTok", "PUBG", "YouTube"):
            w[NAMES.index(a)] *= 2.0
    if not met:                                       # görev bekliyor: kaçamak kullanım biraz azalır
        w[ADDICTIVE] *= 0.7
    return w / w.sum()


def simulate(cfg: Config) -> pd.DataFrame:
    """
    Korelasyonlar: akşam yoğunluğu | notifications~Poisson | times_opened ∝ bildirim |
    usage ~ LogNormal(saat, açılış, momentum, sıkılma) | bildirim yoksa Boredom.
    responsibilities_met: kullanıcı-gün bazında bir "görev bitiş saati" vardır (yatkın
    kullanıcılar erteler); bu saatten sonra 1 olur. Bekleyen görev varken sıkılma-tetiklemeli
    kullanım artar (erteleme davranışı).
    """
    rng = np.random.default_rng(cfg.seed)
    t0 = pd.Timestamp("2025-01-06")                   # pazartesi
    rows = []
    for uid in range(cfg.n_users):
        vuln = float(np.clip(rng.normal(0, 1), -1.5, 1.5))
        nscale = rng.uniform(0.6, 1.6)
        carry = cursor = 0.0
        for day in range(cfg.n_days):
            weekday = (t0 + pd.Timedelta(days=day)).dayofweek < 5
            done_h = float(np.clip(rng.normal((17.5 if weekday else 14) + 1.5 * vuln, 2), 11, 23.5))
            mood = rng.normal(0, 0.25)
            for hour in range(24):
                lam = max(HOURLY_RATE[hour] * (1 + 0.25 * vuln) * np.exp(mood) * (1 + 2 * carry), 0.01)
                for off in np.sort(rng.uniform(0, 60, rng.poisson(lam))):
                    start = max(day * 1440 + hour * 60 + off, cursor + 1)
                    carry *= np.exp(-(start - cursor) / 60)          # momentum sönümü
                    h = int(start % 1440 // 60)
                    met = int(start % 1440 / 60 >= done_h)
                    evening = float(18 <= h <= 23)
                    app = rng.choice(NAMES, p=_app_probs(h, weekday, vuln, met))
                    cat, base, nrate, addictive = APPS[app]

                    notif = int(rng.poisson(nrate * (1.4 if evening else 1) * nscale * 0.8))
                    p_notif = (1 - np.exp(-0.6 * notif)) * (1.0 if met else 0.8)
                    boredom = float(not (notif > 0 and rng.random() < p_notif))
                    opened = 1 + int(rng.poisson(0.8 * notif + 0.3 * boredom))
                    adv = 1.0 if addictive else 0.3
                    mu = (np.log(base) + adv * (0.35 * evening + 0.8 * carry + 0.2 * boredom + 0.15 * vuln)
                          + 0.2 * opened)
                    usage = float(np.clip(rng.lognormal(mu, 0.35), 0.5, 180))

                    rows.append(dict(
                        user_id=uid, start_time=t0 + pd.Timedelta(minutes=float(start)), hour_of_day=h,
                        app_name=app, app_category=cat, notifications=notif, times_opened=opened,
                        usage_minutes=round(usage, 2),
                        trigger_type="Boredom_Triggered" if boredom else "Notification_Triggered",
                        responsibilities_met=met, is_addictive_app=addictive))
                    cursor = start + usage
                    if addictive:
                        carry = min(1.0, carry + 0.25 * usage / 30)

    df = pd.DataFrame(rows).sort_values(["user_id", "start_time"]).reset_index(drop=True)
    return _label(df, cfg, rng)


def _label(df, cfg, rng):
    """
    risk_label kuralı (yalnızca bağımlılık yapıcı uygulamalarda):
      met==0 -> usage >= pending_min           (düşük süre bile riskli)
      met==1 -> usage >= kişisel_eşik * tolerance (esnek mola toleransı)
    """
    thr = (df[df.is_addictive_app].groupby("user_id").usage_minutes.quantile(cfg.risk_quantile)
           .clip(lower=cfg.min_risk_minutes))
    personal = df.user_id.map(thr).fillna(cfg.min_risk_minutes)
    limit = np.where(df.responsibilities_met == 0, cfg.pending_min, personal * cfg.tolerance)
    df["risk_label"] = (df.is_addictive_app & (df.usage_minutes >= limit)).astype(int)
    flip = rng.random(len(df)) < cfg.label_noise
    df.loc[flip, "risk_label"] ^= 1
    return df