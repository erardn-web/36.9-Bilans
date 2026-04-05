import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import uuid
from utils.db import get_sheet, append_row, update_row

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(page_title="Feedback & Votes", page_icon="??", layout="wide")

THERAPEUTES = [
    "— Sélectionner —",
    "Nathan",
    "Alexandre",
    "Mavi",
    "Alexia",
    "Gino",
    "Odile",
    "Sarah",
    "Delphine",
    "Mehdi",
    "Ylana",
    "Célia",
    "Mélissa",
    "Thais",
]

TYPES = {
    "?? Bug": "Bug",
    "?? Suggestion": "Suggestion",
    "?? Amélioration": "Amélioration",
    "?? Bibliothèque": "Bibliothèque",
}

STATUTS_COULEUR = {
    "En vote":          "#F59E0B",
    "Accepté":          "#10B981",
    "En développement": "#3B82F6",
    "Livré":            "#6366F1",
    "Refusé":           "#EF4444",
    "En traitement":    "#F97316",
}

TOUS_STATUTS = list(STATUTS_COULEUR.keys())
DELAI_VOTE   = 10  # jours


# ─────────────────────────────────────────
# HELPERS GSHEETS
# ─────────────────────────────────────────

def load_feedback() -> pd.DataFrame:
    try:
        df = get_sheet("Feedback")
        if df.empty:
            return pd.DataFrame(columns=[
                "id","date_creation","auteur","type","titre",
                "description","statut","deadline_vote",
                "votes_pour","votes_contre","reponse_admin",
            ])
        df["votes_pour"]   = pd.to_numeric(df["votes_pour"],   errors="coerce").fillna(0).astype(int)
        df["votes_contre"] = pd.to_numeric(df["votes_contre"], errors="coerce").fillna(0).astype(int)
        if "reponse_admin" not in df.columns:
            df["reponse_admin"] = ""
        return df
    except Exception as e:
        st.error(f"Erreur chargement Feedback : {e}")
        return pd.DataFrame()


def load_votes() -> pd.DataFrame:
    try:
        df = get_sheet("Votes")
        if df.empty:
            return pd.DataFrame(columns=["feedback_id","votant","vote","date"])
        return df
    except Exception as e:
        st.error(f"Erreur chargement Votes : {e}")
        return pd.DataFrame()


def soumettre_feedback(auteur, type_, titre, description):
    now      = datetime.now()
    est_bug  = (type_ == "Bug")
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
        "reponse_admin": "",
    }
    append_row("Feedback", row)
    return row["id"]


def enregistrer_vote(feedback_id, votant, vote, df_feedback, df_votes):
    idx = df_feedback.index[df_feedback["id"] == feedback_id].tolist()
    if not idx:
        return False, "Proposition introuvable."
    i   = idx[0]
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
    return ((df_votes["feedback_id"] == feedback_id) & (df_votes["votant"] == votant)).any()


def badge_statut(statut):
    couleur = STATUTS_COULEUR.get(statut, "#9CA3AF")
    return f'<span style="background:{couleur};color:white;padding:2px 10px;border-radius:12px;font-size:0.8em;font-weight:600">{statut}</span>'


def badge_type(type_):
    icons = {"Bug": "??", "Suggestion": "??", "Amélioration": "??", "Bibliothèque": "??"}
    return f'{icons.get(type_,"??")} {type_}'





# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
for key, default in [("fb_nom", "")]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────
# UI
# ─────────────────────────────────────────
st.title("?? Feedback & Communauté")
st.caption("Remonte un bug, propose une amélioration, vote sur les idées de tes collègues.")

df_fb    = load_feedback()
df_votes = load_votes()

# ── BANDEAU NOM ──────────────────────────────────────────────
with st.container():
    col_nom, col_info = st.columns([2, 4])
    with col_nom:
        nom = st.selectbox(
            "?? Qui es-tu ?",
            THERAPEUTES,
            index=THERAPEUTES.index(st.session_state.fb_nom)
                  if st.session_state.fb_nom in THERAPEUTES else 0,
            key="select_nom",
        )
        if nom != "— Sélectionner —":
            st.session_state.fb_nom = nom

    with col_info:
        if st.session_state.fb_nom and st.session_state.fb_nom != "— Sélectionner —":
            st.success(f"Connecté en tant que **{st.session_state.fb_nom}**")
        else:
            st.info("Sélectionne ton nom pour participer.")


# ─────────────────────────────────────────
# ONGLETS
# ─────────────────────────────────────────
tab_nouveau, tab_votes, tab_roadmap, tab_bugs = st.tabs([
    "✉️ Nouveau feedback",
    "🗳️ Votes",
    "🗺️ Roadmap",
    "🐛 Bugs",
])


