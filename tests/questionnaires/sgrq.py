"""tests/questionnaires/cardiopulmonaire.py — SGRQ, CRQ, LCADL, PCFS, Borg RPE, PSQI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Borg RPE ─────────────────────────────────────────────────────────────────
@register_test
class SGRQ(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"sgrq","nom":"SGRQ — Qualité de vie respiratoire","tab_label":"🫁 SGRQ",
                "categorie":"questionnaire","tags":["BPCO","asthme","respiratoire","qualité de vie"],
                "description":"St. George's Respiratory Questionnaire — 3 composantes : symptômes, activité, impact /100"}
    @classmethod
    def fields(cls):
        return ["sgrq_symptomes","sgrq_activite","sgrq_impact","sgrq_total","sgrq_notes"]
    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🫁 SGRQ — Qualité de vie respiratoire</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Saisie des scores calculés depuis le questionnaire papier SGRQ. Score 0 = meilleure santé · 100 = pire santé. MCID = 4 points.</div>', unsafe_allow_html=True)
        collected={}; cols=st.columns(3)
        for col,k,label,hint in [(cols[0],"sgrq_symptomes","Symptômes /100","Toux, expectorations, dyspnée"),
                                  (cols[1],"sgrq_activite","Activité /100","Limitation activités"),
                                  (cols[2],"sgrq_impact","Impact /100","Emploi, contrôle, panique")]:
            raw=lv(k,None)
            try: v=float(raw) if raw not in (None,"","None") else 0.0
            except: v=0.0
            val=col.number_input(label,0.0,100.0,v,0.1,key=f"{key_prefix}_{k}",help=hint)
            collected[k]=round(val,1)
        total=round((collected["sgrq_symptomes"]*0.0969+collected["sgrq_activite"]*0.4260+collected["sgrq_impact"]*0.4771),1)
        collected["sgrq_total"]=total
        collected["sgrq_notes"]=st.text_area("Notes",value=lv("sgrq_notes",""),height=60,key=f"{key_prefix}_sgrq_notes")
        color="#388e3c" if total<=25 else "#f57c00" if total<=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">SGRQ total : {total}/100</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("sgrq_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=25 else "#f57c00" if s<=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s}/100 (MCID=4)","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("sgrq_total",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("sgrq_total","Total","#2B57A7"),("sgrq_symptomes","Symptômes","#D85A30"),("sgrq_activite","Activité","#1D9E75")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers",name=l,line=dict(color=c,width=2.5),marker=dict(size=8)))
        fig.add_hline(y=25,line_dash="dot",line_color="#388e3c",annotation_text="≤25 léger")
        fig.update_layout(yaxis=dict(range=[0,105],title="SGRQ /100"),height=320,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Total":r.get("sgrq_total","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── LCADL London Chest Activity of Daily Living ───────────────────────────────