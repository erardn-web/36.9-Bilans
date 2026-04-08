"""tests/questionnaires/misc_scores.py — Cumberland CAIT, IKDC, Tegner, DHI, HIT-6"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Cumberland Ankle Instability Tool (CAIT) ──────────────────────────────────
@register_test
class Tegner(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"tegner","nom":"Tegner — Niveau d'activité","tab_label":"🏅 Tegner","categorie":"questionnaire",
                "tags":["genou","activité","sport","LCA","niveau fonctionnel"],
                "description":"Tegner Activity Scale — niveau d'activité 0-10 avant blessure et actuel"}
    @classmethod
    def fields(cls): return ["tegner_avant","tegner_actuel"]
    OPTS={0:"0 — Incapacité au travail ou pension invalidité",1:"1 — Travail sédentaire",
          2:"2 — Travail léger (marche sur terrain inégal impossible)",3:"3 — Travail léger (marche possible), natation",
          4:"4 — Travail modérément lourd, ski fond, vélo, jogging",5:"5 — Travail lourd, compétition cyclisme, ski alpin",
          6:"6 — Sport loisir : tennis, badminton, hand, basket, ski",7:"7 — Compétition : tennis, athlétisme, motocross, hand, basket",
          8:"8 — Compétition : squash, badminton ou ski alpin de compétition",9:"9 — Compétition : football (D3/D4), hockey sur glace",
          10:"10 — Compétition nationale/internationale football"}

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "actuel", "label": "Niveau actuel", "default": True},
            {"key": "avant", "label": "Niveau avant blessure", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🏅 Tegner — Niveau d\'activité</div>', unsafe_allow_html=True)
        collected={}
        for k,label in [("tegner_avant","Niveau avant blessure"),("tegner_actuel","Niveau actuel")]:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 5
            except: stored=5
            val=st.selectbox(label,list(self.OPTS.keys()),index=stored,format_func=lambda x:self.OPTS[x],key=f"{key_prefix}_{k}")
            collected[k]=val
        diff=collected["tegner_actuel"]-collected["tegner_avant"]
        color="#388e3c" if diff>=0 else "#f57c00" if diff>=-2 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">Avant: {collected["tegner_avant"]}/10 | Actuel: {collected["tegner_actuel"]}/10 | Diff: {diff:+d}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("tegner_actuel",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=7 else "#f57c00" if s>=4 else "#d32f2f"
        return {"score":s,"interpretation":f"Actuel:{s:.0f}/10","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data): return str(data.get("tegner_actuel","")).strip() not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("tegner_avant","Avant","#aaa"),("tegner_actuel","Actuel","#2B57A7")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=l,line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,11],title="Tegner /10"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('tegner', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Avant":r.get("tegner_avant","—"),"Actuel":r.get("tegner_actuel","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── DHI Dizziness Handicap Inventory ─────────────────────────────────────────