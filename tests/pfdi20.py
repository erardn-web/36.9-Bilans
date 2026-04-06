"""tests/questionnaires/urogyno.py — ICIQ-UI SF, PFDI-20, PFIQ-7"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── ICIQ-UI SF ────────────────────────────────────────────────────────────────
@register_test
class PFDI20(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"pfdi20","nom":"PFDI-20 — Plancher pelvien","tab_label":"🔵 PFDI-20",
                "categorie":"questionnaire","tags":["plancher pelvien","incontinence","prolapsus","urogynéco"],
                "description":"Pelvic Floor Distress Inventory-20 — 3 sous-échelles : POPDI, CRADI, UDI /300"}
    POPDI=[("pfdi_pop1","Pression ou pesanteur dans la région pelvienne"),
           ("pfdi_pop2","Pesanteur ou sensations dans le vagin"),
           ("pfdi_pop3","Sensation de bombement ou de quelque chose qui sort du vagin"),
           ("pfdi_pop4","Obligation de pousser sur le vagin ou le rectum pour vider les intestins"),
           ("pfdi_pop5","Difficulté à vider les intestins"),
           ("pfdi_pop6","Mictions difficiles ou incomplètes"),]
    CRADI=[("pfdi_cra1","Pression ou pesanteur dans la région anale"),
           ("pfdi_cra2","Sensation de ne pas avoir vidé complètement les intestins"),
           ("pfdi_cra3","Pertes fécales lors d'efforts physiques"),
           ("pfdi_cra4","Pertes fécales avant d'atteindre les toilettes"),
           ("pfdi_cra5","Pertes de gaz intestinaux involontaires"),
           ("pfdi_cra6","Douleur lors de la défécation"),
           ("pfdi_cra7","Urgences intestinales sévères"),
           ("pfdi_cra8","Difficultés intestinales affectant la qualité de vie"),]
    UDI=[("pfdi_udi1","Fréquence urinaire augmentée"),
         ("pfdi_udi2","Urgences urinaires"),
         ("pfdi_udi3","Pertes urinaires liées à l'urgence"),
         ("pfdi_udi4","Pertes urinaires à l'effort"),
         ("pfdi_udi5","Pertes urinaires en position couchée"),
         ("pfdi_udi6","Difficultés à vider la vessie"),]
    @classmethod
    def fields(cls):
        all_items=cls.POPDI+cls.CRADI+cls.UDI
        return [k for k,_ in all_items]+["pfdi_popdi","pfdi_cradi","pfdi_udi","pfdi_total"]
    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🔵 PFDI-20 — Plancher pelvien</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = pas du tout gêné(e) · 3 = très gêné(e). Score total /300 (3 sous-échelles × 100).</div>', unsafe_allow_html=True)
        collected={}
        def _sec(title,items):
            with st.expander(title,expanded=False):
                sub_total=0; sub_n=0
                for k,label in items:
                    raw=lv(k,None); present_raw=lv(f"{k}_present",None)
                    present=str(present_raw) in ("1","True","Oui")
                    pres=st.checkbox(f"Présent : {label}",value=present,key=f"{key_prefix}_{k}_pres")
                    collected[f"{k}_present"]=1 if pres else 0
                    if pres:
                        try: stored=int(float(raw)) if raw not in (None,"","None") else 0
                        except: stored=0
                        val=st.radio("Combien ça vous gêne ?",list(range(4)),index=stored,
                            format_func=lambda x:["0 — Pas du tout","1 — Légèrement","2 — Modérément","3 — Beaucoup"][x],
                            key=f"{key_prefix}_{k}",horizontal=True)
                        collected[k]=val; sub_total+=val+1; sub_n+=1
                    else:
                        collected[k]=0
                return round((sub_total/sub_n)*25,1) if sub_n else 0
        pop=_sec("POPDI — Prolapsus (6 items)",self.POPDI)
        cra=_sec("CRADI — Intestin (8 items)",self.CRADI)
        udi=_sec("UDI — Urinaire (6 items)",self.UDI)
        total=round(pop+cra+udi,1)
        collected.update({"pfdi_popdi":pop,"pfdi_cradi":cra,"pfdi_udi":udi,"pfdi_total":total})
        color="#388e3c" if total<=60 else "#f57c00" if total<=150 else "#d32f2f"
        c1,c2,c3=st.columns(3)
        c1.markdown(f'<div class="score-box" style="background:{color};font-size:.85rem">POPDI<br>{pop}/100</div>',unsafe_allow_html=True)
        c2.markdown(f'<div class="score-box" style="background:{color};font-size:.85rem">CRADI<br>{cra}/100</div>',unsafe_allow_html=True)
        c3.markdown(f'<div class="score-box" style="background:{color};font-size:.85rem">UDI<br>{udi}/100</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="score-box" style="background:{color}">PFDI-20 total : {total}/300</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("pfdi_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=60 else "#f57c00" if s<=150 else "#d32f2f"
        return {"score":s,"interpretation":f"{s}/300","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("pfdi_total",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("pfdi_udi","UDI","#2B57A7"),("pfdi_popdi","POPDI","#1D9E75"),("pfdi_cradi","CRADI","#D85A30")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers",name=l,line=dict(color=c,width=2.5),marker=dict(size=8)))
        fig.update_layout(yaxis=dict(range=[0,105],title="Score /100"),height=320,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Total":r.get("pfdi_total","—"),"UDI":r.get("pfdi_udi","—"),"POPDI":r.get("pfdi_popdi","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
