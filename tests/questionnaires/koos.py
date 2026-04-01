"""tests/questionnaires/koos.py — KOOS (Knee Injury and Osteoarthritis Outcome Score)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

# Sous-échelles KOOS (items simplifiés)
KOOS_PAIN = [
    ("koos_p1", "Fréquence de la douleur au genou"),
    ("koos_p2", "Torsion/pivotement"),
    ("koos_p3", "Extension complète"),
    ("koos_p4", "Flexion complète"),
    ("koos_p5", "Marche sur terrain plat"),
    ("koos_p6", "Montée/descente des escaliers"),
    ("koos_p7", "La nuit au lit"),
    ("koos_p8", "Position assise ou couchée"),
    ("koos_p9", "Debout"),
]
KOOS_SYMP = [
    ("koos_s1", "Gonflement du genou"),
    ("koos_s2", "Craquements ou bruits"),
    ("koos_s3", "Accrochages"),
    ("koos_s4", "Amplitude des mouvements"),
    ("koos_s5", "Raideur matinale"),
    ("koos_s6", "Raideur après repos"),
    ("koos_s7", "Difficulté en descente"),
]
KOOS_ADL = [
    ("koos_a1",  "Descendre les escaliers"),
    ("koos_a2",  "Monter les escaliers"),
    ("koos_a3",  "Se relever en position assise"),
    ("koos_a4",  "Rester debout"),
    ("koos_a5",  "Se pencher vers le sol"),
    ("koos_a6",  "Marcher sur terrain plat"),
    ("koos_a7",  "Entrer/sortir d'une voiture"),
    ("koos_a8",  "Faire les courses"),
    ("koos_a9",  "Chausser des chaussettes"),
    ("koos_a10", "Se lever du lit"),
    ("koos_a11", "Enlever des chaussettes"),
    ("koos_a12", "Rester couché"),
    ("koos_a13", "Entrer/sortir de la baignoire"),
    ("koos_a14", "S'asseoir"),
    ("koos_a15", "S'asseoir/se lever des toilettes"),
    ("koos_a16", "Tâches ménagères lourdes"),
    ("koos_a17", "Tâches ménagères légères"),
]
KOOS_SPORT = [
    ("koos_sp1", "S'accroupir"),
    ("koos_sp2", "Courir"),
    ("koos_sp3", "Sauter"),
    ("koos_sp4", "Pivoter"),
    ("koos_sp5", "S'agenouiller"),
]
KOOS_QOL = [
    ("koos_q1", "Conscience du problème de genou"),
    ("koos_q2", "Modification du mode de vie"),
    ("koos_q3", "Manque de confiance"),
    ("koos_q4", "Difficultés générales"),
]

OPTS = ["0 — Aucune", "1 — Légère", "2 — Modérée", "3 — Sévère", "4 — Extrême"]


def _koos_sub_score(data, items):
    vals = []
    for k, _ in items:
        try:    vals.append(int(float(data.get(k, ""))))
        except: pass
    if not vals: return None
    return round(100 - (sum(vals) / len(vals)) * 25, 1)


@register_test
class KOOS(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "koos", "nom": "KOOS — Genou (score fonctionnel)",
            "tab_label": "🦵 KOOS",
            "categorie": "questionnaire",
            "tags": ["genou", "fonctionnel", "arthrose", "post-chirurgical", "LCA"],
            "description": "Knee Injury and Osteoarthritis Outcome Score — 5 sous-échelles /100",
        }

    @classmethod
    def fields(cls):
        all_items = KOOS_PAIN + KOOS_SYMP + KOOS_ADL + KOOS_SPORT + KOOS_QOL
        return [k for k, _ in all_items] + [
            "koos_pain", "koos_symptoms", "koos_adl", "koos_sport", "koos_qol"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦵 KOOS — Score fonctionnel du genou</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Pour chaque question, indiquez le niveau de difficulté '
            'ressenti cette semaine. 0 = aucune difficulté, 4 = extrême. '
            'Le score final est exprimé de 0 (problème extrême) à 100 (aucun problème).</div>',
            unsafe_allow_html=True)

        collected = {}

        def _render_section(title, items, key_suffix):
            with st.expander(title, expanded=False):
                for k, label in items:
                    raw = lv(k, None)
                    try:    stored = int(float(raw)) if raw not in (None, "", "None") else None
                    except: stored = None
                    opts_ext = [None] + list(range(5))
                    chosen = st.radio(label, opts_ext,
                        format_func=lambda x, o=OPTS: "— Non renseigné —" if x is None else o[x],
                        index=(stored + 1) if stored is not None else 0,
                        key=f"{key_prefix}_{key_suffix}_{k}", horizontal=True)
                    collected[k] = chosen if chosen is not None else ""

        _render_section("Douleur (P)", KOOS_PAIN, "pain")
        _render_section("Symptômes (S)", KOOS_SYMP, "symp")
        _render_section("Activités quotidiennes (A)", KOOS_ADL, "adl")
        _render_section("Sport & Loisirs (SP)", KOOS_SPORT, "sport")
        _render_section("Qualité de vie (Q)", KOOS_QOL, "qol")

        # Calcul scores
        for key_sub, items, field in [
            ("Pain", KOOS_PAIN, "koos_pain"),
            ("Symptoms", KOOS_SYMP, "koos_symptoms"),
            ("ADL", KOOS_ADL, "koos_adl"),
            ("Sport", KOOS_SPORT, "koos_sport"),
            ("QOL", KOOS_QOL, "koos_qol"),
        ]:
            s = _koos_sub_score(collected, items)
            collected[field] = s if s is not None else ""

        # Affichage résultats
        st.markdown("#### 📊 Résultats")
        cols = st.columns(5)
        labels = ["Douleur", "Symptômes", "AVQ", "Sport", "QoL"]
        fields = ["koos_pain", "koos_symptoms", "koos_adl", "koos_sport", "koos_qol"]
        for col, lbl, field in zip(cols, labels, fields):
            val = collected.get(field, "")
            try:
                v = float(val)
                color = "#388e3c" if v >= 70 else "#f57c00" if v >= 40 else "#d32f2f"
                col.markdown(f'<div class="score-box" style="background:{color};font-size:.9rem">'
                             f'{lbl}<br><b>{v:.0f}</b></div>', unsafe_allow_html=True)
            except:
                col.markdown(f'<div style="text-align:center;color:#aaa">{lbl}<br>—</div>',
                             unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls, data):
        scores = []
        for f in ["koos_pain","koos_symptoms","koos_adl","koos_sport","koos_qol"]:
            try:    scores.append(float(data.get(f, "")))
            except: pass
        if not scores: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        avg = round(sum(scores) / len(scores), 1)
        color = "#388e3c" if avg >= 70 else "#f57c00" if avg >= 40 else "#d32f2f"
        return {"score": avg, "interpretation": f"Moy. {avg}/100", "color": color, "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        for f in ["koos_pain", "koos_adl"]:
            try:
                if float(bilan_data.get(f, "")) >= 0: return True
            except: pass
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        fields_labels = [("koos_pain","Douleur","#2B57A7"),
                         ("koos_adl","AVQ","#1D9E75"),
                         ("koos_sport","Sport","#D85A30"),
                         ("koos_qol","QoL","#7F77DD")]
        for field, lbl, color in fields_labels:
            vals = []
            for _, row in bilans_df.iterrows():
                try:    vals.append(float(row.get(field, "")))
                except: vals.append(None)
            xp = [labels[i] for i, v in enumerate(vals) if v is not None]
            yp = [v for v in vals if v is not None]
            if xp:
                fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers",
                    name=lbl, line=dict(color=color, width=2.5), marker=dict(size=8)))
        fig.add_hline(y=70, line_dash="dot", line_color="#388e3c",
                      annotation_text="Bonne fonction", annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0, 105], title="KOOS /100"),
                          height=350, legend=dict(orientation="h", y=-0.2),
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        rows = [{"Bilan": lbl, "Douleur": row.get("koos_pain","—"),
                 "AVQ": row.get("koos_adl","—"), "Sport": row.get("koos_sport","—"),
                 "QoL": row.get("koos_qol","—")}
                for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
