"""tests/questionnaires/dn4.py — DN4 (Douleur Neuropathique en 4 questions)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

DN4_ITEMS = [
    # Section 1 : interrogatoire
    ("dn4_q1","La douleur a-t-elle une ou plusieurs des caractéristiques suivantes ?\n→ Brûlure"),
    ("dn4_q2","Sensation de froid douloureux"),
    ("dn4_q3","Décharges électriques"),
    # Section 2 : interrogatoire
    ("dn4_q4","La douleur est-elle associée à un ou plusieurs des symptômes suivants ?\n→ Fourmillements"),
    ("dn4_q5","Picotements"),
    ("dn4_q6","Engourdissements"),
    ("dn4_q7","Démangeaisons"),
    # Section 3 : examen
    ("dn4_q8","La douleur est-elle localisée dans un territoire où l'examen met en évidence ?\n→ Hypoesthésie au toucher"),
    ("dn4_q9","Hypoesthésie à la piqûre"),
    # Section 4 : examen
    ("dn4_q10","Dans le territoire douloureux, la douleur est-elle provoquée ou augmentée par ?\n→ Le frottement"),
]


@register_test
class DN4(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"dn4","nom":"DN4 — Douleur neuropathique","tab_label":"⚡ DN4","categorie":"questionnaire",
                "tags":["neuropathique","douleur","dépistage","radiculalgie"],
                "description":"DN4 — Dépistage douleur neuropathique — 10 items oui/non. Seuil ≥ 4/10"}

    @classmethod
    def fields(cls):
        return [k for k,_ in DN4_ITEMS]+["dn4_score"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score DN4 (/10)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">⚡ DN4 — Douleur neuropathique</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Répondez Oui ou Non pour chaque item. Score ≥ 4/10 = probable douleur neuropathique.</div>', unsafe_allow_html=True)
        collected={}; total=0
        sections=[("Interrogatoire (caractéristiques)",["dn4_q1","dn4_q2","dn4_q3"]),
                  ("Interrogatoire (symptômes associés)",["dn4_q4","dn4_q5","dn4_q6","dn4_q7"]),
                  ("Examen (hypoesthésie)",["dn4_q8","dn4_q9"]),
                  ("Examen (allodynie)",["dn4_q10"])]
        items_dict={k:label for k,label in DN4_ITEMS}
        for sec_title,keys in sections:
            st.markdown(f"**{sec_title}**")
            for k in keys:
                raw=lv(k,None); stored=str(raw) in ("1","True","Oui")
                val=st.checkbox(items_dict[k],value=stored,key=f"{key_prefix}_{k}")
                collected[k]=1 if val else 0
                if val: total+=1
        collected["dn4_score"]=total
        color="#d32f2f" if total>=4 else "#388e3c"
        msg="⚠️ Probable douleur neuropathique" if total>=4 else "✅ Pas de signe neuropathique"
        st.markdown(f'<div class="score-box" style="background:{color}">DN4 : {total}/10 — {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("dn4_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s>=4 else "#388e3c"
        return {"score":s,"interpretation":f"{s:.0f}/10 {'Neuropathique probable' if s>=4 else 'Non neuropathique'}","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("dn4_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("dn4_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="DN4",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=4,line_dash="dot",line_color="#d32f2f",annotation_text="Seuil neuropathique ≥4")
        fig.update_layout(yaxis=dict(range=[0,11],title="DN4 /10"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('dn4', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"DN4":r.get("dn4_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
