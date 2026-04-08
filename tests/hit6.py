"""tests/questionnaires/misc_scores.py — Cumberland CAIT, IKDC, Tegner, DHI, HIT-6"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Cumberland Ankle Instability Tool (CAIT) ──────────────────────────────────
@register_test
class HIT6(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"hit6","nom":"HIT-6 — Impact des céphalées","tab_label":"🤕 HIT-6","categorie":"questionnaire",
                "tags":["céphalées","migraines","tête","impact","incapacité"],
                "description":"Headache Impact Test-6 — 6 items, impact des maux de tête /78"}
    @classmethod
    def fields(cls): return [f"hit6_q{i}" for i in range(1,7)]+["hit6_score"]
    OPTS={"never":6,"rarely":8,"sometimes":10,"very_often":11,"always":13}
    OPTS_FR={"never":"Jamais (6)","rarely":"Rarement (8)","sometimes":"Parfois (10)","very_often":"Très souvent (11)","always":"Toujours (13)"}
    QUESTIONS=[
        "Quand vous avez des maux de tête, leur intensité est-elle sévère ?",
        "Vos maux de tête vous empêchent-ils de mener à bien vos activités quotidiennes ?",
        "Vous arrive-t-il de souhaiter vous allonger à cause de vos maux de tête ?",
        "Au cours des 4 dernières semaines, vous êtes-vous senti(e) trop fatigué(e) à cause de vos maux de tête ?",
        "Au cours des 4 dernières semaines, avez-vous eu envie de ne rien faire de spécial à cause de vos maux de tête ?",
        "Au cours des 4 dernières semaines, avez-vous trouvé vos capacités de concentration limitées à cause de vos maux de tête ?",
    ]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score total (/78)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🤕 HIT-6 — Impact des céphalées</div>', unsafe_allow_html=True)
        collected={}; total=0
        for i,q in enumerate(self.QUESTIONS,1):
            k=f"hit6_q{i}"
            raw=lv(k,"never")
            stored=raw if raw in self.OPTS else "never"
            val=st.selectbox(q,list(self.OPTS_FR.keys()),index=list(self.OPTS.keys()).index(stored),
                format_func=lambda x:self.OPTS_FR[x],key=f"{key_prefix}_{k}")
            collected[k]=val; total+=self.OPTS[val]
        collected["hit6_score"]=total
        color="#d32f2f" if total>=60 else "#f57c00" if total>=56 else "#388e3c"
        msg="Impact sévère" if total>=60 else "Impact substantiel" if total>=56 else "Impact moindre"
        st.markdown(f'<div class="score-box" style="background:{color}">HIT-6 : {total}/78 — {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("hit6_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s>=60 else "#f57c00" if s>=56 else "#388e3c"
        return {"score":s,"interpretation":f"{s:.0f}/78","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("hit6_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("hit6_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="HIT-6",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=56,line_dash="dot",line_color="#f57c00",annotation_text="Impact substantiel ≥56")
        fig.add_hline(y=60,line_dash="dot",line_color="#d32f2f",annotation_text="Impact sévère ≥60")
        fig.update_layout(yaxis=dict(range=[36,80],title="HIT-6 /78"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"HIT-6":r.get("hit6_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
