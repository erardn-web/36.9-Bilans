"""tests/questionnaires/cardiopulmonaire.py — SGRQ, CRQ, LCADL, PCFS, Borg RPE, PSQI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Borg RPE ─────────────────────────────────────────────────────────────────
@register_test
class LCADL(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"lcadl","nom":"LCADL — Limitations respiratoires AVQ","tab_label":"🏠 LCADL",
                "categorie":"questionnaire","tags":["BPCO","respiratoire","AVQ","dyspnée","limitations"],
                "description":"London Chest Activity of Daily Living — 15 items, limitation AVQ liée à la dyspnée"}
    ITEMS=[("lcadl_q1","Soins personnels","Se sécher après le bain/douche"),
           ("lcadl_q2","Soins personnels","S'habiller le haut du corps"),
           ("lcadl_q3","Soins personnels","Mettre des chaussures/chaussettes"),
           ("lcadl_q4","Soins personnels","Se laver les cheveux"),
           ("lcadl_q5","Ménage","Faire les lits"),
           ("lcadl_q6","Ménage","Changer les draps"),
           ("lcadl_q7","Ménage","Laver les fenêtres/rideaux"),
           ("lcadl_q8","Ménage","Nettoyer (aspirateur, balai)"),
           ("lcadl_q9","Ménage","Petits travaux ménagers"),
           ("lcadl_q10","Loisirs","Marcher à l'intérieur"),
           ("lcadl_q11","Loisirs","Sortir de la maison"),
           ("lcadl_q12","Loisirs","Marcher dans la rue"),
           ("lcadl_q13","Loisirs","Activités de loisirs (jardinage, sport léger)"),
           ("lcadl_q14","Activités physiques","Monter les escaliers"),
           ("lcadl_q15","Activités physiques","Se pencher, s'accroupir"),]
    OPTS=["1 — Je ne ferais pas","2 — Je n'ai pas de problème","3 — Problème léger","4 — Problème modéré","5 — Je ne peux pas le faire"]
    @classmethod
    def fields(cls): return [k for k,*_ in cls.ITEMS]+["lcadl_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score LCADL (/90)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🏠 LCADL — Limitations respiratoires AVQ</div>', unsafe_allow_html=True)
        collected={}; total=0
        secs={}
        for k,sec,_ in self.ITEMS:
            secs.setdefault(sec,[]).append(k)
        for sec,keys in secs.items():
            with st.expander(sec,expanded=False):
                for k,s2,label in [(x,y,z) for x,y,z in self.ITEMS if y==sec]:
                    raw=lv(k,None)
                    try: stored=int(float(raw)) if raw not in (None,"","None") else None
                    except: stored=None
                    chosen=st.radio(label,[None]+list(range(1,6)),
                        format_func=lambda x,o=self.OPTS:"— Non renseigné —" if x is None else o[x-1],
                        index=(stored) if stored is not None else 0,
                        key=f"{key_prefix}_{k}",horizontal=True)
                    collected[k]=chosen if chosen is not None else ""
                    if chosen is not None: total+=chosen
        collected["lcadl_score"]=total
        color="#388e3c" if total<=25 else "#f57c00" if total<=45 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">LCADL : {total}/75</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("lcadl_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=25 else "#f57c00" if s<=45 else "#d32f2f"
        return {"score":s,"interpretation":f"{s}/75","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("lcadl_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("lcadl_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="LCADL",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[15,80],title="LCADL /75"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('lcadl', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"LCADL":r.get("lcadl_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── PCFS Post-COVID Functional Status ─────────────────────────────────────────