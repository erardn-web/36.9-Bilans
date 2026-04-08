"""tests/questionnaires/vestibulaire.py — ABC Scale, Mini-BESTest, VADL"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── ABC Scale Activities-specific Balance Confidence ─────────────────────────
@register_test
class MiniBESTest(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"mini_bestest","nom":"Mini-BESTest — Équilibre","tab_label":"🧍 Mini-BESTest",
                "categorie":"test_clinique","tags":["équilibre","marche","Parkinson","neurologie","gériatrie"],
                "description":"Mini Balance Evaluation Systems Test — 14 items /28, évaluation équilibre multisystème"}
    ITEMS=[
        ("mb_q1","Assise debout sans aide"),("mb_q2","Debout sur pointe des pieds"),
        ("mb_q3","Debout sur une jambe (droite)"),("mb_q4","Debout sur une jambe (gauche)"),
        ("mb_q5","Correction compensatoire — avant"),("mb_q6","Correction compensatoire — arrière"),
        ("mb_q7","Correction compensatoire — côté"),("mb_q8","Équilibre dans station debout"),
        ("mb_q9","Équilibre debout les yeux fermés sur surface molle"),("mb_q10","Inclinaison — tilt"),
        ("mb_q11","Changement de vitesse de marche"),("mb_q12","Marche avec rotation de tête — horizontale"),
        ("mb_q13","Marche et pivot — retour"),("mb_q14","Franchissement d'obstacles"),
    ]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS]+["mini_bestest_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score total (/28)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
            {"key": "detail_items", "label": "Détail des items", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🧍 Mini-BESTest — Équilibre</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Chaque item 0-2 (0=incapable, 1=aide/correction, 2=normal). Score /28. Seuil risque chutes ≤ 20.</div>', unsafe_allow_html=True)
        collected={}; total=0
        for k,label in self.ITEMS:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else None
            except: stored=None
            chosen=st.radio(f"**{label}**",[None,0,1,2],
                format_func=lambda x:"— Non renseigné —" if x is None else ["0 — Incapable","1 — Avec aide/compensation","2 — Normal"][x],
                index=(stored+1) if stored is not None else 0,
                key=f"{key_prefix}_{k}",horizontal=True)
            collected[k]=chosen if chosen is not None else ""
            if chosen is not None: total+=chosen
        collected["mini_bestest_score"]=total
        color="#388e3c" if total>=25 else "#f57c00" if total>=20 else "#d32f2f"
        msg="Équilibre normal" if total>=25 else "Risque modéré" if total>=20 else "Risque élevé de chutes"
        st.markdown(f'<div class="score-box" style="background:{color}">Mini-BESTest : {total}/28 — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("mini_bestest_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=25 else "#f57c00" if s>=20 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/28","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("mini_bestest_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("mini_bestest_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Mini-BESTest",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=20,line_dash="dot",line_color="#d32f2f",annotation_text="Risque chutes ≤20")
        fig.update_layout(yaxis=dict(range=[0,30],title="Score /28"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('mini_bestest', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Mini-BESTest":r.get("mini_bestest_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── FES-I Falls Efficacy Scale International ──────────────────────────────────