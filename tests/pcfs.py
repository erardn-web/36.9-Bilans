"""tests/questionnaires/cardiopulmonaire.py — SGRQ, CRQ, LCADL, PCFS, Borg RPE, PSQI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Borg RPE ─────────────────────────────────────────────────────────────────
@register_test
class PCFS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"pcfs","nom":"PCFS — État fonctionnel post-COVID","tab_label":"🦠 PCFS",
                "categorie":"questionnaire","tags":["post-COVID","long COVID","fonctionnel","fatigue"],
                "description":"Post-COVID Functional Status Scale — 5 grades (0-4), état fonctionnel après COVID"}
    @classmethod
    def fields(cls): return ["pcfs_grade","pcfs_notes"]
    GRADES={
        0:"Grade 0 — Aucune limitation fonctionnelle (pas de symptômes)",
        1:"Grade 1 — Limitation légère (symptômes présents mais activités normales)",
        2:"Grade 2 — Limitation modérée (quelques activités réduites, pas besoin d'aide)",
        3:"Grade 3 — Limitation importante (aide pour les tâches ménagères ou AVQ)",
        4:"Grade 4 — Limitation sévère (dépendance totale pour les soins personnels)",
    }
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "grade", "label": "Grade PCFS (0-5)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦠 PCFS — État fonctionnel post-COVID</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Évaluation fonctionnelle globale après infection COVID-19. Grade 0 = pas de limitation · Grade 4 = limitation sévère.</div>', unsafe_allow_html=True)
        raw=lv("pcfs_grade",None)
        try: stored=int(float(raw)) if raw not in (None,"","None") else 0
        except: stored=0
        grade=st.radio("Grade fonctionnel",list(range(5)),index=stored,format_func=lambda x:self.GRADES[x],key=f"{key_prefix}_pcfs_grade")
        notes=st.text_area("Notes cliniques",value=lv("pcfs_notes",""),height=80,key=f"{key_prefix}_pcfs_notes")
        collected={"pcfs_grade":grade,"pcfs_notes":notes}
        color="#388e3c" if grade==0 else "#7cb87e" if grade==1 else "#f57c00" if grade==2 else "#e65100" if grade==3 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">PCFS Grade {grade}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("pcfs_grade",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        colors=["#388e3c","#7cb87e","#f57c00","#e65100","#d32f2f"]
        return {"score":s,"interpretation":f"Grade {s:.0f}/4","color":colors[int(s)],"details":{}}
    @classmethod
    def is_filled(cls,data):
        return str(data.get("pcfs_grade","")).strip() not in ("","None","nan")
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("pcfs_grade","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="PCFS",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"G{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[-0.2,4.5],tickvals=[0,1,2,3,4],title="Grade"),height=250,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"PCFS Grade":r.get("pcfs_grade","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── PSQI Pittsburgh Sleep Quality Index ───────────────────────────────────────