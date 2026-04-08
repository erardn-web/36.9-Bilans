"""tests/questionnaires/rhumato_geriatrie.py — HAQ, BASDAI, DAS28, Frailty, FRAIL, Gait Speed"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── HAQ Health Assessment Questionnaire ──────────────────────────────────────
@register_test
class FRAILScale(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"frail_scale","nom":"FRAIL Scale — Dépistage fragilité","tab_label":"👴 FRAIL",
                "categorie":"questionnaire","tags":["fragilité","gériatrie","dépistage","rapide"],
                "description":"FRAIL Scale — 5 critères de dépistage rapide de la fragilité /5"}
    @classmethod
    def fields(cls): return ["frail_fatigue","frail_resistance","frail_ambulation","frail_illness","frail_weight","frail_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score FRAIL", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">👴 FRAIL Scale — Dépistage fragilité</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0-1 : robuste · 2 : pré-fragile · 3-5 : fragile</div>', unsafe_allow_html=True)
        collected={}; total=0
        criteria=[
            ("frail_fatigue","F — Fatigue","Vous sentez-vous fatigué(e) la plupart du temps ?"),
            ("frail_resistance","R — Résistance","Avez-vous du mal à monter une volée d'escaliers ?"),
            ("frail_ambulation","A — Marche","Avez-vous du mal à marcher une centaine de mètres ?"),
            ("frail_illness","I — Illnesses","Avez-vous 5 maladies chroniques ou plus ?"),
            ("frail_weight","L — Poids","Avez-vous perdu plus de 5% de votre poids en 1 an ?"),
        ]
        for k,label,desc in criteria:
            raw=lv(k,None); stored=str(raw) in ("1","True","Oui")
            val=st.checkbox(f"**{label}** — {desc}",value=stored,key=f"{key_prefix}_{k}")
            collected[k]=1 if val else 0
            if val: total+=1
        collected["frail_score"]=total
        color="#388e3c" if total<=1 else "#f57c00" if total==2 else "#d32f2f"
        msg="Robuste" if total<=1 else "Pré-fragile" if total==2 else "Fragile"
        st.markdown(f'<div class="score-box" style="background:{color}">FRAIL : {total}/5 — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("frail_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=1 else "#f57c00" if s==2 else "#d32f2f"
        msg="Robuste" if s<=1 else "Pré-fragile" if s==2 else "Fragile"
        return {"score":s,"interpretation":f"{s:.0f}/5 — {msg}","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data): return str(data.get("frail_score","")).strip() not in ("","None","nan")
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("frail_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="FRAIL",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=3,line_dash="dot",line_color="#d32f2f",annotation_text="Fragile ≥3")
        fig.update_layout(yaxis=dict(range=[-0.2,5.5],title="FRAIL /5"),height=250,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('frail_scale', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"FRAIL":r.get("frail_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── Gait Speed 4m ─────────────────────────────────────────────────────────────