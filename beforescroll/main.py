"""BeforeScroll MVP: simülasyon -> özellikler -> model.   Kullanım: python main.py [--sweep]"""
import argparse
from pathlib import Path

from config import Config
from features import build_features, feature_cols
from model import horizon_sweep, importance, train_evaluate
from simulate import simulate

def main():
    ap = argparse.ArgumentParser()
    d = Config()
    ap.add_argument("--users", type=int, default=d.n_users)
    ap.add_argument("--days", type=int, default=d.n_days)
    ap.add_argument("--horizon", type=int, default=d.horizon_min)
    ap.add_argument("--seed", type=int, default=d.seed)
    ap.add_argument("--out", default=d.out_dir)
    ap.add_argument("--sweep", action="store_true", help="1/5/10/30 dk ufuk taraması")
    a = ap.parse_args()
    cfg = Config(n_users=a.users, n_days=a.days, horizon_min=a.horizon, seed=a.seed, out_dir=a.out)
    out = Path(cfg.out_dir); out.mkdir(parents=True, exist_ok=True)

    df = simulate(cfg); df.to_csv(out / "sessions.csv", index=False)
    print(f"Veri: {len(df)} oturum | risk oranı {df.risk_label.mean():.3f}")
    print("Risk oranı (responsibilities_met'e göre, bağımlılık yapıcı uygulamalar):")
    print(df[df.is_addictive_app].groupby("responsibilities_met")
          .agg(oturum=("risk_label", "size"), risk=("risk_label", "mean"), ort_dk=("usage_minutes", "mean"))
          .round(3).to_string())

    f = build_features(df, cfg.horizon_min); f.to_csv(out / f"features_h{cfg.horizon_min}.csv", index=False)
    print(f"\nÖzellikler: {f.shape[0]} satır x {len(feature_cols(f))} özellik | ufuk={cfg.horizon_min} dk")
    res = train_evaluate(f, cfg.seed)
    print("\nÖzellik önemi (AUPRC düşüşü):\n" + importance(res, feature_cols(f), seed=cfg.seed).round(4).to_string())

    if a.sweep:
        s = horizon_sweep(df, cfg.seed); s.to_csv(out / "horizon_sweep.csv", index=False)
        print("\nUfuk taraması:\n" + s.round(3).to_string(index=False))


if __name__ == "__main__":
    main()