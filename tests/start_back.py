"""tests/questionnaires/start_back.py — STarT Back Screening Tool"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

START_ITEMS = [
    ("sb_q1","Mon mal de dos s'est propagé vers mes jambes (la plupart du temps)","bool"),
    ("sb_q2","J'ai eu une douleur dans l'épaule ou le cou (la plupart du temps)","bool"),
    ("sb_q3","J'ai seulement marché sur de courtes distances à cause de mon dos","bool"),
    ("sb_q4","Au cours des deux dernières semaines, j'ai habillé plus lentement que d'habitude à cause de mon dos","bool"),
    ("sb_q5","Ce n'est vraiment pas sûr pour une personne dans mon état d'être physiquement actif","bool"),
    ("sb_q6","Les pensées inquiètes ont traversé mon esprit tout le temps","bool"),
    ("sb_q7","J'ai le sentiment que mon dos est terrible et que ça ne s'améliorera jamais","bool"),
    ("sb_q8","En général, je n'ai pas apprécié toutes les choses que j'aimais faire","bool"),
    ("sb_q9","Dans l'ensemble, quelle a été la gêne de votre douleur de dos au cours des deux dernières semaines ?","scale"),
]


@register_test
class STarTBack(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"start_back","nom":"STarT Back — Dépistage","tab_label":"🚦 STarT Back","categorie":"questionnaire",
                "tags":["lombalgie","dépistage","psychosocial","risque chronification"],
                "description":"STarT Back Screening Tool — 9 items, stratification risque faible/moyen/élevé"}

    @classmethod
    def fields(cls):
        return [k for k,*_ in START_ITEMS]+["sb_total","sb_psycho","sb_risque"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score STarT Back", "default": True},
            {"key": "risque", "label": "Niveau de risque", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🚦 STarT Back — Dépistage lombaire</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Questions sur votre dos au cours des 2 dernières semaines.</div>', unsafe_allow_html=True)
        collected={}
        total=0; psycho=0
        for k,label,qtype in START_ITEMS:
            if qtype=="bool":
                raw=lv(k,None); stored = str(raw) in ("1","True","Oui")
                val=st.checkbox(label,value=stored,key=f"{key_prefix}_{k}")
                collected[k]=1 if val else 0
                if val: total+=1
                if k in ("sb_q5","sb_q6","sb_q7","sb_q8") and val: psycho+=1
            else:
                raw=lv(k,None)
                try: stored=int(float(raw)) if raw not in (None,"","None") else 1
                except: stored=1
                val=st.radio(label,[1,2,3,4,5],index=stored-1,
                    format_func=lambda x:["1 — Pas du tout","2 — Légèrement","3 — Modérément","4 — Très","5 — Extrêmement"][x-1],
                    key=f"{key_prefix}_{k}",horizontal=True)
                collected[k]=1 if val>=4 else 0
                if val>=4: total+=1
        if total<=3: risque="Faible 🟢"
        elif psycho>=4: risque="Élevé 🔴"
        else: risque="Moyen 🟡"
        collected.update({"sb_total":total,"sb_psycho":psycho,"sb_risque":risque})
        color="#388e3c" if "Faible" in risque else "#d32f2f" if "Élevé" in risque else "#f57c00"
        st.markdown(f'<div class="score-box" style="background:{color}">STarT Back : {total}/9 | Risque : {risque} | Psychosocial : {psycho}/5</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        risque=data.get("sb_risque","—"); total=data.get("sb_total","—")
        if str(total).strip() in ("","None","nan"): return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if "Faible" in str(risque) else "#d32f2f" if "Élevé" in str(risque) else "#f57c00"
        return {"score":float(total),"interpretation":f"Score:{total} Risque:{risque}","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        return str(data.get("sb_total","")).strip() not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("sb_total","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="STarT",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=3,line_dash="dot",line_color="#388e3c",annotation_text="Seuil risque moyen")
        fig.update_layout(yaxis=dict(range=[0,10],title="Score /9"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Score":r.get("sb_total","—"),"Risque":r.get("sb_risque","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
