"""tests/questionnaires/vestibulaire.py — ABC Scale, Mini-BESTest, VADL"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── ABC Scale Activities-specific Balance Confidence ─────────────────────────
@register_test
class FESI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"fes_i","nom":"FES-I — Peur de tomber","tab_label":"😨 FES-I",
                "categorie":"questionnaire","tags":["chutes","peur","gériatrie","vestibulaire","équilibre"],
                "description":"Falls Efficacy Scale-International — 16 activités, peur de tomber /64"}
    ITEMS=[
        ("fes_q1","Nettoyer la maison"),("fes_q2","S'habiller/se déshabiller"),
        ("fes_q3","Préparer de simples repas"),("fes_q4","Prendre un bain/douche"),
        ("fes_q5","Faire les courses"),("fes_q6","S'asseoir/se lever d'une chaise"),
        ("fes_q7","Monter/descendre les escaliers"),("fes_q8","Marcher dans le quartier"),
        ("fes_q9","Atteindre quelque chose au-dessus de la tête"),("fes_q10","Se dépêcher pour répondre au téléphone"),
        ("fes_q11","Marcher sur une surface glissante"),("fes_q12","Rendre visite à un ami/proche"),
        ("fes_q13","Marcher dans une foule"),("fes_q14","Marcher sur terrain irrégulier"),
        ("fes_q15","Monter/descendre une pente"),("fes_q16","Assister à un événement social"),
    ]
    OPTS=["1 — Pas du tout","2 — Un peu","3 — Assez","4 — Très préoccupé(e)"]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS]+["fes_i_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score total (/64)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
            {"key": "detail_items", "label": "Détail des items", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">😨 FES-I — Peur de tomber</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">1 = pas du tout préoccupé(e) · 4 = très préoccupé(e). Score 16 (aucune peur) → 64 (peur maximale). Seuil risque modéré ≥ 23.</div>', unsafe_allow_html=True)
        collected={}; total=0
        for k,label in self.ITEMS:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else None
            except: stored=None
            chosen=st.radio(label,[None,1,2,3,4],
                format_func=lambda x,o=self.OPTS:"— Non renseigné —" if x is None else o[x-1],
                index=(stored) if stored is not None else 0,key=f"{key_prefix}_{k}",horizontal=True)
            collected[k]=chosen if chosen is not None else ""
            if chosen is not None: total+=chosen
        collected["fes_i_score"]=total
        color="#388e3c" if total<23 else "#f57c00" if total<31 else "#d32f2f"
        msg="Peur faible" if total<23 else "Peur modérée" if total<31 else "Peur élevée"
        st.markdown(f'<div class="score-box" style="background:{color}">FES-I : {total}/64 — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("fes_i_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<23 else "#f57c00" if s<31 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/64","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("fes_i_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("fes_i_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="FES-I",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=23,line_dash="dot",line_color="#f57c00",annotation_text="Peur modérée ≥23")
        fig.update_layout(yaxis=dict(range=[16,66],title="FES-I /64"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('fes_i', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"FES-I":r.get("fes_i_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
