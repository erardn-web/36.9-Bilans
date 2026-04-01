"""tests/questionnaires/hagos.py — HAGOS (Copenhagen Hip and Groin Outcome Score)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

HAGOS_PAIN=[
    ("hagos_p1","Tordre/pivoter sur la hanche/aine"),("hagos_p2","Étirer complètement la hanche"),
    ("hagos_p3","Plier complètement la hanche"),("hagos_p4","Marcher sur terrain plat"),
    ("hagos_p5","Courir"),("hagos_p6","Sprint"),("hagos_p7","La nuit au lit"),
    ("hagos_p8","Assis"),("hagos_p9","Debout"),("hagos_p10","Donner un coup de pied"),
]
HAGOS_SYMP=[
    ("hagos_s1","Gonflement hanche/aine"),("hagos_s2","Raideur matinale"),
    ("hagos_s3","Raideur après repos"),("hagos_s4","Dérobement"),("hagos_s5","Réduction amplitude"),
    ("hagos_s6","Accrochages"),("hagos_s7","Difficultés à enjamber"),
]
HAGOS_ADL=[
    ("hagos_a1","Descendre escaliers"),("hagos_a2","Monter escaliers"),("hagos_a3","Se relever"),
    ("hagos_a4","Rester debout"),("hagos_a5","Se pencher"),("hagos_a6","Marcher plat"),
    ("hagos_a7","Voiture"),("hagos_a8","Courses"),("hagos_a9","Chaussettes"),
    ("hagos_a10","Lever du lit"),("hagos_a11","Enlever chaussettes"),("hagos_a12","Couché"),
    ("hagos_a13","Baignoire"),("hagos_a14","S'asseoir"),("hagos_a15","Toilettes"),
    ("hagos_a16","Tâches lourdes"),("hagos_a17","Tâches légères"),
]
HAGOS_SPORT=[
    ("hagos_sp1","S'accroupir"),("hagos_sp2","Courir"),("hagos_sp3","Sauter"),
    ("hagos_sp4","Pivoter"),("hagos_sp5","Changer direction"),("hagos_sp6","Frapper balle"),
]
HAGOS_PR=[
    ("hagos_pr1","Niveau d'activité sportive habituel"),
    ("hagos_pr2","Jours d'entraînement par semaine"),
    ("hagos_pr3","Performance sportive"),
]
HAGOS_QOL=[
    ("hagos_q1","Conscience du problème"),("hagos_q2","Modification mode de vie"),
    ("hagos_q3","Confiance"),("hagos_q4","Difficultés générales"),
]
OPTS=["0 — Extrême","1 — Sévère","2 — Modérée","3 — Légère","4 — Aucune"]


def _sub(data,items):
    vals=[]
    for k,_ in items:
        try: vals.append(int(float(data.get(k,""))))
        except: pass
    return round(sum(vals)/len(items)*25,1) if len(vals)==len(items) else None


@register_test
class HAGOS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"hagos","nom":"HAGOS — Hanche/Aine","tab_label":"🦴 HAGOS","categorie":"questionnaire",
                "tags":["hanche","aine","sport","fonctionnel","tendinopathie"],
                "description":"Copenhagen Hip and Groin Outcome Score — 6 sous-échelles /100"}

    @classmethod
    def fields(cls):
        all_items=HAGOS_PAIN+HAGOS_SYMP+HAGOS_ADL+HAGOS_SPORT+HAGOS_PR+HAGOS_QOL
        return [k for k,_ in all_items]+["hagos_pain","hagos_symp","hagos_adl","hagos_sport","hagos_pr","hagos_qol"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦴 HAGOS — Hanche/Aine</div>', unsafe_allow_html=True)
        collected={}
        def _sec(title,items,sfx):
            with st.expander(title,expanded=False):
                for k,label in items:
                    raw=lv(k,None)
                    try: stored=int(float(raw)) if raw not in (None,"","None") else None
                    except: stored=None
                    chosen=st.radio(label,[None]+list(range(5)),
                        format_func=lambda x,o=OPTS:"— Non renseigné —" if x is None else o[4-x] if x is not None else "",
                        index=(stored+1) if stored is not None else 0,
                        key=f"{key_prefix}_{sfx}_{k}",horizontal=True)
                    collected[k]=chosen if chosen is not None else ""
        _sec("Douleur",HAGOS_PAIN,"pain"); _sec("Symptômes",HAGOS_SYMP,"symp")
        _sec("AVQ",HAGOS_ADL,"adl"); _sec("Sport/Loisirs",HAGOS_SPORT,"sport")
        _sec("Participation sportive",HAGOS_PR,"pr"); _sec("Qualité de vie",HAGOS_QOL,"qol")
        for items,field in [(HAGOS_PAIN,"hagos_pain"),(HAGOS_SYMP,"hagos_symp"),(HAGOS_ADL,"hagos_adl"),(HAGOS_SPORT,"hagos_sport"),(HAGOS_PR,"hagos_pr"),(HAGOS_QOL,"hagos_qol")]:
            s=_sub(collected,items); collected[field]=s if s is not None else ""
        st.markdown("#### Résultats")
        cols=st.columns(6)
        for col,lbl,f in zip(cols,["Douleur","Symp.","AVQ","Sport","PR","QoL"],["hagos_pain","hagos_symp","hagos_adl","hagos_sport","hagos_pr","hagos_qol"]):
            v=collected.get(f,"")
            try:
                v=float(v); c="#388e3c" if v>=70 else "#f57c00" if v>=40 else "#d32f2f"
                col.markdown(f'<div class="score-box" style="background:{c};font-size:.8rem">{lbl}<br><b>{v:.0f}</b></div>',unsafe_allow_html=True)
            except: col.markdown(f'<div style="text-align:center;color:#aaa;font-size:.8rem">{lbl}<br>—</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        scores=[]
        for f in ["hagos_pain","hagos_adl","hagos_sport","hagos_qol"]:
            try: scores.append(float(data.get(f,"")))
            except: pass
        if not scores: return {"score":None,"interpretation":"","color":"#888","details":{}}
        avg=round(sum(scores)/len(scores),1)
        color="#388e3c" if avg>=70 else "#f57c00" if avg>=40 else "#d32f2f"
        return {"score":avg,"interpretation":f"Moy. {avg}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        for f in ["hagos_pain","hagos_adl"]:
            try:
                if float(data.get(f,""))>=0: return True
            except: pass
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("hagos_pain","Douleur","#2B57A7"),("hagos_adl","AVQ","#1D9E75"),("hagos_sport","Sport","#D85A30")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers",name=l,line=dict(color=c,width=2.5),marker=dict(size=8)))
        fig.update_layout(yaxis=dict(range=[0,105],title="HAGOS /100"),height=320,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Douleur":r.get("hagos_pain","—"),"Sport":r.get("hagos_sport","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
