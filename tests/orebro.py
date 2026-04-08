"""tests/tests_cliniques/orebro.py — Örebro Musculoskeletal Screening (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

OREBRO_ITEMS=[
    ("orebro_1","Quelle est l'intensité de votre douleur en ce moment ?","0 = pas de douleur  ·  10 = douleur insupportable"),
    ("orebro_2","Dans quelle mesure votre douleur est-elle présente en permanence pendant vos heures d'éveil ?","0 = jamais  ·  10 = toujours"),
    ("orebro_3","Dans quelle mesure la douleur perturbe-t-elle votre sommeil ?","0 = pas du tout  ·  10 = complètement"),
    ("orebro_4","Dans quelle mesure avez-vous peur que l'activité physique aggrave votre douleur ?","0 = pas du tout  ·  10 = extrêmement"),
    ("orebro_5","Dans quelle mesure pensez-vous que votre douleur disparaîtra ?","0 = pas du tout  ·  10 = complètement"),
    ("orebro_6","Quelle confiance avez-vous dans le fait de retourner au travail dans les 3 prochains mois ?","0 = aucune confiance  ·  10 = très confiant(e)"),
    ("orebro_7","Dans quelle mesure pensez-vous que vous pouvez effectuer un travail malgré la douleur ?","0 = pas du tout  ·  10 = totalement"),
    ("orebro_8","Activités légères à la maison — dans quelle mesure la douleur affecte-t-elle votre capacité ?","0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_9","Activités lourdes à la maison — dans quelle mesure la douleur affecte-t-elle votre capacité ?","0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_10","Activités sociales — dans quelle mesure la douleur affecte-t-elle votre capacité ?","0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_11","Déplacements — dans quelle mesure la douleur affecte-t-elle votre capacité ?","0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_12","Loisirs légers — dans quelle mesure la douleur affecte-t-elle votre capacité ?","0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_13","Travail ou études — dans quelle mesure la douleur affecte-t-elle votre capacité ?","0 = pas d'effet  ·  10 = incapable de faire"),
]
OREBRO_INVERTED={"orebro_5","orebro_6","orebro_7"}
OREBRO_KEYS=[o[0] for o in OREBRO_ITEMS]

def compute_orebro(answers):
    total=0; count=0
    for key,_,_ in OREBRO_ITEMS:
        v=answers.get(key)
        if v is not None:
            score=int(v)
            if key in OREBRO_INVERTED: score=10-score
            total+=score; count+=1
    if count==0: return {"score":None,"interpretation":"","color":"#888","raw":0}
    pct=round(total/(count*10)*100)
    if pct<=50:   interp,color="Risque faible de chronicisation (≤ 50)","#388e3c"
    elif pct<=74: interp,color="Risque moyen de chronicisation (51–74)","#f57c00"
    else:         interp,color="Risque élevé de chronicisation (≥ 75)","#d32f2f"
    return {"score":pct,"interpretation":interp,"color":color,"raw":total}

@register_test
class Orebro(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"orebro","nom":"Örebro","tab_label":"🔮 Örebro",
                "categorie":"questionnaire","tags":["lombalgie", "chronicisation", "pronostic", "rachis"],"description":"Risque de chronicisation, seuil > 50/75"}

    @classmethod
    def fields(cls):
        return OREBRO_KEYS+["orebro_score","orebro_interpretation"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score Örebro (/210)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">Örebro Musculoskeletal Screening Questionnaire</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">13 questions sur échelle 0–10. '
                    'Seuils de chronicisation : ≤ 50 faible · 51–74 moyen · ≥ 75 élevé</div>',
                    unsafe_allow_html=True)
        orebro_answers={}; collected={}
        for key,question,hint in OREBRO_ITEMS:
            num=int(key.split("_")[1])
            stored=lv(key,"")
            opts=[None]+list(range(11))
            def fmt(x,h=hint): return "— Non renseigné —" if x is None else str(x)
            try: default=int(float(stored)) if stored not in ("","None","nan") else None
            except: default=None
            st.markdown(f"**{num}.** {question}  \n<small style='color:#666'>{hint}</small>",
                        unsafe_allow_html=True)
            chosen=st.select_slider(f"q{num}",options=opts,value=default,
                format_func=fmt,key=f"{key_prefix}_{key}",label_visibility="collapsed")
            collected[key]="" if chosen is None else chosen
            if chosen is not None: orebro_answers[key]=chosen
        orebro_r=compute_orebro(orebro_answers)
        if orebro_r["score"] is not None:
            st.markdown("---")
            st.markdown(f'<div class="score-box" style="background:{orebro_r["color"]};">'
                        f'Örebro : {orebro_r["score"]}/100 — {orebro_r["interpretation"]}</div>',
                        unsafe_allow_html=True)
        collected.update({"orebro_score":orebro_r["score"] if orebro_r["score"] is not None else "",
                          "orebro_interpretation":orebro_r["interpretation"]})
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("orebro_score","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("orebro_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Örebro /100",
                line=dict(color="#7B1FA2",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}" for v in yp],textposition="top center"))
        for y,color,label in [(50,"#388e3c","50 faible"),(75,"#d32f2f","75 élevé")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,105],title="Score /100"),height=300,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('orebro', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "Örebro", "col_key": "orebro_score",
             "values": [r.get("orebro_score","—") for _,r in bilans_df.iterrows()]},
            {"label": "Risque", "col_key": "orebro_interpretation",
             "values": [r.get("orebro_interpretation","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows=[{"Bilan":lbl,"Örebro":row.get("orebro_score","—"),"Risque":row.get("orebro_interpretation","—")}
                          for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
