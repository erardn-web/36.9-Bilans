"""tests/questionnaires/other_scores.py — IKDC, CSI, QBPDS, ATRS, WOSI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── IKDC ─────────────────────────────────────────────────────────────────────
@register_test
class IKDC(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"ikdc","nom":"IKDC — Genou","tab_label":"📊 IKDC","categorie":"questionnaire",
                "tags":["genou","LCA","fonctionnel","ligament"],
                "description":"International Knee Documentation Committee — score fonctionnel genou /100"}
    @classmethod
    def fields(cls): return [f"ikdc_q{i}" for i in range(1,11)]+["ikdc_score"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📊 IKDC — Genou</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">10 questions sur la fonction du genou. Score 0 = incapacité maximale · 100 = aucune limitation.</div>', unsafe_allow_html=True)
        collected={}
        questions=[
            ("ikdc_q1","Quelle est l'activité la plus intense que vous puissiez pratiquer sans douleur sévère ?",[
                (0,"Pas d'activité physique"),(1,"Activités légères (marche, ménage)"),(2,"Activités modérées (nage, vélo)"),
                (3,"Activités intenses (jogging, tennis)"),(4,"Activités très intenses (saut, pivotement)")]),
            ("ikdc_q2","À quelle fréquence votre genou est-il douloureux ?",[
                (0,"Constamment"),(2,"Quotidiennement"),(4,"Hebdomadairement"),(6,"Mensuellement"),(8,"Jamais")]),
            ("ikdc_q3","Si vous avez de la douleur, quelle est son intensité ?",[
                (0,"10/10 — Extrême"),(2,"7-9/10 — Sévère"),(4,"4-6/10 — Modérée"),(6,"1-3/10 — Légère"),(8,"Aucune douleur")]),
            ("ikdc_q4","Quelle est la rigidité de votre genou ?",[
                (0,"Extrême"),(2,"Sévère"),(4,"Modérée"),(6,"Légère"),(8,"Aucune")]),
            ("ikdc_q5","Quel gonflement avez-vous dans le genou ?",[
                (0,"Extrême"),(2,"Sévère"),(4,"Modéré"),(6,"Léger"),(8,"Aucun")]),
            ("ikdc_q6","Votre genou est-il instable (dérobements) ?",[
                (0,"Constamment"),(2,"Souvent"),(4,"Parfois"),(6,"Rarement"),(8,"Jamais")]),
            ("ikdc_q7","À quelle activité êtes-vous limité(e) ?",[
                (0,"Incapable de travailler"),(2,"Seulement travail léger"),(4,"Travail modéré"),(6,"Toutes activités quotidiennes"),(8,"Aucune limitation")]),
            ("ikdc_q8","Quelle activité sportive ?",[
                (0,"Aucune"),(2,"Activités légères"),(4,"Activités modérées"),(6,"Sport intensif non compétitif"),(8,"Compétition à niveau habituel")]),
            ("ikdc_q9","Comment évaluez-vous votre genou ?",[
                (0,"Très mauvais"),(2,"Mauvais"),(4,"Moyen"),(6,"Bon"),(8,"Normal")]),
            ("ikdc_q10","Quelle note sur 10 donneriez-vous à votre genou ?",[
                (0,"0-2"),(2,"3-4"),(4,"5-6"),(6,"7-8"),(8,"9-10")]),
        ]
        total=0
        for k,label,opts in questions:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else None
            except: stored=None
            vals=[o[0] for o in opts]; opts_ext=[None]+vals
            def _fmt(x,o=opts): return "— Non renseigné —" if x is None else next(l for s,l in o if s==x)
            default=(vals.index(stored)+1) if stored in vals else 0
            chosen=st.radio(f"**{label}**",opts_ext,format_func=_fmt,index=default,key=f"{key_prefix}_{k}",horizontal=True)
            collected[k]=chosen if chosen is not None else ""
            if chosen is not None: total+=chosen
        score=round(total/0.8)
        collected["ikdc_score"]=min(score,100)
        color="#388e3c" if score>=75 else "#f57c00" if score>=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">IKDC : {min(score,100)}/100</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("ikdc_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=75 else "#f57c00" if s>=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("ikdc_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("ikdc_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="IKDC",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="IKDC /100"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"IKDC":r.get("ikdc_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── CSI Central Sensitization Inventory ──────────────────────────────────────