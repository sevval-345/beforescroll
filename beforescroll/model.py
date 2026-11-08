"""Zamana göre bölme, eğitim, sorumluluk-duyarlı eşik ve ufuk taraması."""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score as ap, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from features import build_features, feature_cols

def time_split(f, a=0.70, b=0.85):
    qa, qb = f.start_time.quantile([a, b])
    return f[f.start_time <= qa], f[(f.start_time > qa) & (f.start_time <= qb)], f[f.start_time > qb]


def _thresholds(y, p, met):
    """Sorumluluk durumuna göre ayrı eşik: görev bekliyorsa (met=0) sistem daha hassas olabilir."""
    grid, thr = np.linspace(0.05, 0.95, 91), {}
    for m in (0, 1):
        mask = (met == m).to_numpy()
        ok = mask.sum() >= 30 and 0 < y[mask].sum() < mask.sum()
        thr[m] = grid[int(np.argmax([f1_score(y[mask], p[mask] >= t, zero_division=0) for t in grid]))] if ok else 0.5
    return thr


def train_evaluate(f, seed=42, verbose=True):
    cols = feature_cols(f)
    tr, va, te = time_split(f)
    models = {
        "LogReg": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced")),
        "HistGB": HistGradientBoostingClassifier(learning_rate=0.06, max_depth=4, max_iter=250,
                                                 class_weight="balanced", random_state=seed),
    }
    res = {"prevalence": te.risk_label.mean()}
    for name, m in models.items():
        m.fit(tr[cols], tr.risk_label)
        thr = _thresholds(va.risk_label.to_numpy(), m.predict_proba(va[cols])[:, 1], va.responsibilities_met)
        p, y = m.predict_proba(te[cols])[:, 1], te.risk_label.to_numpy()
        pred = p >= te.responsibilities_met.map(thr).to_numpy()
        res[name] = dict(auprc=ap(y, p), roc_auc=roc_auc_score(y, p), precision=precision_score(y, pred, zero_division=0),
                         recall=recall_score(y, pred, zero_division=0), f1=f1_score(y, pred, zero_division=0),
                         thr_pending=thr[0], thr_met=thr[1])
        if verbose:
            print(f"  {name:<7}" + "  ".join(f"{k}={v:.3f}" for k, v in res[name].items()))
    res["model"], res["test"] = models["HistGB"], te
    if verbose:
        print(f"  Taban çizgisi (pozitif oranı) = {res['prevalence']:.3f}")
    return res


def importance(res, cols, top=10, seed=42):
    te = res["test"]
    pi = permutation_importance(res["model"], te[cols], te.risk_label, scoring="average_precision",
                                n_repeats=5, random_state=seed)
    return pd.Series(pi.importances_mean, index=cols).sort_values(ascending=False).head(top)


def horizon_sweep(df, seed, horizons=(1, 5, 10, 30)):
    rows = []
    for h in horizons:
        print(f"[Ufuk={h} dk]")
        r = train_evaluate(build_features(df, h), seed)
        rows.append(dict(horizon_min=h, auprc=r["HistGB"]["auprc"], recall=r["HistGB"]["recall"],
                         baseline=r["prevalence"]))
    return pd.DataFrame(rows)