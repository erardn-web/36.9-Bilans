"""tests/questionnaires/sport_main.py — K-SES, PRWE, BPI, MHQ"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── K-SES Knee Self-Efficacy Scale ────────────────────────────────────────────
@register_test
class BPI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"bpi","nom":"BPI — Inventaire bref de la douleur","tab_label":"📊 BPI",
                "categorie":"questionnaire","tags":["douleur","intensité","impact","universel","cancer"],
                "description":"Brief Pain Inventory — intensité douleur + retentissement sur les activités"}
    @classmethod
    def fields(cls):
        return ["bpi_worst","bpi_least","bpi_average","bpi_now",
                "bpi_activity","bpi_mood","bpi_walk","bpi_work","bpi_relations","bpi_sleep","bpi_enjoyment",
                "bpi_severity_score","bpi_interference_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "severity", "label": "Sévérité (/10)", "default": True},
            {"key": "interference", "label": "Interférence (/10)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📊 BPI — Inventaire bref de la douleur</div>', unsafe_allow_html=True)
        collected={}
        st.markdown("**Intensité de la douleur (0=aucune · 10=pire imaginable)**")
        c1,c2=st.columns(2)
        sev_vals=[]
        for col,k,label in [(c1,"bpi_worst","Au pire"),(c1,"bpi_least","Au moins intense"),
                             (c2,"bpi_average","En moyenne"),(c2,"bpi_now","En ce moment")]:
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 0
            except: v=0
            val=col.slider(label,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; sev_vals.append(val)
        sev=round(sum(sev_vals)/4,1)
        collected["bpi_severity_score"]=sev
        st.markdown("**Retentissement de la douleur sur... (0=aucun · 10=total)**")
        int_vals=[]
        c3,c4=st.columns(2)
        for col,k,label in [(c3,"bpi_activity","Activité générale"),(c3,"bpi_mood","Humeur"),
                             (c3,"bpi_walk","Capacité à marcher"),(c3,"bpi_work","Travail"),
                             (c4,"bpi_relations","Relations avec les autres"),(c4,"bpi_sleep","Sommeil"),
                             (c4,"bpi_enjoyment","Goût de vivre")]:
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 0
            except: v=0
            val=col.slider(label,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; int_vals.append(val)
        interf=round(sum(int_vals)/7,1)
        collected["bpi_interference_score"]=interf
        c5,c6=st.columns(2)
        color_s="#388e3c" if sev<=3 else "#f57c00" if sev<=6 else "#d32f2f"
        color_i="#388e3c" if interf<=3 else "#f57c00" if interf<=6 else "#d32f2f"
        c5.markdown(f'<div class="score-box" style="background:{color_s}">Sévérité : {sev}/10</div>',unsafe_allow_html=True)
        c6.markdown(f'<div class="score-box" style="background:{color_i}">Retentissement : {interf}/10</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("bpi_severity_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=3 else "#f57c00" if s<=6 else "#d32f2f"
        interf=data.get("bpi_interference_score","—")
        return {"score":s,"interpretation":f"Sévérité:{s} Retent:{interf}","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("bpi_severity_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("bpi_severity_score","Sévérité","#D85A30"),("bpi_interference_score","Retentissement","#2B57A7")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=l,line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v:.1f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,11],title="/10"),height=280,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('bpi', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Sévérité":r.get("bpi_severity_score","—"),"Retentissement":r.get("bpi_interference_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
