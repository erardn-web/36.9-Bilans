"""tests/questionnaires/womac.py — WOMAC (Western Ontario and McMaster Universities Osteoarthritis Index)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

WOMAC_PAIN = [
    ("womac_p1","Marcher sur une surface plane"),("womac_p2","Monter ou descendre des escaliers"),
    ("womac_p3","La nuit, au lit"),("womac_p4","En position assise ou couchée"),
    ("womac_p5","En position debout"),
]
WOMAC_STIFF = [
    ("womac_s1","Raideur matinale (réveil)"),("womac_s2","Raideur après repos dans la journée"),
]
WOMAC_FUNC = [
    ("womac_f1","Descendre les escaliers"),("womac_f2","Monter les escaliers"),
    ("womac_f3","Se lever après être assis"),("womac_f4","Rester debout"),
    ("womac_f5","Se pencher pour ramasser un objet"),("womac_f6","Marcher sur terrain plat"),
    ("womac_f7","Entrer/sortir d'une voiture ou transports en commun"),
    ("womac_f8","Faire les courses"),("womac_f9","Mettre des chaussettes"),
    ("womac_f10","Se lever du lit"),("womac_f11","Enlever des chaussettes"),
    ("womac_f12","Rester couché"),("womac_f13","Entrer/sortir de la baignoire"),
    ("womac_f14","S'asseoir"),("womac_f15","S'asseoir/se lever des toilettes"),
    ("womac_f16","Tâches ménagères lourdes"),("womac_f17","Tâches ménagères légères"),
]
OPTS = ["0 — Aucune","1 — Légère","2 — Modérée","3 — Sévère","4 — Extrême"]


@register_test
class WOMAC(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"womac","nom":"WOMAC — Arthrose","tab_label":"🦴 WOMAC","categorie":"questionnaire",
                "tags":["arthrose","genou","hanche","fonctionnel","douleur"],
                "description":"WOMAC — Indice arthrose genou/hanche : douleur, raideur, fonction /96"}

    @classmethod
    def fields(cls):
        all_items = WOMAC_PAIN+WOMAC_STIFF+WOMAC_FUNC
        return [k for k,_ in all_items]+["womac_pain","womac_stiff","womac_func","womac_total"]

    def _sub(self, data, items):
        vals = []
        for k,_ in items:
            try: vals.append(int(float(data.get(k,""))))
            except: pass
        return round(sum(vals)/len(items)*25,1) if len(vals)==len(items) else None

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score WOMAC total", "default": True},
            {"key": "sous_scores", "label": "Sous-scores (douleur, raideur, fonction)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦴 WOMAC — Indice d\'arthrose</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = aucune limitation → 100 = limitation maximale (score normalisé)</div>', unsafe_allow_html=True)
        collected = {}
        def _sec(title, items, sfx):
            with st.expander(title, expanded=False):
                for k,label in items:
                    raw=lv(k,None)
                    try: stored=int(float(raw)) if raw not in (None,"","None") else None
                    except: stored=None
                    chosen=st.radio(label,[None]+list(range(5)),
                        format_func=lambda x,o=OPTS:"— Non renseigné —" if x is None else o[x],
                        index=(stored+1) if stored is not None else 0,
                        key=f"{key_prefix}_{sfx}_{k}",horizontal=True)
                    collected[k]=chosen if chosen is not None else ""
        _sec("Douleur (5 items)",WOMAC_PAIN,"pain")
        _sec("Raideur (2 items)",WOMAC_STIFF,"stiff")
        _sec("Fonction (17 items)",WOMAC_FUNC,"func")
        for sub,items,field in [("pain",WOMAC_PAIN,"womac_pain"),("stiff",WOMAC_STIFF,"womac_stiff"),("func",WOMAC_FUNC,"womac_func")]:
            s=self._sub(collected,items); collected[field]=s if s is not None else ""
        try:
            total=round((float(collected["womac_pain"])*5+float(collected["womac_stiff"])*2+float(collected["womac_func"])*17)/24,1)
            collected["womac_total"]=total
            color="#388e3c" if total<=25 else "#f57c00" if total<=50 else "#d32f2f"
            st.markdown(f'<div class="score-box" style="background:{color}">WOMAC total : {total}/100</div>',unsafe_allow_html=True)
        except: collected["womac_total"]=""
        return collected

    @classmethod
    def score(cls, data):
        try: s=float(data.get("womac_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=25 else "#f57c00" if s<=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("womac_total",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("womac_total","Total","#2B57A7"),("womac_pain","Douleur","#D85A30"),("womac_func","Fonction","#1D9E75")]:
            vals=[]; 
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers",name=l,line=dict(color=c,width=2.5),marker=dict(size=8)))
        fig.update_layout(yaxis=dict(range=[0,105],title="WOMAC /100"),height=320,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Total":r.get("womac_total","—"),"Douleur":r.get("womac_pain","—"),"Fonction":r.get("womac_func","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
