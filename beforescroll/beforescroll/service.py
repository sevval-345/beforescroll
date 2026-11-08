"""Model + veri -> panelin ihtiyaç duyduğu canlı durum. Flask'tan bağımsız (test edilebilir)."""
import pandas as pd

from config import Config
from features import build_features, feature_cols
from model import train_evaluate
from simulate import simulate

GUN = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
QUESTIONS = ["Bu akşam neden riskliyim?", "5 dakikalık mola öner", "Bildirimleri nasıl gruplayayım?"]


class Engine:
    def __init__(self, cfg: Config | None = None, user: int | None = None):
        self.cfg = cfg or Config()
        self.df = simulate(self.cfg)
        feat = build_features(self.df, self.cfg.horizon_min)
        self.cols = feature_cols(feat)
        res = train_evaluate(feat, self.cfg.seed, verbose=False)
        self.model, self.m = res["model"], res["HistGB"]

        self.feat = feat
        self.user = user if user is not None else self._pick_demo_user()
        self.row = self._anchor(self.user)
        self.now = self.row.start_time
        d = self.df[(self.df.user_id == self.user) & (self.df.start_time <= self.now)]
        self.day = d[d.start_time.dt.date == self.now.date()]
        self.week = d[d.start_time.dt.normalize() > self.now.normalize() - pd.Timedelta(days=6)]
        self.tasks = [dict(t="Ödev raporunu gönder", done=True), dict(t="45 dakika spor yap", done=True),
                      dict(t="Ders notlarını çalış", done=False)]
        per_day = self.week.groupby(self.week.start_time.dt.date).risk_label.sum()
        self.streak = 0
        for c in reversed(per_day.tolist()):
            if c >= 4:
                break
            self.streak += 1

    def _anchor(self, user):
        """"Şu an": kullanıcının son akşam (18-22) oturumunun özellik satırı."""
        u = self.feat[self.feat.user_id == user]
        ev = u[u.start_time.dt.hour.between(18, 22)]
        return (ev if len(ev) else u).iloc[-1]

    def _pick_demo_user(self):
        """Demo için: görevler bekleyince uyarı veren, bitince vermeyen (hassas/esnek farkı görünen) kullanıcı."""
        for u in self.feat.user_id.unique():
            r = self._anchor(u)
            X = pd.DataFrame([r[self.cols].astype(float)] * 2)
            X["responsibilities_met"] = [0, 1]
            p0, p1 = self.model.predict_proba(X)[:, 1]
            day = self.df[(self.df.user_id == u) & (self.df.start_time.dt.date == r.start_time.date())
                          & (self.df.start_time <= r.start_time)].usage_minutes.sum()
            if p0 >= self.m["thr_pending"] and p1 < self.m["thr_met"] and day < 300:
                return int(u)
        return 0

    # ---- model çağrısı: görev durumu canlı girdi ----
    def _score(self):
        met = all(t["done"] for t in self.tasks)
        X = self.row[self.cols].astype(float).to_frame().T
        X["responsibilities_met"] = int(met)
        p = float(self.model.predict_proba(X)[0, 1])
        thr = self.m["thr_met" if met else "thr_pending"]
        return met, p, thr

    def state(self):
        met, p, thr = self._score()
        level = "low" if p < 0.8 * thr else "mid" if p < thr else "high"
        trend = (self.day.groupby("hour_of_day").usage_minutes.sum()
                 .reindex(range(24), fill_value=0).round(1).tolist())
        pk = max(range(24), key=trend.__getitem__)
        wk = self.week.groupby(self.week.start_time.dt.date).risk_label.sum()
        notif = float((self.week.trigger_type == "Notification_Triggered").mean())
        bw = self.week[(self.week.trigger_type == "Boredom_Triggered") & (self.week.hour_of_day >= 17)]
        bore = bw.hour_of_day.mode()
        mins = int(self.day.usage_minutes.sum())
        return dict(
            score=round(p * 100), level=level, level_text={"low": "Düşük risk", "mid": "Orta risk", "high": "Yüksek risk"}[level],
            warn=bool(p >= thr), horizon_min=self.cfg.horizon_min, met=met, tasks=self.tasks,
            mode=(
                  "Esnek mod: sorumlulukların bitti, mola toleransı 1,25 kat genişletildi.") if met else
                 "Hassas mod: görevlerin sürerken 5 dakikalık sosyal medya kullanımı bile riskli sayılır.",
            dialog=("Son kullanım örüntün normalinden sapıyor" + ("." if met else " ve bekleyen sorumlulukların var.")
                    + " Bu gidişle 10 dakika içinde uzun bir oturum başlayabilir."),
            trend=trend, peak=dict(hour=pk, value=trend[pk]),
            notif_pct=round(notif * 100), bored_pct=100 - round(notif * 100),
            bored_hour=int(bore.iloc[0]) if len(bore) else None,
            week=[[GUN[pd.Timestamp(k).weekday()], int(v)] for k, v in wk.items()],
            stats=dict(unlocks=int(self.day.times_opened.sum()), screen=f"{mins // 60} sa {mins % 60} dk",
                       notif=int((self.day.trigger_type == "Notification_Triggered").sum()), streak=self.streak),
            questions=QUESTIONS,
            source=f"Simülasyon kullanıcısı #{self.user} · Model: HistGB · AUPRC {self.m['auprc']:.2f} · ufuk {self.cfg.horizon_min} dk",
        )

    def set_task(self, i, done):
        self.tasks[i]["done"] = bool(done)
        return self.state()

    def checkin(self, ok):
        self.streak = self.streak + 1 if ok else 0
        msg = (f"Kaydedildi. Odak serin {self.streak} güne çıktı." if ok else
               "Kaydedildi. Sürçme normal; yarın akşam uyarısını daha hassas çalıştıracağız.")
        return dict(message=msg, streak=self.streak)

    def ask(self, q):
        met, p, _ = self._score()
        z = float(self.row["usage_dev_z"])
        if q == QUESTIONS[0]:
            why = [] if met else ["bekleyen sorumluluğun var"]
            if z > 0.3:
                why.append("son kullanımın kişisel normalinden yüksek")
            if self.now.hour >= 18:
                why.append("akşam saatlerinde risk kalıbın yükseliyor")
            return (f"Modelin tahmini %{round(p * 100)}. Nedenler: " + ", ".join(why or ["belirgin bir sapma yok"]) + ".")
        if q == QUESTIONS[1]:
            return "Telefonu başka odaya bırak, su iç ve kalan görevin ilk adımını 5 dakika dene. Süre bitince tekrar karar ver."
        if q == QUESTIONS[2]:
            h = self.state()["bored_hour"]
            return (f"Sosyal medya bildirimlerini 19:00 ve 21:00’de toplu teslim et. "
                    + (f"Sıkılma kaynaklı açılışların {h:02d}:00 civarında yoğunlaştığı için o saatte farkındalık uyarısı da açık kalsın." if h is not None else ""))
        return "Bu soruyu henüz yanıtlayamıyorum."