"""tests/questionnaires/douleur_psy.py — PCS, BPI, PHQ-9, GAD-7, ISI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── PCS Pain Catastrophizing Scale ───────────────────────────────────────────
@register_test
class ISI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"isi","nom":"ISI — Insomnie","tab_label":"🌙 ISI",
                "categorie":"questionnaire","tags":["insomnie","sommeil","douleur chronique","qualité de vie"],
                "description":"Insomnia Severity Index — 7 items /28. Seuil insomnie modérée ≥ 15"}
    ITEMS=[
        ("isi_q1a","Difficulté à s'endormir"),("isi_q1b","Difficulté à rester endormi(e)"),
        ("isi_q1c","Problème de réveil trop tôt"),("isi_q2","Satisfait(e) du sommeil actuel"),
        ("isi_q3","Dans quelle mesure les troubles du sommeil perturbent votre vie quotidienne"),
        ("isi_q4","Comment vos troubles du sommeil sont-ils visibles pour les autres"),
        ("isi_q5","Inquiet(e)/préoccupé(e) par vos problèmes de sommeil"),
    ]
    OPTS_Q1=["0 — Aucune","1 — Légère","2 — Modérée","3 — Sévère","4 — Très sévère"]
    OPTS_Q2=["0 — Très satisfait","1 — Satisfait","2 — Neutre","3 — Insatisfait","4 — Très insatisfait"]
    OPTS_GEN=["0 — Aucunement","1 — Un peu","2 — Assez","3 — Beaucoup","4 — Extrêmement"]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS]+["isi_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score ISI (/28)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🌙 ISI — Indice de sévérité de l\'insomnie</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Score ≤ 7 : pas d\'insomnie · 8-14 : légère · 15-21 : modérée · 22-28 : sévère</div>', unsafe_allow_html=True)
        collected={}; total=0
        opts_map={"isi_q1a":self.OPTS_Q1,"isi_q1b":self.OPTS_Q1,"isi_q1c":self.OPTS_Q1,
                  "isi_q2":self.OPTS_Q2,"isi_q3":self.OPTS_GEN,"isi_q4":self.OPTS_GEN,"isi_q5":self.OPTS_GEN}
        for k,label in self.ITEMS:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(label,list(range(5)),index=stored,format_func=lambda x,o=opts_map[k]:o[x],horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["isi_score"]=total
        color="#388e3c" if total<=7 else "#f57c00" if total<=14 else "#d32f2f"
        msg="Pas d'insomnie" if total<=7 else "Légère" if total<=14 else "Modérée" if total<=21 else "Sévère"
        st.markdown(f'<div class="score-box" style="background:{color}">ISI : {total}/28 — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("isi_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=7 else "#f57c00" if s<=14 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/28","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("isi_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("isi_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="ISI",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=15,line_dash="dot",line_color="#d32f2f",annotation_text="Insomnie modérée ≥15")
        fig.update_layout(yaxis=dict(range=[0,30],title="ISI /28"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('isi', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"ISI":r.get("isi_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
