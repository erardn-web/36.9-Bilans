"""tests/questionnaires/sport_main.py — K-SES, PRWE, BPI, MHQ"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── K-SES Knee Self-Efficacy Scale ────────────────────────────────────────────
@register_test
class KSES(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"k_ses","nom":"K-SES — Auto-efficacité genou","tab_label":"🏃 K-SES",
                "categorie":"questionnaire","tags":["genou","auto-efficacité","LCA","confiance","sport"],
                "description":"Knee Self-Efficacy Scale — confiance en son genou, 4 sous-échelles /10"}
    ITEMS_NOW=[
        ("kses_n1","Monter les escaliers"),("kses_n2","Descendre les escaliers"),
        ("kses_n3","Marcher sur terrain inégal"),("kses_n4","Sauter sur une jambe"),
        ("kses_n5","Pivoter"),("kses_n6","Courir"),("kses_n7","Pratiquer mon sport habituel"),
    ]
    ITEMS_FUTURE=[
        ("kses_f1","Capacité à récupérer complètement"),("kses_f2","Capacité à pratiquer le sport"),
        ("kses_f3","Absence de douleur à l'avenir"),
    ]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS_NOW+cls.ITEMS_FUTURE]+["kses_now","kses_future","kses_total"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score K-SES (/100)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🏃 K-SES — Confiance dans son genou</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = pas du tout confiant · 10 = totalement confiant. Score ≥ 8 = bonne auto-efficacité.</div>', unsafe_allow_html=True)
        collected={}
        st.markdown("**Capacités actuelles**")
        now_vals=[]
        for k,label in self.ITEMS_NOW:
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 5
            except: v=5
            val=st.slider(label,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; now_vals.append(val)
        st.markdown("**Perspectives futures**")
        fut_vals=[]
        for k,label in self.ITEMS_FUTURE:
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 5
            except: v=5
            val=st.slider(label,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; fut_vals.append(val)
        now=round(sum(now_vals)/len(now_vals),1)
        fut=round(sum(fut_vals)/len(fut_vals),1)
        total=round((now+fut)/2,1)
        collected.update({"kses_now":now,"kses_future":fut,"kses_total":total})
        color="#388e3c" if total>=8 else "#f57c00" if total>=5 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">K-SES : {total}/10 | Actuel:{now} Futur:{fut}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("kses_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=8 else "#f57c00" if s>=5 else "#d32f2f"
        return {"score":s,"interpretation":f"{s}/10","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("kses_total",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("kses_total","Total","#2B57A7"),("kses_now","Actuel","#1D9E75"),("kses_future","Futur","#D85A30")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=l,line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v:.1f}" for v in yp],textposition="top center"))
        fig.add_hline(y=8,line_dash="dot",line_color="#388e3c",annotation_text="Bonne efficacité ≥8")
        fig.update_layout(yaxis=dict(range=[0,11],title="K-SES /10"),height=300,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('k_ses', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"K-SES":r.get("kses_total","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── PRWE Patient-Rated Wrist Evaluation ──────────────────────────────────────