"""tests/questionnaires/rhumato_geriatrie.py — HAQ, BASDAI, DAS28, Frailty, FRAIL, Gait Speed"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── HAQ Health Assessment Questionnaire ──────────────────────────────────────
@register_test
class HAQ(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"haq","nom":"HAQ — Polyarthrite rhumatoïde","tab_label":"🦴 HAQ",
                "categorie":"questionnaire","tags":["polyarthrite","rhumatologie","incapacité","fonctionnel"],
                "description":"Health Assessment Questionnaire Disability Index — 8 catégories /3, PR et rhumatismes"}
    CATEGORIES=[
        ("haq_s'habiller","S'habiller et se coiffer"),
        ("haq_lever","Se lever"),("haq_manger","Manger"),("haq_marcher","Marcher"),
        ("haq_hygiene","Hygiène"),("haq_atteindre","Atteindre"),("haq_saisir","Saisir"),
        ("haq_activites","Activités courantes"),
    ]
    OPTS=["0 — Sans aucune difficulté","1 — Avec quelque difficulté","2 — Avec beaucoup de difficulté","3 — Incapable de le faire"]
    @classmethod
    def fields(cls): return [k for k,_ in cls.CATEGORIES]+["haq_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score HAQ (/3)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦴 HAQ — Indice d\'incapacité fonctionnelle</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = aucune incapacité · 3 = incapacité maximale. MCID = 0.22.</div>', unsafe_allow_html=True)
        collected={}; vals=[]
        for k,label in self.CATEGORIES:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(f"**{label}**",list(range(4)),index=stored,format_func=lambda x:self.OPTS[x],horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; vals.append(val)
        score=round(sum(vals)/len(vals),2)
        collected["haq_score"]=score
        color="#388e3c" if score<0.5 else "#f57c00" if score<1.5 else "#d32f2f"
        msg="Légère" if score<0.5 else "Modérée" if score<1.5 else "Sévère"
        st.markdown(f'<div class="score-box" style="background:{color}">HAQ-DI : {score}/3 — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("haq_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<0.5 else "#f57c00" if s<1.5 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.2f}/3","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("haq_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("haq_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="HAQ",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"{v:.2f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,3.5],title="HAQ /3"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('haq', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"HAQ":r.get("haq_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── BASDAI Bath Ankylosing Spondylitis Disease Activity Index ─────────────────