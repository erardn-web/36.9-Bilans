"""tests/questionnaires/misc_scores.py — Cumberland CAIT, IKDC, Tegner, DHI, HIT-6"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Cumberland Ankle Instability Tool (CAIT) ──────────────────────────────────
@register_test
class DHI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"dhi","nom":"DHI — Vertiges","tab_label":"🌀 DHI","categorie":"questionnaire",
                "tags":["vertiges","vestibulaire","équilibre","VPPB"],
                "description":"Dizziness Handicap Inventory — 25 items /100, impact des vertiges"}
    @classmethod
    def fields(cls): return [f"dhi_q{i}" for i in range(1,26)]+["dhi_score","dhi_physique","dhi_emotionnel","dhi_fonctionnel"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score total (/100)", "default": True},
            {"key": "sous_scores", "label": "Sous-scores (fonct., émot., physique)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
            {"key": "detail_items", "label": "Détail des items", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🌀 DHI — Inventaire du handicap lié aux vertiges</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">25 questions — Oui (4 pts) / Parfois (2 pts) / Non (0 pt). Score 0 = pas de handicap · 100 = handicap maximal.</div>', unsafe_allow_html=True)
        from collections import defaultdict
        collected={}; scores=defaultdict(int)
        subs={1:"P",2:"E",3:"F",4:"P",5:"F",6:"F",7:"P",8:"E",9:"P",10:"F",
              11:"E",12:"F",13:"P",14:"F",15:"E",16:"F",17:"P",18:"E",19:"P",20:"P",
              21:"E",22:"F",23:"E",24:"F",25:"F"}
        labels_q=[
            "Votre problème de vertige vous fait-il regarder où vous posez les pieds ?",
            "Votre problème de vertige est-il déprimant pour vous ?",
            "Est-ce que votre problème de vertige vous prive de voyages d'affaires ou de loisirs ?",
            "Marcher dans les allées d'un supermarché aggrave-t-il votre vertige ?",
            "Votre problème de vertige vous complique-t-il l'entrée/sortie du lit ?",
            "Votre problème de vertige vous contraint-il à limiter vos activités sociales ?",
            "Le fait de regarder en l'air aggrave-t-il votre problème de vertige ?",
            "Votre problème de vertige vous prive-t-il d'assumer plus de responsabilités ?",
            "Votre problème de vertige aggrave-t-il votre difficulté lors de promenades seul(e) ?",
            "Votre problème de vertige a-t-il un retentissement sur vos activités professionnelles/ménagères ?",
            "Avez-vous honte de votre problème de vertige devant autrui ?",
            "Votre problème de vertige vous prive-t-il de visiter des amis ou de la famille ?",
            "En raison de votre vertige, pouvez-vous décrire votre démarche comme titubante ?",
            "Votre problème de vertige rend-il difficile des sports ou activités physiques intenses ?",
            "Votre problème de vertige vous déprime-t-il parfois ?",
            "Votre problème de vertige vous complique-t-il les promenades seul(e) ?",
            "Marcher sur le trottoir aggrave-t-il votre vertige ?",
            "En raison de votre problème de vertige, est-il difficile pour vous de vous concentrer ?",
            "En raison de votre problème de vertige, est-il difficile de marcher dans votre maison la nuit ?",
            "Votre problème de vertige vous prive-t-il de rester seul(e) à la maison ?",
            "Votre problème de vertige vous fait-il vous sentir handicapé(e) ?",
            "Votre problème de vertige vous complique-t-il les relations avec votre famille et vos amis ?",
            "Avez-vous quelquefois des épisodes de dépression en raison de votre vertige ?",
            "Votre problème de vertige aggrave-t-il vos activités professionnelles ?",
            "En vous penchant en avant, votre problème de vertige aggrave-t-il votre vertige ?",
        ]
        total=0
        for i,q_label in enumerate(labels_q,1):
            k=f"dhi_q{i}"
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(q_label,[0,2,4],index=[0,2,4].index(stored) if stored in [0,2,4] else 0,
                format_func=lambda x:{0:"Non (0)",2:"Parfois (2)",4:"Oui (4)"}[x],
                horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val; scores[subs[i]]+=val
        collected.update({"dhi_score":total,"dhi_physique":scores["P"],"dhi_emotionnel":scores["E"],"dhi_fonctionnel":scores["F"]})
        color="#388e3c" if total<=16 else "#f57c00" if total<=36 else "#d32f2f"
        msg="Léger" if total<=16 else "Moyen" if total<=36 else "Sévère"
        st.markdown(f'<div class="score-box" style="background:{color}">DHI : {total}/100 — {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("dhi_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=16 else "#f57c00" if s<=36 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("dhi_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("dhi_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="DHI",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=16,line_dash="dot",line_color="#388e3c",annotation_text="≤16 léger")
        fig.add_hline(y=36,line_dash="dot",line_color="#f57c00",annotation_text="≤36 moyen")
        fig.update_layout(yaxis=dict(range=[0,105],title="DHI /100"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('dhi', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"DHI":r.get("dhi_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── HIT-6 Headache Impact Test ────────────────────────────────────────────────