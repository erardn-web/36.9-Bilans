"""tests/questionnaires/urogyno.py — ICIQ-UI SF, PFDI-20, PFIQ-7"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── ICIQ-UI SF ────────────────────────────────────────────────────────────────
@register_test
class ICIQUI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"iciq_ui","nom":"ICIQ-UI SF — Incontinence urinaire","tab_label":"💧 ICIQ-UI",
                "categorie":"questionnaire","tags":["incontinence","pelvi-périnéal","urogynéco","femme","homme"],
                "description":"ICIQ-UI Short Form — 3 questions + 1 diagnostic, /21. Score ≥ 1 = incontinence"}
    @classmethod
    def fields(cls): return ["iciq_frequence","iciq_quantite","iciq_impact","iciq_score","iciq_type_list"]
    FREQ_OPTS={0:"0 — Jamais",1:"1 — 1×/semaine ou moins",2:"2 — 2–3×/semaine",
               3:"3 — 1×/jour",4:"4 — Plusieurs fois/jour",5:"5 — Tout le temps"}
    QTE_OPTS={0:"0 — Aucune",2:"2 — Petite quantité",4:"4 — Quantité modérée",6:"6 — Grande quantité"}
    TYPE_OPTS=["Pertes avant d'atteindre les toilettes","Pertes lors d'efforts (toux, éternuement, activité physique)",
               "Pertes sans raison apparente","Pertes permanentes","Pertes pendant le sommeil",
               "Pertes lors de rapports sexuels"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score ICIQ-UI (/21)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💧 ICIQ-UI SF — Incontinence urinaire</div>', unsafe_allow_html=True)
        collected={}
        # Q1 Fréquence
        raw=lv("iciq_frequence",None)
        try: stored_f=int(float(raw)) if raw not in (None,"","None") else 0
        except: stored_f=0
        freq=st.selectbox("À quelle fréquence perdez-vous des urines ?",
            list(self.FREQ_OPTS.keys()),index=list(self.FREQ_OPTS.keys()).index(stored_f) if stored_f in self.FREQ_OPTS else 0,
            format_func=lambda x:self.FREQ_OPTS[x],key=f"{key_prefix}_iciq_freq")
        collected["iciq_frequence"]=freq
        # Q2 Quantité
        raw=lv("iciq_quantite",None)
        try: stored_q=int(float(raw)) if raw not in (None,"","None") else 0
        except: stored_q=0
        qte=st.selectbox("Quelle quantité d'urines perdez-vous habituellement ?",
            list(self.QTE_OPTS.keys()),index=list(self.QTE_OPTS.keys()).index(stored_q) if stored_q in self.QTE_OPTS else 0,
            format_func=lambda x:self.QTE_OPTS[x],key=f"{key_prefix}_iciq_qte")
        collected["iciq_quantite"]=qte
        # Q3 Impact
        raw=lv("iciq_impact",None)
        try: stored_i=int(float(raw)) if raw not in (None,"","None") else 0
        except: stored_i=0
        impact=st.slider("Dans quelle mesure ces pertes affectent-elles votre vie quotidienne ? (0=pas du tout · 10=beaucoup)",0,10,stored_i,key=f"{key_prefix}_iciq_imp")
        collected["iciq_impact"]=impact
        # Score
        score=freq+qte+impact
        collected["iciq_score"]=score
        # Type (diagnostic)
        raw_type=str(lv("iciq_type_list","") or "")
        stored_types=[x for x in raw_type.split("|") if x in self.TYPE_OPTS]
        types=st.multiselect("Quand perdez-vous des urines ? (diagnostic)",self.TYPE_OPTS,default=stored_types,key=f"{key_prefix}_iciq_type")
        collected["iciq_type_list"]="|".join(types)
        if score==0:
            st.success("✅ Aucune incontinence")
        else:
            color="#388e3c" if score<=5 else "#f57c00" if score<=12 else "#d32f2f"
            sev="Légère" if score<=5 else "Modérée" if score<=12 else "Sévère"
            st.markdown(f'<div class="score-box" style="background:{color}">ICIQ-UI : {score}/21 — {sev}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("iciq_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        if s==0: return {"score":0,"interpretation":"Continence","color":"#388e3c","details":{}}
        color="#388e3c" if s<=5 else "#f57c00" if s<=12 else "#d32f2f"
        sev="Légère" if s<=5 else "Modérée" if s<=12 else "Sévère"
        return {"score":s,"interpretation":f"{s:.0f}/21 — {sev}","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        return str(data.get("iciq_score","")).strip() not in ("","None","nan")
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("iciq_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="ICIQ",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=1,line_dash="dot",line_color="#d32f2f",annotation_text="Seuil incontinence ≥1")
        fig.update_layout(yaxis=dict(range=[0,22],title="ICIQ /21"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"ICIQ":r.get("iciq_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── PFDI-20 Pelvic Floor Distress Inventory ───────────────────────────────────