# ════════════════════════════════════════════
# ONGLET NOUVEAU FEEDBACK
# ════════════════════════════════════════════
with tab_nouveau:
    st.subheader("✉️ Soumettre un feedback")
    nom_actif = st.session_state.get("fb_nom","")
    if not nom_actif or nom_actif == "— Sélectionner —":
        st.warning("Sélectionne ton nom dans le bandeau ci-dessus pour continuer.")
        st.stop()

    with st.form("form_nouveau_feedback", clear_on_submit=True):
        type_label = st.selectbox("Type", list(TYPES.keys()), key="fb_type")
        titre      = st.text_input("Titre *", placeholder="Résumé en une phrase", key="fb_titre")
        description = st.text_area("Description *", height=120,
            placeholder="Décris le problème ou la fonctionnalité souhaitée…", key="fb_desc")
        est_bug = TYPES[type_label] == "Bug"
        if est_bug:
            st.info("🐛 Les bugs sont traités directement sans vote — tu recevras un retour rapide.")
        else:
            st.info(f"🗳️ Ta proposition sera soumise au vote de l'équipe pendant {DELAI_VOTE} jours.")
        submitted = st.form_submit_button("Envoyer ✉️", use_container_width=True, type="primary")
        if submitted:
            if not titre.strip() or not description.strip():
                st.error("Titre et description sont obligatoires.")
            else:
                type_val = TYPES[type_label]
                fid = soumettre_feedback(nom_actif, type_val, titre.strip(), description.strip())
                if type_val == "Bug":
                    st.success(f"🐛 Bug #{fid} enregistré — il sera traité rapidement !")
                else:
                    st.success(f"✅ Proposition #{fid} soumise au vote pendant {DELAI_VOTE} jours !")
                st.rerun()


# ════════════════════════════════════════════
# ONGLET VOTES
# ════════════════════════════════════════════
with tab_votes:
    st.subheader("🗳️ Propositions en cours de vote")
    nom_actif = st.session_state.get("fb_nom","")
    if df_fb.empty:
        st.info("Aucune proposition en cours.")
    else:
        en_vote = df_fb[df_fb["statut"] == "En vote"].sort_values("votes_pour", ascending=False)
        if en_vote.empty:
            st.info("Aucune proposition en cours de vote.")
        else:
            for _, row in en_vote.iterrows():
                fid = row["id"]
                has_voted = a_deja_vote(fid, nom_actif, df_votes) if nom_actif and nom_actif != "— Sélectionner —" else False
                couleur = STATUTS_COULEUR.get(row["statut"],"#9CA3AF")
                with st.expander(
                    f'#{fid} — {badge_type(row["type"])} — {row["titre"]}  '
                    f'· ✅ {int(row["votes_pour"])} / ❌ {int(row["votes_contre"])}',
                    expanded=False,
                ):
                    st.markdown(f'**Auteur :** {row["auteur"]} · **Soumis le :** {row["date_creation"]}')
                    st.markdown(f'**Description :** {row["description"]}')
                    if str(row.get("deadline_vote","")).strip():
                        st.caption("Vote jusqu'au " + str(row["deadline_vote"]))
                    if row.get("reponse_admin","").strip():
                        st.info(f'💬 {row["reponse_admin"]}')
                    if has_voted:
                        st.success("✅ Tu as déjà voté pour cette proposition.")
                    elif not nom_actif or nom_actif == "— Sélectionner —":
                        st.warning("Sélectionne ton nom pour voter.")
                    else:
                        cv1, cv2 = st.columns(2)
                        if cv1.button("✅ Pour", key=f"pour_{fid}", use_container_width=True):
                            ok, msg = enregistrer_vote(fid, nom_actif, "pour", df_fb, df_votes)
                            st.success(msg) if ok else st.error(msg)
                            st.rerun()
                        if cv2.button("❌ Contre", key=f"contre_{fid}", use_container_width=True):
                            ok, msg = enregistrer_vote(fid, nom_actif, "contre", df_fb, df_votes)
                            st.success(msg) if ok else st.error(msg)
                            st.rerun()


# ════════════════════════════════════════════
# ONGLET ROADMAP
# ════════════════════════════════════════════
with tab_roadmap:
    st.subheader("Roadmap")
    statuts_roadmap = ["Accepté", "En développement", "Livré"]
    labels = {
        "Accepté":          "✅ Accepté — à programmer",
        "En développement": "?? En développement",
        "Livré":            "?? Livré",
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
                    + (f'<br><em style="color:#374151">?? {row["reponse_admin"]}</em>'
                       if row.get("reponse_admin","").strip() else "")
                    + '</div>',
                    unsafe_allow_html=True,
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
            st.success("Aucun bug enregistré ??")
        else:
            for _, row in bugs.iterrows():
                with st.expander(
                    f"#{row['id']}  —  {row['titre']}  ·  {row['auteur']}",
                    expanded=(row["statut"] == "En traitement"),
                ):
                    st.markdown(f"**Description :** {row['description']}")
                    if row.get("reponse_admin","").strip():
                        st.info(f"?? **Nathan :** {row['reponse_admin']}")
                    col_s, col_d = st.columns(2)
                    with col_s:
                        st.markdown(f'Statut : {badge_statut(row["statut"])}', unsafe_allow_html=True)
                    with col_d:
                        st.caption(f"Soumis le {row['date_creation']}")
