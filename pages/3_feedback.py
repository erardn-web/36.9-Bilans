import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
from utils.db import get_sheet, append_row, update_row

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(page_title="Feedback & Votes", page_icon="💬", layout="wide")

THERAPEUTES = [
    "— Sélectionner —",
    "Nathan",
    "Thérapeute 2",
    "Thérapeute 3",
    "Thérapeute 4",
    "Thérapeute 5",
    # ➕ Ajouter les noms ici
]

TYPES = {
    "🐛 Bug": "Bug",
    "🆕 Suggestion": "Suggestion",
    "🔧 Amélioration": "Amélioration",
    "📚 Bibliothèque": "Bibliothèque",
}

STATUTS_COULEUR = {
    "En vote":          "#F59E0B",
    "Accepté":          "#10B981",
    "En développement": "#3B82F6",
    "Livré":            "#6366F1",
    "Refusé":           "#EF4444",
    "En traitement":    "#F97316",
}

DELAI_VOTE = 10  # jours


# ─────────────────────────────────────────
# HELPERS GSHEETS
# ─────────────────────────────────────────

def load_feedback() -> pd.DataFrame:
    try:
        df = get_sheet("Feedback")
        if df.empty:
            return pd.DataFrame(columns=[
                "id", "date_creation", "auteur", "type", "titre",
                "description", "statut", "deadline_vote",
                "votes_pour", "votes_contre"
            ])
        df["votes_pour"]   = pd.to_numeric(df["votes_pour"],   errors="coerce").fillna(0).astype(int)
        df["votes_contre"] = pd.to_numeric(df["votes_contre"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Erreur chargement Feedback : {e}")
        return pd.DataFrame()


def load_votes() -> pd.DataFrame:
    try:
        df = get_sheet("Votes")
        if df.empty:
            return pd.DataFrame(columns=["feedback_id", "votant", "vote", "date"])
        return df
    except Exception as e:
        st.error(f"Erreur chargement Votes : {e}")
        return pd.DataFrame()


def soumettre_feedback(auteur, type_, titre, description):
    now = datetime.now()
    est_bug = (type_ == "Bug")
    statut   = "En traitement" if est_bug else "En vote"
    deadline = "" if est_bug else (now + timedelta(days=DELAI_VOTE)).strftime("%Y-%m-%d")
    row = {
        "id":            str(uuid.uuid4())[:8].upper(),
        "date_creation": now.strftime("%Y-%m-%d %H:%M"),
        "auteur":        auteur,
        "type":          type_,
        "titre":         titre,
        "description":   description,
        "statut":        statut,
        "deadline_vote": deadline,
        "votes_pour":    0,
        "votes_contre":  0,
    }
    append_row("Feedback", row)
    return row["id"]


def enregistrer_vote(feedback_id, votant, vote, df_feedback, df_votes):
    """vote = 'pour' ou 'contre'"""
    idx = df_feedback.index[df_feedback["id"] == feedback_id].tolist()
    if not idx:
        return False, "Proposition introuvable."

    i = idx[0]
    col = "votes_pour" if vote == "pour" else "votes_contre"
    nouveau = int(df_feedback.at[i, col]) + 1
    df_feedback.at[i, col] = nouveau

    update_row("Feedback", feedback_id, {col: nouveau})

    append_row("Votes", {
        "feedback_id": feedback_id,
        "votant":      votant,
        "vote":        vote,
        "date":        datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    return True, "Vote enregistré ✅"


def a_deja_vote(feedback_id, votant, df_votes) -> bool:
    if df_votes.empty:
        return False
    mask = (df_votes["feedback_id"] == feedback_id) & (df_votes["votant"] == votant)
    return mask.any()


def badge_statut(statut):
    couleur = STATUTS_COULEUR.get(statut, "#9CA3AF")
    return f'<span style="background:{couleur};color:white;padding:2px 10px;border-radius:12px;font-size:0.8em;font-weight:600">{statut}</span>'


def badge_type(type_):
    icons = {"Bug": "🐛", "Suggestion": "🆕", "Amélioration": "🔧", "Bibliothèque": "📚"}
    return f'{icons.get(type_,"💬")} {type_}'


# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "fb_nom" not in st.session_state:
    st.session_state.fb_nom = ""


# ─────────────────────────────────────────
# UI
# ─────────────────────────────────────────
st.title("💬 Feedback & Communauté")
st.caption("Remonte un bug, propose une amélioration, vote sur les idées de tes collègues.")

df_fb    = load_feedback()
df_votes = load_votes()

# ── BANDEAU NOM ──────────────────────────────────────────────
with st.container():
    col_nom, col_info = st.columns([2, 4])
    with col_nom:
        nom = st.selectbox(
            "👤 Qui es-tu ?",
            THERAPEUTES,
            index=THERAPEUTES.index(st.session_state.fb_nom) if st.session_state.fb_nom in THERAPEUTES else 0,
            key="select_nom"
        )
        if nom != "— Sélectionner —":
            st.session_state.fb_nom = nom
    with col_info:
        if st.session_state.fb_nom and st.session_state.fb_nom != "— Sélectionner —":
            st.success(f"Connecté en tant que **{st.session_state.fb_nom}**")
        else:
            st.info("Sélectionne ton nom pour voter ou soumettre une proposition.")

nom_ok = st.session_state.fb_nom and st.session_state.fb_nom != "— Sélectionner —"

st.divider()

# ── ONGLETS ──────────────────────────────────────────────────
tab_vote, tab_nouveau, tab_roadmap, tab_bugs = st.tabs([
    "🗳️ Voter",
    "✏️ Proposer",
    "🗺️ Roadmap",
    "🐛 Bugs",
])


# ════════════════════════════════════════════
# ONGLET VOTER
# ════════════════════════════════════════════
with tab_vote:
    st.subheader("Propositions en cours de vote")

    actives = df_fb[df_fb["statut"] == "En vote"].copy() if not df_fb.empty else pd.DataFrame()

    if actives.empty:
        st.info("Aucune proposition en cours de vote pour l'instant.")
    else:
        actives = actives.sort_values("deadline_vote")

        for _, row in actives.iterrows():
            with st.expander(
                f"{badge_type(row['type'])}  —  **{row['titre']}**  ·  par {row['auteur']}",
                expanded=False
            ):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**Description :** {row['description']}")
                    st.caption(f"Soumis le {row['date_creation']}  ·  Vote jusqu'au {row['deadline_vote']}")

                    total = int(row["votes_pour"]) + int(row["votes_contre"])
                    pct   = int(row["votes_pour"]) / total * 100 if total > 0 else 0
                    st.markdown(
                        f"**Votes : ✅ {int(row['votes_pour'])}  ·  ❌ {int(row['votes_contre'])}**"
                        + (f"  — {pct:.0f}% pour" if total > 0 else "  — Aucun vote encore")
                    )
                    if total > 0:
                        st.progress(pct / 100)

                with c2:
                    if not nom_ok:
                        st.warning("Sélectionne ton nom pour voter.")
                    elif a_deja_vote(row["id"], st.session_state.fb_nom, df_votes):
                        st.success("✔ Tu as déjà voté")
                    else:
                        st.markdown("**Ton vote :**")
                        col_p, col_c = st.columns(2)
                        with col_p:
                            if st.button("✅ Pour", key=f"pour_{row['id']}", use_container_width=True):
                                ok, msg = enregistrer_vote(
                                    row["id"], st.session_state.fb_nom,
                                    "pour", df_fb, df_votes
                                )
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        with col_c:
                            if st.button("❌ Contre", key=f"contre_{row['id']}", use_container_width=True):
                                ok, msg = enregistrer_vote(
                                    row["id"], st.session_state.fb_nom,
                                    "contre", df_fb, df_votes
                                )
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)


# ════════════════════════════════════════════
# ONGLET PROPOSER
# ════════════════════════════════════════════
with tab_nouveau:
    st.subheader("Soumettre une proposition ou un bug")

    if not nom_ok:
        st.warning("Sélectionne ton nom en haut de page avant de soumettre.")
    else:
        with st.form("form_feedback", clear_on_submit=True):
            type_label = st.selectbox("Type", list(TYPES.keys()))
            titre      = st.text_input("Titre court *", max_chars=80)
            description = st.text_area(
                "Description détaillée *",
                placeholder="Décris le problème ou l'idée avec le plus de détails possible...",
                height=150
            )

            if type_label == "🐛 Bug":
                st.info("🐛 Les bugs sont traités directement sans vote — tu recevras un retour rapide.")
            else:
                st.info(f"🗳️ Ta proposition sera soumise au vote de l'équipe pendant {DELAI_VOTE} jours.")

            submitted = st.form_submit_button("Envoyer ✉️", use_container_width=True, type="primary")

            if submitted:
                if not titre.strip() or not description.strip():
                    st.error("Titre et description sont obligatoires.")
                else:
                    type_val = TYPES[type_label]
                    fid = soumettre_feedback(
                        st.session_state.fb_nom, type_val,
                        titre.strip(), description.strip()
                    )
                    if type_val == "Bug":
                        st.success(f"🐛 Bug #{fid} enregistré — Nathan va s'en occuper !")
                    else:
                        st.success(f"✅ Proposition #{fid} soumise au vote pendant {DELAI_VOTE} jours !")
                    st.rerun()


# ════════════════════════════════════════════
# ONGLET ROADMAP
# ════════════════════════════════════════════
with tab_roadmap:
    st.subheader("Roadmap")

    statuts_roadmap = ["Accepté", "En développement", "Livré"]
    labels = {
        "Accepté":          "✅ Accepté — à programmer",
        "En développement": "🔨 En développement",
        "Livré":            "🚀 Livré",
    }

    if df_fb.empty:
        st.info("La roadmap est vide pour l'instant.")
    else:
        for statut in statuts_roadmap:
            subset = df_fb[df_fb["statut"] == statut]
            if subset.empty:
                continue
            st.markdown(f"### {labels[statut]}")
            for _, row in subset.iterrows():
                couleur = STATUTS_COULEUR[statut]
                st.markdown(
                    f'<div style="border-left:4px solid {couleur};padding:8px 12px;margin-bottom:8px;background:#f8f9fa;border-radius:4px">'
                    f'<strong>{badge_type(row["type"])}</strong> — {row["titre"]}<br>'
                    f'<small style="color:#6B7280">Proposé par {row["auteur"]} · {row["date_creation"]}'
                    f' · ✅ {int(row["votes_pour"])} / ❌ {int(row["votes_contre"])}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.markdown("")


# ════════════════════════════════════════════
# ONGLET BUGS
# ════════════════════════════════════════════
with tab_bugs:
    st.subheader("Suivi des bugs")

    if df_fb.empty:
        st.info("Aucun bug enregistré.")
    else:
        bugs = df_fb[df_fb["type"] == "Bug"].sort_values("date_creation", ascending=False)

        if bugs.empty:
            st.success("Aucun bug enregistré 🎉")
        else:
            for _, row in bugs.iterrows():
                couleur = STATUTS_COULEUR.get(row["statut"], "#9CA3AF")
                with st.expander(
                    f"#{row['id']}  —  {row['titre']}  ·  {row['auteur']}",
                    expanded=(row["statut"] == "En traitement")
                ):
                    st.markdown(f"**Description :** {row['description']}")
                    col_s, col_d = st.columns(2)
                    with col_s:
                        st.markdown(
                            f'Statut : {badge_statut(row["statut"])}',
                            unsafe_allow_html=True
                        )
                    with col_d:
                        st.caption(f"Soumis le {row['date_creation']}")
