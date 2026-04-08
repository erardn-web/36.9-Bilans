"""tests/tests_cliniques/cat.py — CAT COPD Assessment Test (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

CAT_ITEMS = [
    ("cat_1","Je ne tousse jamais","Je tousse tout le temps"),
    ("cat_2","Je n'ai pas du tout de glaires dans la poitrine","J'ai la poitrine pleine de glaires"),
    ("cat_3","Je n'ai pas du tout la poitrine oppressée","J'ai très fortement la poitrine oppressée"),
    ("cat_4","Quand je monte un escalier, je ne suis pas essoufflé(e)","Quand je monte un escalier, je suis très essoufflé(e)"),
    ("cat_5","Les activités à la maison ne me sont pas du tout limitées","Les activités à la maison me sont très limitées"),
    ("cat_6","Je suis confiant(e) de sortir malgré ma condition pulmonaire","Je ne suis pas du tout confiant(e) de sortir à cause de ma condition pulmonaire"),
    ("cat_7","Je dors profondément","Je ne dors pas profondément à cause de ma condition pulmonaire"),
    ("cat_8","J'ai plein d'énergie","Je n'ai pas du tout d'énergie"),
]
CAT_KEYS = [c[0] for c in CAT_ITEMS]

def compute_cat(answers):
    vals = [int(answers[k]) for k in CAT_KEYS if str(answers.get(k,"")).strip() != ""]
    if not vals: return {"score":None,"color":"#888","interpretation":""}
    total = sum(vals)
    if total<=10:   color,interp = "#388e3c","Impact faible (0–10)"
    elif total<=20: color,interp = "#f57c00","Impact modéré (11–20)"
    elif total<=30: color,interp = "#e64a19","Impact sévère (21–30)"
    else:           color,interp = "#d32f2f","Impact très sévère (31–40)"
    return {"score":total,"color":color,"interpretation":interp}

@register_test
class CAT(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"cat","nom":"CAT — COPD Assessment Test","tab_label":"📋 CAT",
                "categorie":"questionnaire","tags":["BPCO", "respiratoire", "qualité de vie", "symptômes"],"description":"8 items /40, seuils 10/20/30"}

    @classmethod
    def fields(cls):
        return CAT_KEYS + ["cat_score","cat_interpretation"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score CAT (/40)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
            {"key": "detail_items", "label": "Détail des items", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">CAT — COPD Assessment Test</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">8 questions, chacune de 0 à 5. '
                    'Seuils : 0–10 faible · 11–20 modéré · 21–30 sévère · 31–40 très sévère</div>',
                    unsafe_allow_html=True)
        cat_answers={}; collected={}
        for key,left,right in CAT_ITEMS:
            num=int(key.split("_")[1])
            stored=lv(key,"")
            opts=[None,0,1,2,3,4,5]
            def fmt(x,l=left,r=right):
                if x is None: return "— Non renseigné —"
                if x==0: return f"0 — {l}"
                if x==5: return f"5 — {r}"
                return str(x)
            default_v=None if stored=="" else (int(float(stored)) if stored not in (None,"None","nan") else None)
            st.markdown(f"**Question {num}**  \n"
                f"<small style='color:#2B57A7'>0 — {left}</small>"
                f"<small style='color:#888'> &nbsp;···&nbsp; </small>"
                f"<small style='color:#C4603A'>5 — {right}</small>",
                unsafe_allow_html=True)
            chosen=st.select_slider(f"Q{num}",options=opts,value=default_v,
                format_func=fmt,key=f"{key_prefix}_{key}",label_visibility="collapsed")
            collected[key]="" if chosen is None else chosen
            if chosen is not None: cat_answers[key]=chosen
        cat_r=compute_cat(cat_answers)
        if cat_r["score"] is not None:
            st.markdown("---")
            st.markdown(f'<div class="score-box" style="background:{cat_r["color"]};">'
                        f'CAT : {cat_r["score"]}/40 — {cat_r["interpretation"]}</div>',
                        unsafe_allow_html=True)
        collected.update({"cat_score":cat_r["score"] if cat_r["score"] is not None else "",
                          "cat_interpretation":cat_r["interpretation"]})
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("cat_score","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("cat_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="CAT /40",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}/40" for v in yp],textposition="top center"))
        for y,color,label in [(10,"#388e3c","10 faible"),(20,"#f57c00","20 modéré"),(30,"#d32f2f","30 sévère")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,42],title="Score /40"),height=320,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('cat', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "CAT /40", "col_key": "cat_score",
             "values": [r.get("cat_score","—") for _,r in bilans_df.iterrows()]},
            {"label": "Impact", "col_key": "cat_interpretation",
             "values": [r.get("cat_interpretation","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows=[{"Bilan":lbl,"CAT /40":row.get("cat_score","—"),"Impact":row.get("cat_interpretation","—")}
                          for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
