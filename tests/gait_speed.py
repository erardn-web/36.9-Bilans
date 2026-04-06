"""tests/questionnaires/rhumato_geriatrie.py — HAQ, BASDAI, DAS28, Frailty, FRAIL, Gait Speed"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── HAQ Health Assessment Questionnaire ──────────────────────────────────────
@register_test
class GaitSpeed4m(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"gait_speed","nom":"Vitesse de marche 4m","tab_label":"🚶 Vitesse 4m",
                "categorie":"test_clinique","tags":["marche","gériatrie","fragilité","vitesse","SPPB"],
                "description":"Gait Speed 4 mètres — prédicteur de mortalité et fragilité chez le sujet âgé"}
    @classmethod
    def fields(cls): return ["gait_temps_1","gait_temps_2","gait_vitesse","gait_aide"]
    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🚶 Vitesse de marche 4 mètres</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Mesurer le temps sur 4 mètres à vitesse habituelle. Seuil fragilité < 0.8 m/s. Seuil sarcopénie < 1.0 m/s.</div>', unsafe_allow_html=True)
        collected={}
        c1,c2=st.columns(2)
        t1=c1.number_input("Essai 1 (s)",0.0,60.0,float(lv("gait_temps_1",0) or 0),0.1,key=f"{key_prefix}_gait_t1")
        t2=c2.number_input("Essai 2 (s)",0.0,60.0,float(lv("gait_temps_2",0) or 0),0.1,key=f"{key_prefix}_gait_t2")
        best=min(t for t in [t1,t2] if t>0) if any(t>0 for t in [t1,t2]) else 0
        vitesse=round(4/best,2) if best>0 else 0.0
        collected.update({"gait_temps_1":t1,"gait_temps_2":t2,"gait_vitesse":vitesse})
        aide_opts=["Aucune","Canne","Déambulateur"]
        raw_aide=lv("gait_aide","Aucune")
        aide=st.selectbox("Aide technique",aide_opts,index=aide_opts.index(raw_aide) if raw_aide in aide_opts else 0,key=f"{key_prefix}_gait_aide")
        collected["gait_aide"]=aide
        if vitesse>0:
            color="#388e3c" if vitesse>=1.0 else "#f57c00" if vitesse>=0.8 else "#d32f2f"
            msg="Normal" if vitesse>=1.0 else "Risque sarcopénie" if vitesse>=0.8 else "Fragile/Sarcopénie"
            st.metric("Meilleure vitesse",f"{vitesse} m/s")
            st.markdown(f'<div class="score-box" style="background:{color}">Vitesse : {vitesse} m/s — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("gait_vitesse",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        if s<=0: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=1.0 else "#f57c00" if s>=0.8 else "#d32f2f"
        return {"score":s,"interpretation":f"{s} m/s","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("gait_vitesse",""))>0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("gait_vitesse","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Vitesse 4m",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.2f}" for v in yp],textposition="top center"))
        fig.add_hline(y=0.8,line_dash="dot",line_color="#f57c00",annotation_text="Fragilité <0.8 m/s")
        fig.add_hline(y=1.0,line_dash="dot",line_color="#388e3c",annotation_text="Normal ≥1.0 m/s")
        fig.update_layout(yaxis=dict(range=[0,2.5],title="Vitesse (m/s)"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Vitesse (m/s)":r.get("gait_vitesse","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
