"""
ai_analyse.py — Analyse IA de l'évolution physiothérapeutique
Appel à l'API Anthropic pour générer une synthèse clinique en français.
"""
import json
import requests
import streamlit as st


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL             = "claude-haiku-4-5-20251001"  # Rapide et économique
MAX_TOKENS        = 1200


# ─── Prompts par module ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es un assistant physiothérapeute expert. Tu rédiges des synthèses 
d'évolution clinique en français, destinées à des médecins. 

Règles absolues :
- Tu ne poses AUCUN diagnostic médical
- Tu décris des évolutions fonctionnelles et des tendances cliniques
- Tu utilises un vocabulaire physiothérapeutique précis
- Tu mentionnes les seuils cliniques pertinents quand ils sont franchis
- Tu signales les points de vigilance ou plateaux d'évolution
- Tu restes factuel, sobre et professionnel
- La longueur cible est 200-300 mots
- Pas de titres ni de bullet points — texte courant structuré en 2-3 paragraphes"""


MODULE_CONTEXT = {
    "shv": "Syndrome d'Hyperventilation (SHV). Scores : HAD anxiété (/21, seuil pathologique >10), "
           "HAD dépression (/21, seuil >10), BOLT (secondes, normal >25s), Nijmegen (/64, seuil pathologique >23), "
           "SF-12 PCS et MCS (score composite physique/mental, moyenne population = 50), "
           "EtCO2 (mmHg, normal 35-45), pattern respiratoire, SNIF/PImax/PEmax (% valeur prédite).",

    "lombalgie": "Lombalgie. Scores : EVA repos/mouvement/nuit (/10), ODI Oswestry (/100, seuil clinique >20%), "
                 "Tampa (kinésiophobie, seuil >37), Örebro (risque chronification, seuil >50/210), "
                 "Luomajoki (contrôle moteur lombaire /6 erreurs), mobilité lombaire (Schober, flexion cm).",

    "equilibre": "Bilan d'équilibre et de marche. Scores : Tinetti total (/28, seuil risque élevé <19, modéré <24), "
                 "Berg Balance Scale (/56, risque élevé ≤20, modéré ≤40), TUG en secondes (normal <10s, "
                 "risque élevé ≥20s), STS 1 minute (répétitions), SPPB (/12), équilibre unipodal (secondes).",

    "bpco": "BPCO / pathologie respiratoire chronique. Scores : 6MWT distance (m, bon pronostic ≥400m, "
            "très limité <150m), CAT (/40, seuil faible ≤10, sévère >20), mMRC grade (0-4), "
            "VEMS % prédit, BODE index (/10, pronostic), STS 1 minute, SpO2 effort.",
}


def _format_bilans(bilans_df, module: str) -> str:
    """Formate les données des bilans pour le prompt."""
    import pandas as pd
    
    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan").reset_index(drop=True)
    
    lines = []
    for i, (_, row) in enumerate(bilans_df.iterrows()):
        d = row["date_bilan"]
        date_str = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        type_b   = row.get("type_bilan", "") or ""
        lines.append(f"\n--- Bilan {i+1} — {date_str} ({type_b}) ---")
        
        # Filtrer les colonnes pertinentes (non vides, non techniques)
        skip = {"bilan_id","patient_id","date_bilan","type_bilan","praticien",
                "notes_generales","date_creation"}
        for col in bilans_df.columns:
            if col in skip: continue
            val = row.get(col, "")
            if val is None or str(val).strip() in ("","0","0.0","None","nan"): continue
            # Exclure les items individuels (had_a1, sf12_q1...) — garder les scores
            if any(col.endswith(f"_{x}") for x in
                   list("abcdefghij123456789") + [str(i) for i in range(1,20)]):
                continue
            lines.append(f"  {col}: {val}")
    
    return "\n".join(lines)


def generate_analyse(bilans_df, patient_info: dict, module: str) -> str:
    """
    Génère une analyse IA de l'évolution.
    Retourne le texte généré ou un message d'erreur.
    """
    patient_name = f"{patient_info.get('nom','')} {patient_info.get('prenom','')}".strip()
    n_bilans = len(bilans_df)
    context  = MODULE_CONTEXT.get(module, "")
    data_str = _format_bilans(bilans_df, module)
    
    user_prompt = f"""Rédige une synthèse physiothérapeutique de l'évolution du patient {patient_name} 
sur {n_bilans} bilan(s).

Contexte clinique : {context}

Données des bilans :
{data_str}

Rédige une synthèse clinique structurée destinée au médecin traitant. 
Décris l'évolution fonctionnelle, les progrès ou stagnations observés, 
les seuils cliniques franchis, et les points de vigilance. 
N'émets aucun diagnostic médical."""

    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "⚠️ Clé API Anthropic manquante — ajoutez ANTHROPIC_API_KEY dans les secrets Streamlit."
        
        resp = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model":      MODEL,
                "max_tokens": MAX_TOKENS,
                "system":     SYSTEM_PROMPT,
                "messages":   [{"role": "user", "content": user_prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]
    except requests.exceptions.Timeout:
        return "⚠️ Délai dépassé — veuillez réessayer."
    except Exception as e:
        return f"⚠️ Erreur lors de la génération : {str(e)}"


def render_analyse_section(bilans_df, patient_info: dict, module: str,
                           patient_id: str):
    """
    Affiche le bloc analyse IA dans la page d'évolution.
    Gère la génération, l'édition et la sauvegarde.
    """
    from utils.db import load_analyse, save_analyse

    st.markdown("---")
    st.markdown("### 🤖 Synthèse physiothérapeutique (IA)")

    # Charger le texte existant
    session_key  = f"analyse_text_{module}_{patient_id}"
    stale_key    = f"analyse_stale_{module}_{patient_id}"
    is_stale     = st.session_state.get(stale_key, False)

    if session_key not in st.session_state:
        stored = load_analyse(patient_id, module)
        st.session_state[session_key] = stored

    analyse_text = st.session_state[session_key]

    col_gen, col_info = st.columns([2, 5])
    with col_gen:
        if is_stale:
            btn_label = "🔄 Regénérer (bilan modifié)"
        elif not analyse_text:
            btn_label = "🤖 Générer la synthèse"
        else:
            btn_label = "🔄 Regénérer"
        if st.button(btn_label, key=f"btn_gen_{module}", type="primary"):
            with st.spinner("Analyse en cours…"):
                new_text = generate_analyse(bilans_df, patient_info, module)
            st.session_state[session_key] = new_text
            save_analyse(patient_id, module, new_text)
            st.session_state.pop(stale_key, None)
            st.rerun()
    with col_info:
        if is_stale:
            st.warning("⚠️ Un bilan a été modifié — la synthèse doit être régénérée.")
        elif analyse_text:
            st.caption("✏️ Texte éditable — vos modifications sont sauvegardées automatiquement.")
        else:
            st.caption("Cliquez sur 'Générer' pour produire une synthèse basée sur les bilans sélectionnés.")

    if analyse_text:
        edited = st.text_area(
            "Synthèse",
            value=analyse_text,
            height=220,
            key=f"ta_{module}_{patient_id}",
            label_visibility="collapsed",
        )
        # Sauvegarder si modifié
        if edited != analyse_text:
            st.session_state[session_key] = edited
            save_analyse(patient_id, module, edited)
        
        st.caption(f"💡 Cette synthèse sera incluse dans le prochain export PDF. "
                   f"Elle sera automatiquement régénérée si un bilan est modifié ou ajouté.")
