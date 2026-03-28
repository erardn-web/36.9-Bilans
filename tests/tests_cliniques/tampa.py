"""tests/tests_cliniques/tampa.py — Tampa Scale Kinésiophobie (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

TAMPA_ITEMS=[
    ("tampa_1",False,"J'ai peur de me blesser si je fais de l'exercice."),
    ("tampa_2",False,"Si j'essayais de surmonter ma douleur, celle-ci augmenterait."),
    ("tampa_3",False,"Mon corps me dit que quelque chose ne va pas vraiment."),
    ("tampa_4",False,"Ma blessure a mis mon corps en danger toute ma vie."),
    ("tampa_5",False,"Les gens ne prennent pas ma condition médicale assez au sérieux."),
    ("tampa_6",False,"Ma blessure a mis mon corps en danger de façon permanente."),
    ("tampa_7",False,"La douleur signifie toujours que j'ai subi une blessure corporelle."),
    ("tampa_8",True,"Simplement parce que quelque chose aggrave ma douleur ne signifie pas qu'elle est dangereuse."),
    ("tampa_9",False,"J'ai peur de me blesser accidentellement."),
    ("tampa_10",False,"Le plus sûr est de faire attention à ne pas faire de mouvements inutiles."),
    ("tampa_11",False,"Je n'aurais pas autant de douleur si quelque chose de potentiellement grave ne se passait pas."),
    ("tampa_12",True,"Bien que ma condition soit douloureuse, je me sentirais mieux si j'étais plus actif(ve)."),
    ("tampa_13",False,"La douleur me signale que je dois arrêter ce que je fais pour ne pas me blesser."),
    ("tampa_14",False,"Ce n'est pas vraiment sûr pour quelqu'un avec ma condition d'être physiquement actif(ve)."),
    ("tampa_15",False,"Je risque trop facilement de me blesser."),
    ("tampa_16",True,"Même si quelque chose me fait très mal, je ne pense pas que ce soit dangereux."),
    ("tampa_17",False,"Personne ne devrait faire de l'exercice physique quand il souffre de douleur."),
]
TAMPA_KEYS=[t[0] for t in TAMPA_ITEMS]
TAMPA_SCALE=["1 — Pas du tout d'accord","2 — Plutôt pas d'accord","3 — Plutôt d'accord","4 — Tout à fait d'accord"]
TAMPA_VALS=[1,2,3,4]

def compute_tampa(answers):
    total=0; count=0
    for key,reversed_item,_ in TAMPA_ITEMS:
        v=answers.get(key)
        if v is not None:
            score=int(v)
            if reversed_item: score=5-score
            total+=score; count+=1
    if count==0: return {"score":None,"interpretation":"","color":"#888"}
    if count<17: total=round(total/count*17)
    if total<=37:   interp,color="Kinésiophobie faible (≤ 37)","#388e3c"
    elif total<=44: interp,color="Kinésiophobie modérée (38–44)","#f57c00"
    else:           interp,color="Kinésiophobie élevée (> 44)","#d32f2f"
    return {"score":total,"interpretation":interp,"color":color}

@register_test
class Tampa(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"tampa","nom":"Tampa — Kinésiophobie","tab_label":"😰 Tampa",
                "categorie":"questionnaire","tags":["lombalgie", "douleur chronique", "kinésiophobie", "psychologique"],"description":"TSK-17, kinésiophobie, seuil > 37"}

    @classmethod
    def fields(cls):
        return TAMPA_KEYS+["tampa_score","tampa_interpretation"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">Tampa Scale for Kinesiophobia (TSK-17)</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">17 items. Seuils : ≤ 37 faible · 38–44 modéré · > 44 élevé. '
                    'Items marqués (R) sont inversés.</div>', unsafe_allow_html=True)
        tampa_answers={}; collected={}
        for key,reversed_item,text in TAMPA_ITEMS:
            num=int(key.split("_")[1])
            stored=lv(key,"")
            opts=["— Non renseigné —"]+TAMPA_SCALE
            idx=0
            if stored!="":
                try: idx=int(float(stored))
                except: pass
            label=f"**{num}{'(R)' if reversed_item else '.'}** {text}"
            chosen=st.radio(label,opts,index=idx,key=f"{key_prefix}_{key}",horizontal=True)
            if chosen=="— Non renseigné —": collected[key]=""
            else:
                v=int(chosen.split(" — ")[0]); tampa_answers[key]=v; collected[key]=v
        tampa_r=compute_tampa(tampa_answers)
        if tampa_r["score"] is not None:
            st.markdown("---")
            st.markdown(f'<div class="score-box" style="background:{tampa_r["color"]};">'
                        f'Tampa : {tampa_r["score"]}/68 — {tampa_r["interpretation"]}</div>',
                        unsafe_allow_html=True)
        collected.update({"tampa_score":tampa_r["score"] if tampa_r["score"] is not None else "",
                          "tampa_interpretation":tampa_r["interpretation"]})
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("tampa_score","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("tampa_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Tampa /68",
                line=dict(color="#C4603A",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}" for v in yp],textposition="top center"))
        for y,color,label in [(37,"#388e3c","37 faible"),(44,"#f57c00","44 modéré")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis_title="Score Tampa",height=300,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows=[{"Bilan":lbl,"Tampa":row.get("tampa_score","—"),"Kinésiophobie":row.get("tampa_interpretation","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
