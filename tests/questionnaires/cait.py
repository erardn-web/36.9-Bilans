"""tests/questionnaires/misc_scores.py — Cumberland CAIT, IKDC, Tegner, DHI, HIT-6"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Cumberland Ankle Instability Tool (CAIT) ──────────────────────────────────
@register_test
class CAIT(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"cait","nom":"CAIT — Instabilité cheville","tab_label":"🦶 CAIT","categorie":"questionnaire",
                "tags":["cheville","instabilité","entorse","fonctionnel"],
                "description":"Cumberland Ankle Instability Tool — 9 items /30. Seuil instabilité ≤ 27"}
    @classmethod
    def fields(cls): return [f"cait_q{i}" for i in range(1,10)]+["cait_score"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦶 CAIT — Instabilité de cheville</div>', unsafe_allow_html=True)
        collected={}; total=0
        questions=[
            ("cait_q1","Douleur à la cheville",[("4","Jamais"),("3","Pendant le sport"),("2","En courant sur terrain inégal"),("1","En courant sur terrain plat"),("0","En marchant")]),
            ("cait_q2","Instabilité (genou qui cède)",[("4","Jamais"),("3","Parfois pendant sport (pas à chaque fois)"),("2","Souvent pendant sport"),("1","Parfois dans AVQ"),("0","Souvent dans AVQ")]),
            ("cait_q3","Sensation de cheville qui 'tourne'",[("3","Jamais"),("2","Parfois"),("1","Souvent"),("0","Toujours")]),
            ("cait_q4","Instabilité en virage serré",[("3","Jamais"),("2","Parfois"),("1","Souvent"),("0","Toujours")]),
            ("cait_q5","Descendre les escaliers",[("3","Jamais"),("2","Parfois"),("1","Souvent"),("0","Toujours")]),
            ("cait_q6","Tenir en équilibre sur une jambe",[("2","Jamais, >10s"),("1","Parfois"),("0","Souvent")]),
            ("cait_q7","Instabilité en sautant d'une seule jambe",[("2","Jamais"),("1","Parfois"),("0","Souvent")]),
            ("cait_q8","Instabilité en sautant en hauteur",[("2","Jamais"),("1","Parfois"),("0","Souvent")]),
            ("cait_q9","Instabilité en courant sur terrain inégal",[("2","Jamais"),("1","Parfois"),("0","Souvent")]),
        ]
        for k,label,opts in questions:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else None
            except: stored=None
            vals=[int(o[0]) for o in opts]; opts_ext=[None]+vals
            def _fmt(x,o=opts): return "— Non renseigné —" if x is None else next(l for s,l in o if int(s)==x)
            default=(vals.index(stored)+1) if stored in vals else 0
            chosen=st.radio(f"**{label}**",opts_ext,format_func=_fmt,index=default,key=f"{key_prefix}_{k}",horizontal=True)
            collected[k]=chosen if chosen is not None else ""
            if chosen is not None: total+=chosen
        collected["cait_score"]=total
        color="#d32f2f" if total<=27 else "#388e3c"
        msg="Instabilité fonctionnelle" if total<=27 else "Cheville stable"
        st.markdown(f'<div class="score-box" style="background:{color}">CAIT : {total}/30 — {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("cait_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s<=27 else "#388e3c"
        return {"score":s,"interpretation":f"{s:.0f}/30","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("cait_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("cait_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="CAIT",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=27,line_dash="dot",line_color="#d32f2f",annotation_text="Seuil instabilité ≤27")
        fig.update_layout(yaxis=dict(range=[0,32],title="CAIT /30"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"CAIT":r.get("cait_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── Tegner Activity Scale ─────────────────────────────────────────────────────