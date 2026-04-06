"""tests/questionnaires/neurologie.py — Barthel, 10MWT, Ashworth, Fugl-Meyer"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Barthel Index ─────────────────────────────────────────────────────────────
@register_test
class TenMWT(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"ten_mwt","nom":"10MWT — Vitesse de marche","tab_label":"🚶 10MWT",
                "categorie":"test_clinique","tags":["marche","neurologie","AVC","vitesse","Parkinson"],
                "description":"10-Metre Walk Test — vitesse de marche confortable et maximale (m/s)"}
    @classmethod
    def fields(cls): return ["ten_mwt_confort_temps","ten_mwt_confort_vitesse","ten_mwt_max_temps","ten_mwt_max_vitesse","ten_mwt_aide","ten_mwt_notes"]
    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🚶 10MWT — Test de marche 10 mètres</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Mesurer le temps sur 10 mètres (vitesse confortable et maximale). Normale > 1.0 m/s. Seuil communautaire ≥ 0.8 m/s.</div>', unsafe_allow_html=True)
        collected={}
        c1,c2=st.columns(2)
        for col,k_t,k_v,label in [(c1,"ten_mwt_confort_temps","ten_mwt_confort_vitesse","Vitesse confortable"),
                                   (c2,"ten_mwt_max_temps","ten_mwt_max_vitesse","Vitesse maximale")]:
            raw=lv(k_t,None)
            try: t=float(raw) if raw not in (None,"","None") else 0.0
            except: t=0.0
            temps=col.number_input(f"{label} — Temps (s)",0.0,120.0,t,0.1,key=f"{key_prefix}_{k_t}")
            vitesse=round(10/temps,2) if temps>0 else 0.0
            col.metric(f"Vitesse {label}",f"{vitesse} m/s")
            collected[k_t]=temps; collected[k_v]=vitesse
        aide_opts=["Aucune","Canne","Déambulateur","Aide humaine"]
        raw_aide=lv("ten_mwt_aide","Aucune")
        aide=st.selectbox("Aide technique",aide_opts,index=aide_opts.index(raw_aide) if raw_aide in aide_opts else 0,key=f"{key_prefix}_ten_aide")
        notes=st.text_input("Notes",value=lv("ten_mwt_notes",""),key=f"{key_prefix}_ten_notes")
        collected.update({"ten_mwt_aide":aide,"ten_mwt_notes":notes})
        v=collected["ten_mwt_confort_vitesse"]
        color="#388e3c" if v>=1.0 else "#f57c00" if v>=0.8 else "#d32f2f"
        if v>0: st.markdown(f'<div class="score-box" style="background:{color}">Vitesse confort : {v} m/s</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("ten_mwt_confort_vitesse",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=1.0 else "#f57c00" if s>=0.8 else "#d32f2f"
        return {"score":s,"interpretation":f"{s} m/s","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("ten_mwt_confort_vitesse",""))>0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("ten_mwt_confort_vitesse","Confort","#2B57A7"),("ten_mwt_max_vitesse","Maximale","#1D9E75")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=l,line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v:.2f}" for v in yp],textposition="top center"))
        fig.add_hline(y=0.8,line_dash="dot",line_color="#f57c00",annotation_text="Seuil communautaire 0.8 m/s")
        fig.add_hline(y=1.0,line_dash="dot",line_color="#388e3c",annotation_text="Normal ≥1.0 m/s")
        fig.update_layout(yaxis=dict(range=[0,2.5],title="Vitesse (m/s)"),height=300,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Confort (m/s)":r.get("ten_mwt_confort_vitesse","—"),"Max (m/s)":r.get("ten_mwt_max_vitesse","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── Modified Ashworth Scale ───────────────────────────────────────────────────