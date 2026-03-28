"""tests/tests_cliniques/quick_dash.py — QuickDASH (11 items)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

QDASH_ITEMS = [
    ("qd_1",  "Ouvrir un pot ou un bocal"),
    ("qd_2",  "Faire des tâches ménagères lourdes (laver les murs, les planchers)"),
    ("qd_3",  "Porter un sac à provisions ou une mallette"),
    ("qd_4",  "Se laver le dos"),
    ("qd_5",  "Utiliser un couteau pour couper des aliments"),
    ("qd_6",  "Activités de loisirs nécessitant peu d'effort (jouer aux cartes, tricoter)"),
    ("qd_7",  "Activités de loisirs provoquant des douleurs à votre bras, épaule ou main"),
    ("qd_8",  "Activités de loisirs nécessitant des mouvements libres du bras, épaule ou main"),
    ("qd_9",  "Difficultés à dormir à cause de douleurs de votre bras, épaule ou main"),
    ("qd_10", "Engourdissements ou picotements de votre bras, épaule ou main"),
    ("qd_11", "Difficultés dans votre travail ou activités quotidiennes habituelles"),
]
QDASH_OPTS = ["— Non renseigné —",
              "1 — Aucune difficulté",
              "2 — Légère difficulté",
              "3 — Difficulté modérée",
              "4 — Difficulté importante",
              "5 — Incapable"]

def _compute_qdash(answers):
    vals = [answers[k] for k in [i[0] for i in QDASH_ITEMS] if k in answers]
    if len(vals) < 10: return None
    return round((sum(vals)/len(vals) - 1) * 25, 1)

@register_test
class QuickDASH(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"quick_dash","nom":"QuickDASH","tab_label":"✋ QuickDASH",
                "categorie":"questionnaire","tags":["épaule", "coude", "poignet", "membre supérieur", "incapacité"],
                "description":"Disabilities of the Arm, Shoulder and Hand — épaule, coude, poignet — version courte 11 items /100"}

    @classmethod
    def fields(cls):
        return [i[0] for i in QDASH_ITEMS] + ["qdash_score","qdash_interpretation"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">QuickDASH — Incapacité du membre supérieur</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">11 questions sur la difficulté à réaliser des activités. '
                    'Seuil clinique significatif : > 10/100</div>', unsafe_allow_html=True)
        answers = {}; collected = {}
        for key, text in QDASH_ITEMS:
            stored = lv(key, "")
            idx = 0
            if stored not in ("", None):
                try: idx = int(float(stored))
                except: idx = 0
            chosen = st.radio(f"**{text}**", QDASH_OPTS, index=idx,
                              horizontal=True, key=f"{key_prefix}_{key}")
            if chosen == "— Non renseigné —":
                collected[key] = ""
            else:
                v = int(chosen.split(" — ")[0]); answers[key] = v; collected[key] = v

        score = _compute_qdash(answers)
        if score is not None:
            color = "#388e3c" if score <= 20 else "#f57c00" if score <= 40 else "#d32f2f"
            interp = ("Incapacité légère" if score <= 20
                      else "Incapacité modérée" if score <= 40
                      else "Incapacité sévère")
            st.markdown(f'<div class="score-box" style="background:{color};">'
                        f'QuickDASH : {score}/100 — {interp}</div>', unsafe_allow_html=True)
        collected.update({"qdash_score": score if score is not None else "",
                          "qdash_interpretation": interp if score is not None else ""})
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("qdash_score","")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go, pandas as pd
        vals = []
        for _, row in bilans_df.iterrows():
            try:
                import math; f = float(row.get("qdash_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                line=dict(color="#2B57A7",width=2.5), marker=dict(size=9),
                text=[f"{v:.0f}" for v in yp], textposition="top center"))
        for y,c,l in [(10,"#388e3c","10 légère"),(40,"#f57c00","40 modérée")]:
            fig.add_hline(y=y, line_dash="dot", line_color=c,
                          annotation_text=l, annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,105],title="QuickDASH /100"),
                          height=300, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        rows = [{"Bilan":lbl,"QuickDASH":row.get("qdash_score","—"),
                 "Incapacité":row.get("qdash_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
