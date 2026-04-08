"""tests/questionnaires/cardiopulmonaire.py — SGRQ, CRQ, LCADL, PCFS, Borg RPE, PSQI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Borg RPE ─────────────────────────────────────────────────────────────────
@register_test
class BorgRPE(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"borg_rpe","nom":"Borg RPE — Effort perçu","tab_label":"💨 Borg RPE",
                "categorie":"test_clinique","tags":["effort","dyspnée","BPCO","cardiaque","réhabilitation"],
                "description":"Borg RPE / CR10 — effort perçu 0-10 (dyspnée et fatigue à l'effort)"}
    @classmethod
    def fields(cls):
        return ["borg_dyspnee_repos","borg_fatigue_repos","borg_dyspnee_effort","borg_fatigue_effort","borg_notes"]
    OPTS={0:"0 — Rien du tout",0.5:"0.5 — Très très légère",1:"1 — Très légère",2:"2 — Légère",
          3:"3 — Modérée",4:"4 — Assez forte",5:"5 — Forte",6:"6",7:"7 — Très forte",8:"8",
          9:"9 — Très très forte",10:"10 — Maximale"}
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "dyspnee", "label": "Borg dyspnée", "default": True},
            {"key": "fatigue", "label": "Borg fatigue", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💨 Borg RPE — Effort perçu</div>', unsafe_allow_html=True)
        collected={}
        c1,c2=st.columns(2)
        for col,k,label in [(c1,"borg_dyspnee_repos","Dyspnée au repos"),(c1,"borg_fatigue_repos","Fatigue au repos"),
                             (c2,"borg_dyspnee_effort","Dyspnée à l'effort"),(c2,"borg_fatigue_effort","Fatigue à l'effort")]:
            raw=lv(k,None); vals=list(self.OPTS.keys())
            try: stored=float(raw) if raw not in (None,"","None") else 0.0
            except: stored=0.0
            stored=stored if stored in vals else 0
            val=col.selectbox(label,vals,index=vals.index(stored),format_func=lambda x:self.OPTS[x],key=f"{key_prefix}_{k}")
            collected[k]=val
        collected["borg_notes"]=st.text_input("Notes",value=lv("borg_notes",""),key=f"{key_prefix}_borg_notes")
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("borg_dyspnee_effort",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=3 else "#f57c00" if s<=6 else "#d32f2f"
        return {"score":s,"interpretation":f"Dyspnée effort:{s}/10","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        return str(data.get("borg_dyspnee_effort","")).strip() not in ("","None","nan")
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("borg_dyspnee_effort","Dyspnée effort","#2B57A7"),("borg_fatigue_effort","Fatigue effort","#D85A30")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=l,line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,11],title="Borg /10"),height=280,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Dyspnée":r.get("borg_dyspnee_effort","—"),"Fatigue":r.get("borg_fatigue_effort","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── SGRQ St. George's Respiratory Questionnaire ───────────────────────────────