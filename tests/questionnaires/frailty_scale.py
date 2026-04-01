"""tests/questionnaires/rhumato_geriatrie.py — HAQ, BASDAI, DAS28, Frailty, FRAIL, Gait Speed"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── HAQ Health Assessment Questionnaire ──────────────────────────────────────
@register_test
class ClinicalFrailtyScale(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"frailty_scale","nom":"Clinical Frailty Scale","tab_label":"👴 Frailty Scale",
                "categorie":"questionnaire","tags":["fragilité","gériatrie","dépendance","âgé"],
                "description":"Clinical Frailty Scale (Rockwood) — 9 niveaux de fragilité"}
    GRADES={
        1:"1 — Très bien portant (actif, énergique, motivé, en forme)",
        2:"2 — Bien portant (sans maladie active, mais moins bien que grade 1)",
        3:"3 — Bien portant avec traitement (symptômes contrôlés)",
        4:"4 — Vulnérable (ralentissement ou fatigable mais autonome)",
        5:"5 — Légèrement fragile (dépendant pour IADL: finances, transport)",
        6:"6 — Modérément fragile (aide pour IADL et AVQ internes)",
        7:"7 — Sévèrement fragile (totalement dépendant AVQ ou en fin de vie stable)",
        8:"8 — Très sévèrement fragile (entièrement dépendant, pronostic vital engagé)",
        9:"9 — Fin de vie (espérance de vie < 6 mois)",
    }
    @classmethod
    def fields(cls): return ["frailty_grade","frailty_notes"]
    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">👴 Clinical Frailty Scale</div>', unsafe_allow_html=True)
        raw=lv("frailty_grade",None)
        try: stored=int(float(raw)) if raw not in (None,"","None") else 1
        except: stored=1
        grade=st.radio("Grade de fragilité",list(range(1,10)),index=stored-1,
            format_func=lambda x:self.GRADES[x],key=f"{key_prefix}_frailty_grade")
        notes=st.text_area("Notes",value=lv("frailty_notes",""),height=60,key=f"{key_prefix}_frailty_notes")
        collected={"frailty_grade":grade,"frailty_notes":notes}
        colors=["#388e3c","#388e3c","#7cb87e","#f57c00","#f57c00","#e65100","#d32f2f","#d32f2f","#922b21"]
        st.markdown(f'<div class="score-box" style="background:{colors[grade-1]}">Fragilité Grade {grade}/9</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("frailty_grade",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        colors=["#388e3c","#388e3c","#7cb87e","#f57c00","#f57c00","#e65100","#d32f2f","#d32f2f","#922b21"]
        return {"score":s,"interpretation":f"Grade {s:.0f}/9","color":colors[int(s)-1],"details":{}}
    @classmethod
    def is_filled(cls,data): return str(data.get("frailty_grade","")).strip() not in ("","None","nan")
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("frailty_grade","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Fragilité",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"G{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=5,line_dash="dot",line_color="#f57c00",annotation_text="Fragile ≥5")
        fig.update_layout(yaxis=dict(range=[0.5,9.5],tickvals=list(range(1,10)),title="Grade"),height=250,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Grade fragilité":r.get("frailty_grade","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── FRAIL Scale ───────────────────────────────────────────────────────────────