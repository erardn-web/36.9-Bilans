"""tests/questionnaires/sport_main.py — K-SES, PRWE, BPI, MHQ"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── K-SES Knee Self-Efficacy Scale ────────────────────────────────────────────
@register_test
class PRWE(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"prwe","nom":"PRWE — Poignet/Main","tab_label":"🤚 PRWE",
                "categorie":"questionnaire","tags":["poignet","main","fonctionnel","douleur","fracture"],
                "description":"Patient-Rated Wrist Evaluation — douleur + fonction /150"}
    PAIN_ITEMS=[("prwe_p1","Au repos"),("prwe_p2","En répétant des mouvements de poignet"),
                ("prwe_p3","En portant un sac d'épicerie"),("prwe_p4","Au pire"),
                ("prwe_p5","Fréquence habituelle")]
    FUNC_SPECIFIC=[("prwe_fs1","Tourner une poignée de porte"),("prwe_fs2","Couper des aliments"),
                   ("prwe_fs3","Attacher des boutons"),("prwe_fs4","Pousser depuis un fauteuil"),
                   ("prwe_fs5","Porter un sac de 5 kg"),("prwe_fs6","Sécher après la douche"),
                   ("prwe_fs7","Tâches ménagères"),("prwe_fs8","Travailler"),("prwe_fs9","Loisirs habituels"),
                   ("prwe_fs10","Activités de votre famille ou amis")]
    @classmethod
    def fields(cls): return [k for k,_ in cls.PAIN_ITEMS+cls.FUNC_SPECIFIC]+["prwe_pain","prwe_func","prwe_total"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score PRWE (/100)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🤚 PRWE — Poignet/Main</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = aucune douleur/difficulté · 10 = pire douleur/incapable. Score total /150.</div>', unsafe_allow_html=True)
        collected={}
        st.markdown("**Douleur /50**")
        pain_vals=[]
        for k,label in self.PAIN_ITEMS:
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 0
            except: v=0
            val=st.slider(label,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; pain_vals.append(val)
        st.markdown("**Fonction /100**")
        func_vals=[]
        for k,label in self.FUNC_SPECIFIC:
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 0
            except: v=0
            val=st.slider(label,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; func_vals.append(val)
        pain=sum(pain_vals); func=sum(func_vals); total=pain+func
        collected.update({"prwe_pain":pain,"prwe_func":func,"prwe_total":total})
        color="#388e3c" if total<=30 else "#f57c00" if total<=80 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">PRWE : {total}/150 | Douleur:{pain}/50 Fonction:{func}/100</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("prwe_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=30 else "#f57c00" if s<=80 else "#d32f2f"
        return {"score":s,"interpretation":f"{s}/150","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("prwe_total",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("prwe_total","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="PRWE",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,155],title="PRWE /150"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('prwe', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"PRWE":r.get("prwe_total","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── BPI Brief Pain Inventory ──────────────────────────────────────────────────