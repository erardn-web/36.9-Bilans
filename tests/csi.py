"""tests/questionnaires/other_scores.py — IKDC, CSI, QBPDS, ATRS, WOSI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── IKDC ─────────────────────────────────────────────────────────────────────
@register_test
class CSI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"csi","nom":"CSI — Sensibilisation centrale","tab_label":"⚡ CSI","categorie":"questionnaire",
                "tags":["sensibilisation centrale","douleur chronique","psychosocial"],
                "description":"Central Sensitization Inventory — 25 items /100. Seuil ≥ 40"}
    @classmethod
    def fields(cls): return [f"csi_q{i}" for i in range(1,26)]+["csi_score"]
    CSI_QUESTIONS=[
        "Je ressens de la douleur dans tout mon corps","Je manque d'énergie",
        "J'ai des troubles du sommeil","Je souffre de raideurs musculaires",
        "Je souffre de difficultés de concentration","J'ai la peau sensible au toucher",
        "Je me sens stressé(e)","Je ressens de la douleur au moindre effort",
        "Je ressens de la douleur qui brûle","Je souffre de maux de tête",
        "J'ai besoin d'uriner souvent","Mes jambes se contractent ou font des spasmes",
        "J'ai du mal à m'endormir ou à rester endormi","J'ai du mal à rester assis longtemps",
        "Je me sens anxieux(se)","Je souffre d'inconfort pelvien",
        "J'ai des indigestions ou le ventre irritable","Je suis fatigué(e)",
        "J'ai des troubles de l'humeur","Je souffre de maux de tête derrière la tête",
        "Ma vision est parfois floue","Je souffre de nausées",
        "Je souffre de sensibilité à la lumière","Mes pieds/mains sont engourdis",
        "J'ai des difficultés à avaler",
    ]
    OPTS=["0 — Jamais","1 — Rarement","2 — Parfois","3 — Souvent","4 — Toujours"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score CSI (/100)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">⚡ CSI — Inventaire de sensibilisation centrale</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = jamais · 4 = toujours. Score ≥ 40 : sensibilisation centrale probable.</div>', unsafe_allow_html=True)
        collected={}; total=0
        for i,q in enumerate(self.CSI_QUESTIONS,1):
            k=f"csi_q{i}"
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(q,[0,1,2,3,4],index=stored,format_func=lambda x:self.OPTS[x],horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["csi_score"]=total
        color="#d32f2f" if total>=53 else "#f57c00" if total>=40 else "#388e3c"
        msg="Sévère" if total>=53 else "Modérée" if total>=40 else "Légère/Absente"
        st.markdown(f'<div class="score-box" style="background:{color}">CSI : {total}/100 — Sensibilisation {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("csi_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s>=53 else "#f57c00" if s>=40 else "#388e3c"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("csi_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("csi_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="CSI",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=40,line_dash="dot",line_color="#f57c00",annotation_text="Seuil sensibilisation ≥40")
        fig.update_layout(yaxis=dict(range=[0,105],title="CSI /100"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"CSI":r.get("csi_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── QBPDS Quebec Back Pain Disability Scale ───────────────────────────────────