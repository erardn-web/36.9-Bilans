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
        Ajoute une fiche imprimable vierge au story PDF questionnaires.
        Par défaut n'ajoute rien — override pour créer la fiche.
        """
        pass

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
