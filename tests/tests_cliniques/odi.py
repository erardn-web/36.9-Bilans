"""tests/tests_cliniques/odi.py — Oswestry Disability Index (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

ODI_SECTIONS = [
    ("odi_s1","1. Intensité de la douleur",["Pas de douleur actuellement","La douleur est très légère actuellement","La douleur est modérée actuellement","La douleur est assez sévère actuellement","La douleur est très sévère actuellement","La douleur est la pire imaginable actuellement"]),
    ("odi_s2","2. Soins personnels (se laver, s'habiller…)",["Je me prends en charge normalement sans douleur supplémentaire","Je me prends en charge normalement mais c'est très douloureux","Se prendre en charge est douloureux — je suis lent(e) et prudent(e)","J'ai besoin d'aide mais j'arrive à gérer la plupart de mes soins","J'ai besoin d'aide chaque jour pour la plupart de mes soins","Je ne m'habille pas, me lave avec difficulté et reste au lit"]),
    ("odi_s3","3. Soulever des charges",["Je peux soulever des charges lourdes sans douleur","Je peux soulever des charges lourdes mais avec douleur supplémentaire","La douleur m'empêche de soulever des charges lourdes du sol","La douleur m'empêche de soulever des charges lourdes (je peux soulever du léger si bien placé)","Je peux soulever des charges très légères uniquement","Je ne peux rien soulever ni porter"]),
    ("odi_s4","4. Marche",["La douleur ne m'empêche pas de marcher quelle que soit la distance","La douleur m'empêche de marcher plus d'un kilomètre","La douleur m'empêche de marcher plus de 500 mètres","La douleur m'empêche de marcher plus de 100 mètres","Je ne marche qu'avec une canne ou des béquilles","Je suis au lit la plupart du temps et dois me traîner pour aller aux toilettes"]),
    ("odi_s5","5. Position assise",["Je peux rester assis(e) aussi longtemps que je veux sans douleur","Je peux rester assis(e) aussi longtemps que je veux avec légère douleur","La douleur m'empêche de rester assis(e) plus d'une heure","La douleur m'empêche de rester assis(e) plus de 30 minutes","La douleur m'empêche de rester assis(e) plus de 10 minutes","La douleur m'empêche totalement de m'asseoir"]),
    ("odi_s6","6. Position debout",["Je peux rester debout aussi longtemps que je veux sans douleur","Je peux rester debout aussi longtemps que je veux mais avec douleur","La douleur m'empêche de rester debout plus d'une heure","La douleur m'empêche de rester debout plus de 30 minutes","La douleur m'empêche de rester debout plus de 10 minutes","La douleur m'empêche totalement de rester debout"]),
    ("odi_s7","7. Sommeil",["Mon sommeil n'est jamais perturbé par la douleur","Mon sommeil est parfois perturbé par la douleur","Je dors moins de 6 heures à cause de la douleur","Je dors moins de 4 heures à cause de la douleur","Je dors moins de 2 heures à cause de la douleur","La douleur m'empêche totalement de dormir"]),
    ("odi_s8","8. Vie sexuelle (si applicable)",["Ma vie sexuelle est normale sans douleur supplémentaire","Ma vie sexuelle est normale mais provoque une douleur supplémentaire","Ma vie sexuelle est presque normale mais est très douloureuse","Ma vie sexuelle est sévèrement limitée par la douleur","Ma vie sexuelle est presque absente en raison de la douleur","La douleur empêche toute vie sexuelle"]),
    ("odi_s9","9. Vie sociale",["Ma vie sociale est normale sans douleur supplémentaire","Ma vie sociale est normale mais augmente le degré de douleur","La douleur n'affecte pas les activités légères mais limite les activités énergiques","La douleur a limité ma vie sociale — je sors moins souvent","La douleur a limité ma vie sociale à ma maison","Je n'ai pas de vie sociale à cause de la douleur"]),
    ("odi_s10","10. Voyages / transports",["Je peux voyager n'importe où sans douleur supplémentaire","Je peux voyager n'importe où mais avec douleur","La douleur est sévère mais je gère les trajets de plus de 2 heures","La douleur me restreint à des trajets de moins d'une heure","La douleur me restreint à des trajets courts de moins de 30 minutes","La douleur m'empêche de voyager sauf pour des soins médicaux"]),
]
ODI_KEYS=[s[0] for s in ODI_SECTIONS]

def compute_odi(answers):
    scores=[int(answers[k]) for k in ODI_KEYS if str(answers.get(k,"")).strip()!=""]
    if not scores: return {"score":None,"interpretation":"","color":"#888","raw":0}
    total=sum(scores); pct=round(total/len(scores)/5*100)
    if pct<=20:   interp,color="Incapacité minimale (0–20%)","#388e3c"
    elif pct<=40: interp,color="Incapacité modérée (21–40%)","#8bc34a"
    elif pct<=60: interp,color="Incapacité sévère (41–60%)","#f57c00"
    elif pct<=80: interp,color="Incapacité très sévère (61–80%)","#e64a19"
    else:         interp,color="Grabataire / exagération (>80%)","#d32f2f"
    return {"score":pct,"interpretation":interp,"color":color,"raw":total}

@register_test
class ODI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"odi","nom":"ODI — Oswestry","tab_label":"📋 ODI",
                "categorie":"questionnaire","description":"Oswestry Disability Index /100, seuil clinique > 20%"}

    @classmethod
    def fields(cls):
        return ODI_KEYS+["odi_score","odi_interpretation"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">ODI — Oswestry Disability Index</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">10 sections, choisir la réponse qui décrit le mieux votre situation. '
                    'Seuil clinique significatif : > 20%</div>', unsafe_allow_html=True)
        odi_answers={}; collected={}
        for key,title,options in ODI_SECTIONS:
            stored=lv(key,"")
            opts=["— Non renseigné —"]+[f"{i} — {opt}" for i,opt in enumerate(options)]
            idx=0
            if stored!="":
                try: idx=int(float(stored))+1
                except: pass
            chosen=st.radio(title,opts,index=idx,key=f"{key_prefix}_{key}")
            if chosen=="— Non renseigné —": collected[key]=""
            else:
                v=int(chosen.split(" — ")[0]); odi_answers[key]=v; collected[key]=v

        odi_r=compute_odi(odi_answers)
        if odi_r["score"] is not None:
            st.markdown("---")
            st.markdown(f'<div class="score-box" style="background:{odi_r["color"]};">'
                        f'ODI : {odi_r["score"]}% — {odi_r["interpretation"]}</div>',
                        unsafe_allow_html=True)
        collected.update({"odi_score":odi_r["score"] if odi_r["score"] is not None else "",
                          "odi_interpretation":odi_r["interpretation"]})
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("odi_score","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("odi_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="ODI %",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}%" for v in yp],textposition="top center"))
        for y,color,label in [(20,"#388e3c","20% min"),(40,"#f57c00","40% mod"),(60,"#d32f2f","60% sév")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,105],title="ODI %"),height=320,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows=[{"Bilan":lbl,"ODI %":row.get("odi_score","—"),"Incapacité":row.get("odi_interpretation","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
