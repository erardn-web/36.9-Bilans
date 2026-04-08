"""tests/questionnaires/bctq.py — BCTQ (Boston Carpal Tunnel Questionnaire)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

BCTQ_SSS = [  # Symptom Severity Scale
    ("bctq_s1","Quelle est l'intensité de votre douleur nocturne au poignet/main ?",
     ["1 — Aucune","2 — Légère","3 — Modérée","4 — Sévère","5 — Très sévère"]),
    ("bctq_s2","Votre douleur nocturne vous réveille-t-elle ?",
     ["1 — Non","2 — 1×/nuit","3 — 2×/nuit","4 — >2×/nuit","5 — Toutes les nuits"]),
    ("bctq_s3","Avez-vous une douleur diurne ?",
     ["1 — Aucune","2 — Légère","3 — Modérée","4 — Sévère","5 — Très sévère"]),
    ("bctq_s4","À quelle fréquence avez-vous une douleur diurne ?",
     ["1 — Jamais","2 — 1–2×/jour","3 — 3–5×/jour","4 — >5×/jour","5 — Continue"]),
    ("bctq_s5","Combien de temps dure en moyenne votre douleur diurne ?",
     ["1 — Pas de douleur","2 — <10 min","3 — 10–60 min","4 — >60 min","5 — Continue"]),
    ("bctq_s6","Avez-vous des engourdissements ?",
     ["1 — Aucun","2 — Léger","3 — Modéré","4 — Sévère","5 — Très sévère"]),
    ("bctq_s7","Avez-vous des fourmillements ?",
     ["1 — Aucun","2 — Léger","3 — Modéré","4 — Sévère","5 — Très sévère"]),
    ("bctq_s8","À quelle fréquence avez-vous des engourdissements nocturnes ?",
     ["1 — Jamais","2 — 1×/nuit","3 — 2×/nuit","4 — >2×/nuit","5 — Toutes les nuits"]),
    ("bctq_s9","Avez-vous une faiblesse dans la main ?",
     ["1 — Aucune","2 — Légère","3 — Modérée","4 — Sévère","5 — Très sévère"]),
    ("bctq_s10","Avez-vous des difficultés à attraper des petits objets ?",
     ["1 — Aucune","2 — Légère","3 — Modérée","4 — Sévère","5 — Très sévère"]),
    ("bctq_s11","Êtes-vous capable de distinguer le chaud et le froid ?",
     ["1 — Oui, normalement","2 — Légère difficulté","3 — Difficulté modérée","4 — Grande difficulté","5 — Incapable"]),
]
BCTQ_FSS = [  # Functional Status Scale
    ("bctq_f1","Écrire"),("bctq_f2","Boutonner des vêtements"),("bctq_f3","Tenir un livre"),
    ("bctq_f4","Tenir le téléphone"),("bctq_f5","Ouvrir des bocaux"),
    ("bctq_f6","Tâches ménagères"),("bctq_f7","Porter des sacs d'épicerie"),
    ("bctq_f8","Se laver, se doucher"),
]
FUNC_OPTS=["1 — Aucune difficulté","2 — Légère difficulté","3 — Difficulté modérée","4 — Grande difficulté","5 — Incapable"]


@register_test
class BCTQ(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"bctq","nom":"BCTQ — Canal carpien","tab_label":"🤚 BCTQ","categorie":"questionnaire",
                "tags":["canal carpien","poignet","main","neuropathique"],
                "description":"Boston Carpal Tunnel Questionnaire — SSS (symptômes) + FSS (fonction)"}

    @classmethod
    def fields(cls):
        return ([k for k,*_ in BCTQ_SSS]+[k for k,_ in BCTQ_FSS]+["bctq_sss","bctq_fss"])

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "sous_scores", "label": "SSS + FSS", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🤚 BCTQ — Canal carpien</div>', unsafe_allow_html=True)
        collected={}
        with st.expander("Échelle des symptômes (SSS)",expanded=True):
            for k,label,opts in BCTQ_SSS:
                raw=lv(k,None)
                try: stored=int(float(raw)) if raw not in (None,"","None") else None
                except: stored=None
                vals=[None]+list(range(1,6))
                chosen=st.radio(label,vals,format_func=lambda x,o=opts:"— Non renseigné —" if x is None else o[x-1],
                    index=(stored) if stored is not None else 0,key=f"{key_prefix}_{k}",horizontal=True)
                collected[k]=chosen if chosen is not None else ""
        with st.expander("Échelle fonctionnelle (FSS)",expanded=False):
            for k,label in BCTQ_FSS:
                raw=lv(k,None)
                try: stored=int(float(raw)) if raw not in (None,"","None") else None
                except: stored=None
                chosen=st.radio(label,[None]+list(range(1,6)),
                    format_func=lambda x,o=FUNC_OPTS:"— Non renseigné —" if x is None else o[x-1],
                    index=(stored) if stored is not None else 0,key=f"{key_prefix}_{k}",horizontal=True)
                collected[k]=chosen if chosen is not None else ""
        sss_vals=[collected[k] for k,*_ in BCTQ_SSS if collected.get(k,"") != ""]
        fss_vals=[collected[k] for k,_ in BCTQ_FSS if collected.get(k,"") != ""]
        sss=round(sum(sss_vals)/len(sss_vals),2) if len(sss_vals)==11 else ""
        fss=round(sum(fss_vals)/len(fss_vals),2) if len(fss_vals)==8 else ""
        collected.update({"bctq_sss":sss,"bctq_fss":fss})
        if sss != "" and fss != "":
            color="#388e3c" if sss<=2 and fss<=2 else "#f57c00" if sss<=3 else "#d32f2f"
            st.markdown(f'<div class="score-box" style="background:{color}">SSS : {sss}/5 | FSS : {fss}/5</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("bctq_sss",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=2 else "#f57c00" if s<=3 else "#d32f2f"
        fss=data.get("bctq_fss","—")
        return {"score":s,"interpretation":f"SSS:{s}/5 FSS:{fss}/5","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("bctq_sss",""))>0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("bctq_sss","SSS","#2B57A7"),("bctq_fss","FSS","#1D9E75")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=l,line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v:.1f}" for v in yp],textposition="top center"))
        fig.add_hline(y=2,line_dash="dot",line_color="#388e3c",annotation_text="Seuil mild")
        fig.update_layout(yaxis=dict(range=[1,5.5],title="Score /5"),height=300,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"SSS":r.get("bctq_sss","—"),"FSS":r.get("bctq_fss","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
