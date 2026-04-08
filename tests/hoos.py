"""tests/questionnaires/hoos.py — HOOS (Hip disability and Osteoarthritis Outcome Score)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

HOOS_PAIN = [
    ("hoos_p1", "Fréquence de la douleur à la hanche"),
    ("hoos_p2", "Torsion/pivotement"),
    ("hoos_p3", "Extension complète"),
    ("hoos_p4", "Flexion complète"),
    ("hoos_p5", "Marche sur terrain plat"),
    ("hoos_p6", "Montée/descente des escaliers"),
    ("hoos_p7", "La nuit au lit"),
    ("hoos_p8", "Position assise ou couchée"),
    ("hoos_p9", "Debout"),
    ("hoos_p10", "Marche sur sol irrégulier"),
]
HOOS_SYMP = [
    ("hoos_s1", "Gonflement de la hanche"),
    ("hoos_s2", "Craquements ou bruits"),
    ("hoos_s3", "Raideur matinale"),
    ("hoos_s4", "Raideur après repos"),
    ("hoos_s5", "Amplitude des mouvements"),
]
HOOS_ADL = [
    ("hoos_a1",  "Descendre les escaliers"),
    ("hoos_a2",  "Monter les escaliers"),
    ("hoos_a3",  "Se relever en position assise"),
    ("hoos_a4",  "Rester debout"),
    ("hoos_a5",  "Se pencher vers le sol"),
    ("hoos_a6",  "Marche sur terrain plat"),
    ("hoos_a7",  "Entrer/sortir d'une voiture"),
    ("hoos_a8",  "Faire les courses"),
    ("hoos_a9",  "Chausser des chaussettes"),
    ("hoos_a10", "Se lever du lit"),
    ("hoos_a11", "Enlever des chaussettes"),
    ("hoos_a12", "Rester couché"),
    ("hoos_a13", "Entrer/sortir de la baignoire"),
    ("hoos_a14", "S'asseoir"),
    ("hoos_a15", "S'asseoir/se lever des toilettes"),
    ("hoos_a16", "Tâches ménagères lourdes"),
    ("hoos_a17", "Tâches ménagères légères"),
]
HOOS_SPORT = [
    ("hoos_sp1", "S'accroupir"),
    ("hoos_sp2", "Courir"),
    ("hoos_sp3", "Sauter"),
    ("hoos_sp4", "Pivoter"),
    ("hoos_sp5", "Activités physiques intenses"),
]
HOOS_QOL = [
    ("hoos_q1", "Conscience du problème de hanche"),
    ("hoos_q2", "Modification du mode de vie"),
    ("hoos_q3", "Manque de confiance"),
    ("hoos_q4", "Difficultés générales"),
]

OPTS = ["0 — Aucune", "1 — Légère", "2 — Modérée", "3 — Sévère", "4 — Extrême"]


def _hoos_sub_score(data, items):
    vals = []
    for k, _ in items:
        try:    vals.append(int(float(data.get(k, ""))))
        except: pass
    if not vals: return None
    return round(100 - (sum(vals) / len(vals)) * 25, 1)


@register_test
class HOOS(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "hoos", "nom": "HOOS — Hanche (score fonctionnel)",
            "tab_label": "🦴 HOOS",
            "categorie": "questionnaire",
            "tags": ["hanche", "fonctionnel", "arthrose", "post-chirurgical", "PTH"],
            "description": "Hip disability and Osteoarthritis Outcome Score — 5 sous-échelles /100",
        }

    @classmethod
    def fields(cls):
        all_items = HOOS_PAIN + HOOS_SYMP + HOOS_ADL + HOOS_SPORT + HOOS_QOL
        return [k for k, _ in all_items] + [
            "hoos_pain", "hoos_symptoms", "hoos_adl", "hoos_sport", "hoos_qol"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "sous_scores", "label": "Sous-scores (douleur, symptômes, AVQ, sport, QdV)", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
            {"key": "detail_items", "label": "Détail des items", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦴 HOOS — Score fonctionnel de la hanche</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Pour chaque question, indiquez le niveau de difficulté '
            'ressenti cette semaine. 0 = aucune difficulté, 4 = extrême. '
            'Le score est exprimé de 0 (extrême) à 100 (aucun problème).</div>',
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

        _render_section("Douleur (P)", HOOS_PAIN, "pain")
        _render_section("Symptômes (S)", HOOS_SYMP, "symp")
        _render_section("Activités quotidiennes (A)", HOOS_ADL, "adl")
        _render_section("Sport & Loisirs (SP)", HOOS_SPORT, "sport")
        _render_section("Qualité de vie (Q)", HOOS_QOL, "qol")

        for key_sub, items, field in [
            ("Pain", HOOS_PAIN, "hoos_pain"),
            ("Symptoms", HOOS_SYMP, "hoos_symptoms"),
            ("ADL", HOOS_ADL, "hoos_adl"),
            ("Sport", HOOS_SPORT, "hoos_sport"),
            ("QOL", HOOS_QOL, "hoos_qol"),
        ]:
            s = _hoos_sub_score(collected, items)
            collected[field] = s if s is not None else ""

        st.markdown("#### 📊 Résultats")
        cols = st.columns(5)
        labels_disp = ["Douleur", "Symptômes", "AVQ", "Sport", "QoL"]
        fields_disp = ["hoos_pain", "hoos_symptoms", "hoos_adl", "hoos_sport", "hoos_qol"]
        for col, lbl, field in zip(cols, labels_disp, fields_disp):
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
        for f in ["hoos_pain", "hoos_symptoms", "hoos_adl", "hoos_sport", "hoos_qol"]:
            try:    scores.append(float(data.get(f, "")))
            except: pass
        if not scores: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        avg = round(sum(scores) / len(scores), 1)
        color = "#388e3c" if avg >= 70 else "#f57c00" if avg >= 40 else "#d32f2f"
        return {"score": avg, "interpretation": f"Moy. {avg}/100", "color": color, "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        for f in ["hoos_pain", "hoos_adl"]:
            try:
                if float(bilan_data.get(f, "")) >= 0: return True
            except: pass
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        fields_colors = [("hoos_pain","Douleur","#2B57A7"),
                         ("hoos_adl","AVQ","#1D9E75"),
                         ("hoos_sport","Sport","#D85A30"),
                         ("hoos_qol","QoL","#7F77DD")]
        for field, lbl, color in fields_colors:
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
        fig.update_layout(yaxis=dict(range=[0, 105], title="HOOS /100"),
                          height=350, legend=dict(orientation="h", y=-0.2),
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('hoos', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "Douleur", "col_key": "hoos_pain",
             "values": [r.get("hoos_pain","—") for _,r in bilans_df.iterrows()]},
            {"label": "AVQ", "col_key": "hoos_adl",
             "values": [r.get("hoos_adl","—") for _,r in bilans_df.iterrows()]},
            {"label": "Sport", "col_key": "hoos_sport",
             "values": [r.get("hoos_sport","—") for _,r in bilans_df.iterrows()]},
            {"label": "QoL", "col_key": "hoos_qol",
             "values": [r.get("hoos_qol","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan": lbl, "Douleur": row.get("hoos_pain","—"),
                             "AVQ": row.get("hoos_adl","—"), "Sport": row.get("hoos_sport","—"),
                 "QoL": row.get("hoos_qol","—")}
                for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
