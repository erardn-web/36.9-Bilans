"""tests/questionnaires/faos.py — FAOS (Foot and Ankle Outcome Score)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

# FAOS sous-échelles simplifiées (items représentatifs)
FAOS_PAIN=[
    ("faos_p1","Fréquence de la douleur à la cheville/pied"),("faos_p2","Tordre/pivoter"),
    ("faos_p3","Étendre complètement"),("faos_p4","Plier complètement"),
    ("faos_p5","Marcher sur terrain plat"),("faos_p6","Monter/descendre escaliers"),
    ("faos_p7","La nuit au lit"),("faos_p8","Assis ou couché"),("faos_p9","Debout"),
]
FAOS_SYMP=[
    ("faos_s1","Gonflement de la cheville/pied"),("faos_s2","Craquements ou bruits"),
    ("faos_s3","Accrochages"),("faos_s4","Amplitude des mouvements"),("faos_s5","Raideur matinale"),
]
FAOS_ADL=[
    ("faos_a1","Descendre escaliers"),("faos_a2","Monter escaliers"),("faos_a3","Se relever"),
    ("faos_a4","Rester debout"),("faos_a5","Se pencher"),("faos_a6","Marcher plat"),
    ("faos_a7","Entrer/sortir voiture"),("faos_a8","Courses"),("faos_a9","Chaussettes"),
    ("faos_a10","Se lever du lit"),("faos_a11","Enlever chaussettes"),("faos_a12","Couché"),
    ("faos_a13","Baignoire"),("faos_a14","S'asseoir"),("faos_a15","Toilettes"),
    ("faos_a16","Tâches lourdes"),("faos_a17","Tâches légères"),
]
FAOS_SPORT=[
    ("faos_sp1","S'accroupir"),("faos_sp2","Courir"),("faos_sp3","Sauter"),
    ("faos_sp4","Pivoter"),("faos_sp5","S'agenouiller"),
]
FAOS_QOL=[
    ("faos_q1","Conscience du problème"),("faos_q2","Modification mode de vie"),
    ("faos_q3","Manque de confiance"),("faos_q4","Difficultés générales"),
]
OPTS=["0 — Aucune","1 — Légère","2 — Modérée","3 — Sévère","4 — Extrême"]


def _sub(data, items):
    vals=[]
    for k,_ in items:
        try: vals.append(int(float(data.get(k,""))))
        except: pass
    return round(100-(sum(vals)/len(items))*25,1) if len(vals)==len(items) else None


@register_test
class FAOS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"faos","nom":"FAOS — Cheville/Pied","tab_label":"🦶 FAOS","categorie":"questionnaire",
                "tags":["cheville","pied","entorse","tendinopathie","fonctionnel"],
                "description":"Foot and Ankle Outcome Score — 5 sous-échelles /100"}

    @classmethod
    def fields(cls):
        all_items=FAOS_PAIN+FAOS_SYMP+FAOS_ADL+FAOS_SPORT+FAOS_QOL
        return [k for k,_ in all_items]+["faos_pain","faos_symptoms","faos_adl","faos_sport","faos_qol"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "sous_scores", "label": "Sous-scores FAOS", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦶 FAOS — Cheville/Pied</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = aucune difficulté → 100 = difficulté maximale (scores inversés : 100 = meilleure fonction)</div>', unsafe_allow_html=True)
        collected={}
        def _sec(title,items,sfx):
            with st.expander(title,expanded=False):
                for k,label in items:
                    raw=lv(k,None)
                    try: stored=int(float(raw)) if raw not in (None,"","None") else None
                    except: stored=None
                    chosen=st.radio(label,[None]+list(range(5)),
                        format_func=lambda x,o=OPTS:"— Non renseigné —" if x is None else o[x],
                        index=(stored+1) if stored is not None else 0,
                        key=f"{key_prefix}_{sfx}_{k}",horizontal=True)
                    collected[k]=chosen if chosen is not None else ""
        _sec("Douleur",FAOS_PAIN,"pain"); _sec("Symptômes",FAOS_SYMP,"symp")
        _sec("AVQ",FAOS_ADL,"adl"); _sec("Sport",FAOS_SPORT,"sport"); _sec("QoL",FAOS_QOL,"qol")
        for items,field in [(FAOS_PAIN,"faos_pain"),(FAOS_SYMP,"faos_symptoms"),(FAOS_ADL,"faos_adl"),(FAOS_SPORT,"faos_sport"),(FAOS_QOL,"faos_qol")]:
            s=_sub(collected,items); collected[field]=s if s is not None else ""
        st.markdown("#### Résultats")
        cols=st.columns(5)
        for col,lbl,f in zip(cols,["Douleur","Symptômes","AVQ","Sport","QoL"],["faos_pain","faos_symptoms","faos_adl","faos_sport","faos_qol"]):
            v=collected.get(f,"")
            try:
                v=float(v); c="#388e3c" if v>=70 else "#f57c00" if v>=40 else "#d32f2f"
                col.markdown(f'<div class="score-box" style="background:{c};font-size:.9rem">{lbl}<br><b>{v:.0f}</b></div>',unsafe_allow_html=True)
            except: col.markdown(f'<div style="text-align:center;color:#aaa">{lbl}<br>—</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        scores=[]
        for f in ["faos_pain","faos_adl","faos_sport","faos_qol"]:
            try: scores.append(float(data.get(f,"")))
            except: pass
        if not scores: return {"score":None,"interpretation":"","color":"#888","details":{}}
        avg=round(sum(scores)/len(scores),1)
        color="#388e3c" if avg>=70 else "#f57c00" if avg>=40 else "#d32f2f"
        return {"score":avg,"interpretation":f"Moy. {avg}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        for f in ["faos_pain","faos_adl"]:
            try:
                if float(data.get(f,""))>=0: return True
            except: pass
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("faos_pain","Douleur","#2B57A7"),("faos_adl","AVQ","#1D9E75"),("faos_sport","Sport","#D85A30")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers",name=l,line=dict(color=c,width=2.5),marker=dict(size=8)))
        fig.update_layout(yaxis=dict(range=[0,105],title="FAOS /100"),height=320,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Douleur":r.get("faos_pain","—"),"AVQ":r.get("faos_adl","—"),"Sport":r.get("faos_sport","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
