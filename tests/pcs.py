"""tests/questionnaires/douleur_psy.py — PCS, BPI, PHQ-9, GAD-7, ISI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── PCS Pain Catastrophizing Scale ───────────────────────────────────────────
@register_test
class PCS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"pcs","nom":"PCS — Catastrophisation douleur","tab_label":"😰 PCS",
                "categorie":"questionnaire","tags":["catastrophisation","douleur chronique","psychosocial","kinésiophobie"],
                "description":"Pain Catastrophizing Scale — 13 items /52. Seuil clinique ≥ 30"}
    ITEMS=[
        ("pcs_q1","Je pense constamment à quel point ça fait mal"),("pcs_q2","Je me dis que ça doit aller mieux"),
        ("pcs_q3","C'est terrible et je pense que ça ne s'améliorera jamais"),("pcs_q4","C'est horrible et je sens que ça me dépasse"),
        ("pcs_q5","J'ai le sentiment de ne plus pouvoir le supporter"),("pcs_q6","J'ai peur que la douleur devienne pire"),
        ("pcs_q7","Je pense à d'autres expériences douloureuses"),("pcs_q8","Je veux désespérément que la douleur disparaisse"),
        ("pcs_q9","Je ne peux pas me sortir ça de la tête"),("pcs_q10","Je pense constamment à combien ça fait mal"),
        ("pcs_q11","Je pense constamment que je veux arrêter la douleur"),("pcs_q12","Il n'y a rien que je puisse faire pour réduire l'intensité"),
        ("pcs_q13","Je me demande si quelque chose de grave peut se produire"),
    ]
    OPTS=["0 — Pas du tout","1 — Un peu","2 — Modérément","3 — Beaucoup","4 — Tout le temps"]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS]+["pcs_rumination","pcs_amplification","pcs_desespoir","pcs_total"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score PCS (/52)", "default": True},
            {"key": "sous_scores", "label": "Sous-scores (rumination, amplification, désespoir)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">😰 PCS — Catastrophisation de la douleur</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Quand vous avez de la douleur, dans quelle mesure avez-vous ces pensées. Score ≥ 30/52 = catastrophisation cliniquement significative.</div>', unsafe_allow_html=True)
        collected={}; total=0
        rum=0; amp=0; desp=0
        rum_keys={"pcs_q8","pcs_q9","pcs_q10","pcs_q11"}
        amp_keys={"pcs_q6","pcs_q7","pcs_q13"}
        desp_keys={"pcs_q1","pcs_q2","pcs_q3","pcs_q4","pcs_q5","pcs_q12"}
        for k,label in self.ITEMS:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(label,list(range(5)),index=stored,format_func=lambda x:self.OPTS[x],horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
            if k in rum_keys: rum+=val
            if k in amp_keys: amp+=val
            if k in desp_keys: desp+=val
        collected.update({"pcs_rumination":rum,"pcs_amplification":amp,"pcs_desespoir":desp,"pcs_total":total})
        color="#d32f2f" if total>=30 else "#f57c00" if total>=20 else "#388e3c"
        msg="Catastrophisation significative" if total>=30 else "Modérée" if total>=20 else "Légère/Absente"
        st.markdown(f'<div class="score-box" style="background:{color}">PCS : {total}/52 — {msg} | Rum:{rum} Amp:{amp} Désesp:{desp}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("pcs_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s>=30 else "#f57c00" if s>=20 else "#388e3c"
        return {"score":s,"interpretation":f"{s:.0f}/52","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("pcs_total",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("pcs_total","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="PCS",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=30,line_dash="dot",line_color="#d32f2f",annotation_text="Seuil clinique ≥30")
        fig.update_layout(yaxis=dict(range=[0,54],title="PCS /52"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"PCS":r.get("pcs_total","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── PHQ-9 Depression ──────────────────────────────────────────────────────────