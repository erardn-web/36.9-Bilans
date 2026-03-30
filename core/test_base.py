"""
core/test_base.py — Classe de base pour tous les tests de la bibliothèque.

Chaque test hérite de BaseTest et implémente :
  - meta()             : métadonnées (id, nom, catégorie...)
  - fields()           : clés Google Sheets utilisées
  - render()           : widget Streamlit → dict {clé: valeur}
  - score()            : calcul du score → dict
  - render_evolution() : graphique/tableau Plotly
  - render_pdf()       : blocs ReportLab pour le rapport PDF
  - render_print_sheet(): fiche imprimable vierge
"""

from abc import ABC, abstractmethod


class BaseTest(ABC):
    """Interface commune à tous les tests de la bibliothèque."""

    # ── Métadonnées ───────────────────────────────────────────────────────────

    @classmethod
    @abstractmethod
    def meta(cls) -> dict:
        """
        Retourne les métadonnées du test.

        Format attendu :
        {
            "id":          "had",                          # identifiant unique snake_case
            "nom":         "HAD — Anxiété & Dépression",   # nom affiché
            "tab_label":   "😟 HAD",                       # label onglet Streamlit
            "categorie":   "questionnaire",                # questionnaire|test_clinique|mesure
            "description": "Hospital Anxiety and Depression Scale",
            "reference":   "Zigmond & Snaith, 1983",       # optionnel
        }
        """

    @classmethod
    @abstractmethod
    def fields(cls) -> list:
        """
        Liste des clés Google Sheets utilisées par ce test.
        Ces clés sont ajoutées dynamiquement aux headers de la feuille Bilans.

        Exemple : ["had_a1", ..., "had_score_anxiete", "had_score_depression"]
        """

    # ── Rendu Streamlit ───────────────────────────────────────────────────────

    @abstractmethod
    def render(self, lv, key_prefix: str) -> dict:
        """
        Affiche le widget Streamlit du test dans l'onglet bilan.

        Args:
            lv          : fonction lv(key, default="") pour charger les valeurs stockées
            key_prefix  : préfixe unique pour les clés Streamlit (ex: "bilan_abc123")

        Retourne : dict {clé_sheets: valeur} — toutes les valeurs à sauvegarder.
        """

    # ── Scoring ───────────────────────────────────────────────────────────────

    @classmethod
    def score(cls, data: dict) -> dict:
        """
        Calcule le(s) score(s) à partir des données du bilan.

        Retourne : {
            "score":          valeur numérique principale (ou None),
            "interpretation": texte court,
            "color":          code couleur hex,
            "details":        dict de scores secondaires (optionnel),
        }

        Par défaut retourne vide — override si le test a un score.
        """
        return {"score": None, "interpretation": "", "color": "#888888", "details": {}}

    # ── Indicateur de complétion (fond vert onglet) ───────────────────────────

    @classmethod
    def is_filled(cls, bilan_data: dict) -> bool:
        """
        Retourne True si ce test a au moins une valeur renseignée.
        Utilisé pour le highlight vert des onglets.
        Override si la logique de complétion est plus complexe.
        """
        for k in cls.fields():
            v = str(bilan_data.get(k, "")).strip()
            if v not in ("", "0", "0.0", "None", "nan"):
                return True
        return False

    # ── Évolution ─────────────────────────────────────────────────────────────

    @classmethod
    def render_evolution(cls, bilans_df, labels: list) -> None:
        """
        Affiche graphique + tableau d'évolution dans la vue Évolution.
        Par défaut : tableau simple. Override pour graphique personnalisé.
        """
        import streamlit as st
        import pandas as pd

        rows = []
        for lbl, (_, row) in zip(labels, bilans_df.iterrows()):
            r = {"Bilan": lbl}
            for f in cls.fields():
                v = row.get(f, "")
                if str(v).strip() not in ("", "None", "nan"):
                    r[f] = v
            if len(r) > 1:
                rows.append(r)

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info(f"Aucune donnée pour {cls.meta()['nom']}.")

    # ── PDF rapport ───────────────────────────────────────────────────────────

    @classmethod
    def render_pdf(cls, story: list, styles: dict, bilans_df, labels: list) -> None:
        """
        Ajoute les éléments ReportLab au story du PDF d'évolution.
        Par défaut n'ajoute rien — override pour personnaliser.
        """
        pass

    # ── Fiche imprimable vierge ───────────────────────────────────────────────

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        """
        Ajoute une fiche imprimable vierge au story PDF.
        Version générique : titre + description + champs avec lignes à remplir.
        Override dans le test pour une fiche sur mesure.
        """
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT

        m = cls.meta()
        nom = m.get("nom", cls.tab_label())
        desc = m.get("description", "")
        ref  = m.get("reference", "")
        fields = cls.fields()

        # Titre
        story.append(Paragraph(nom, styles["section"]))
        if desc:
            story.append(Paragraph(desc, styles["intro"]))
        if ref:
            story.append(Paragraph(f"Référence : {ref}", styles["small"]))
        story.append(Spacer(1, 0.4*cm))

        # Ligne patient / date
        from reportlab.platypus import Table as _T, TableStyle as _TS
        header_data = [["Patient : " + "_"*30, "Date : " + "_"*15, "Praticien : " + "_"*15]]
        header_tbl = _T(header_data, colWidths=[8*cm, 4.5*cm, 4.5*cm])
        header_tbl.setStyle(_TS([
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#555555")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(header_tbl)
        story.append(Spacer(1, 0.4*cm))

        # Champs — ligne de saisie par champ
        if fields:
            # Formater les noms de champs en labels lisibles
            def _label(f):
                # Supprimer le préfixe commun (test_id_)
                tid = m.get("id","")
                f = f.replace(tid + "_", "").replace("_", " ")
                return f.strip().capitalize()

            # Grouper par paires pour 2 colonnes
            pairs = [(fields[i], fields[i+1] if i+1 < len(fields) else None)
                     for i in range(0, len(fields), 2)]
            row_h = 0.9*cm
            line_color = colors.HexColor("#CCCCCC")
            col_w = 8.5*cm

            for f1, f2 in pairs:
                row = []
                for f in [f1, f2]:
                    if f:
                        lbl = _label(f)
                        row.append(f"{lbl} : {'_'*25}")
                    else:
                        row.append("")
                tbl = _T([row], colWidths=[col_w, col_w])
                tbl.setStyle(_TS([
                    ("FONTSIZE", (0,0), (-1,-1), 9),
                    ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#1A1A1A")),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                    ("TOPPADDING", (0,0), (-1,-1), 4),
                    ("LINEBELOW", (0,0), (-1,-1), 0.3, line_color),
                ]))
                story.append(tbl)

        # Zone notes
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Notes / Observations :", styles["normal"]))
        for _ in range(3):
            story.append(Spacer(1, 0.5*cm))
            tbl = _T([["_"*90]], colWidths=[17*cm])
            tbl.setStyle(_TS([
                ("FONTSIZE", (0,0), (-1,-1), 9),
                ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#CCCCCC")),
            ]))
            story.append(tbl)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @classmethod
    def test_id(cls) -> str:
        return cls.meta()["id"]

    @classmethod
    def test_nom(cls) -> str:
        return cls.meta()["nom"]

    @classmethod
    def tab_label(cls) -> str:
        return cls.meta().get("tab_label", cls.meta()["nom"])
