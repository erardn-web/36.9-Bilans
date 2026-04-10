"""pages/1_Patients.py — Vue patients & mes cas"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Patients — 36.9 Bilans", page_icon="👥", layout="wide")

from utils.db import (
    get_all_patients, search_patients, get_patient_cas,
    get_cas_bilans_meta, set_patient_actif, update_patient,
)

S = st.session_state

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""<style>
.patient-row{display:flex;align-items:center;gap:12px;padding:10px 14px;
    border:0.5px solid var(--color-border-tertiary);border-radius:10px;
    margin-bottom:6px;background:var(--color-background-primary)}
.patient-row:hover{border-color:var(--color-border-secondary)}
.patient-nom{font-size:14px;font-weight:600}
.patient-info{font-size:12px;color:var(--color-text-secondary)}
.cas-badge{display:inline-block;padding:2px 8px;border-radius:10px;
    font-size:11px;font-weight:600;margin-right:4px}
.inactive{opacity:0.45}
</style>""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_cabinet, tab_moi = st.tabs(["🏥 Vue cabinet", "👤 Mes cas"])


# ═══════════════════════════════════════════════════════════════════════════════
# VUE CABINET — tous les patients
# ═══════════════════════════════════════════════════════════════════════════════
with tab_cabinet:
    st.markdown("### 👥 Patients du cabinet")

    # ── Sidebar search & filters ──────────────────────────────────────────────
    col_s, col_f1 = st.columns([4, 1])
    search_q    = col_s.text_input("🔍 Rechercher", placeholder="Nom, prénom…", key="pt_search")
    show_inact  = col_f1.checkbox("Inactifs", value=False, key="pt_inact")

    # ── Charger patients ──────────────────────────────────────────────────────
    @st.cache_data(ttl=30)
    def _load_patients_all():
        """Charge tous les patients y compris les inactifs."""
        try:
            from utils.db import get_sheet
            df = get_sheet("Patients")
            if df.empty: return pd.DataFrame()
            if "actif" not in df.columns: df["actif"] = "1"
            return df
        except Exception:
            return pd.DataFrame()

    df_all = _load_patients_all()

    if df_all.empty:
        st.info("Aucun patient enregistré.")
        st.stop()

    # Filtres
    if not show_inact:
        df_view = df_all[df_all.get("actif", pd.Series(["1"]*len(df_all))) != "0"]
    else:
        df_view = df_all.copy()


    if search_q.strip():
        mask = df_view.apply(lambda r: search_q.lower() in
            f"{r.get('nom','')} {r.get('prenom','')}".lower(), axis=1)
        df_view = df_view[mask]

    df_view = df_view.sort_values(["nom","prenom"]).reset_index(drop=True)

    # Compteurs
    c1, c2, c3 = st.columns(3)
    c1.metric("Total patients", len(df_all[df_all.get("actif","1") != "0"]))
    c2.metric("Affichés", len(df_view))
    c3.metric("Inactifs", len(df_all[df_all.get("actif","1") == "0"]))
    st.markdown("---")

    # ── Sélection patient ─────────────────────────────────────────────────────
    if "pt_selected" not in S: S["pt_selected"] = None

    # ── Vue détail patient ────────────────────────────────────────────────────
    if S.get("pt_selected"):
        pid = S["pt_selected"]
        row = df_all[df_all["patient_id"] == pid]
        if row.empty:
            S["pt_selected"] = None
            st.rerun()
        row = row.iloc[0]
        is_actif = str(row.get("actif","1")) != "0"

        col_back, _ = st.columns([1,5])
        if col_back.button("⬅️ Retour à la liste"):
            S["pt_selected"] = None
            st.rerun()

        # En-tête patient
        actif_badge = "" if is_actif else ' <span class="cas-badge" style="background:#f5f5f5;color:#999">Inactif</span>'
        st.markdown(
            f"## 👤 {row.get('nom','')} {row.get('prenom','')} {actif_badge}",
            unsafe_allow_html=True)
        st.caption(
            f"Né(e) le {row.get('date_naissance','—')} · "
            f"{row.get('sexe','—')} · "
            f"Patient depuis {str(row.get('date_creation',''))[:10]}")
        st.markdown("---")

        col_cas, col_edit = st.columns([3, 2])

        # ── Cas du patient ────────────────────────────────────────────────────
        with col_cas:
            st.markdown("#### 📁 Historique des cas")
            try:
                df_cas = get_patient_cas(pid)
                if df_cas.empty:
                    st.info("Aucun cas pour ce patient.")
                else:
                    import json
                    for _, cas in df_cas.sort_values("date_ouverture", ascending=False).iterrows():
                        try:
                            snap = json.loads(cas.get("template_snapshot","{}") or "{}")
                            tmpl_nom = snap.get("nom", cas.get("template_id","—"))
                        except Exception:
                            tmpl_nom = cas.get("template_id","—")

                        statut = cas.get("statut","ouvert")
                        s_color = "#388e3c" if statut=="ouvert" else "#999"
                        s_label = "🟢 Ouvert" if statut=="ouvert" else "⚫ Clôturé"

                        # Bilans du cas
                        try:
                            df_b = get_cas_bilans_meta(cas["cas_id"])
                            n_bilans = len(df_b)
                        except Exception:
                            n_bilans = 0

                        with st.expander(
                            f"{tmpl_nom} · {s_label} · {n_bilans} bilan(s) · "
                            f"{str(cas.get('date_ouverture',''))[:10]}",
                            expanded=False):
                            st.caption(f"Praticien : {cas.get('praticien_creation','—')} · "
                                       f"Ouvert le {str(cas.get('date_ouverture',''))[:10]}")
                            if cas.get("date_cloture","").strip():
                                st.caption(f"Clôturé le {str(cas['date_cloture'])[:10]}")
                            if cas.get("notes_cas","").strip():
                                st.info(cas["notes_cas"])
            except Exception as e:
                st.warning(f"Impossible de charger les cas : {e}")

        # ── Actions sur le patient ────────────────────────────────────────────
        with col_edit:
            st.markdown("#### ⚙️ Actions")

            # Modifier les infos
            with st.expander("✏️ Modifier les informations", expanded=False):
                with st.form(f"edit_patient_{pid}"):
                    new_nom   = st.text_input("Nom",    value=row.get("nom",""))
                    new_prenom= st.text_input("Prénom", value=row.get("prenom",""))
                    new_dn    = st.text_input("Date naissance (YYYY-MM-DD)", value=row.get("date_naissance",""))
                    new_sexe  = st.selectbox("Sexe", ["M","F"],
                        index=0 if row.get("sexe","M")=="M" else 1)
                    if st.form_submit_button("💾 Enregistrer", type="primary"):
                        if update_patient(pid, new_nom, new_prenom, new_dn, new_sexe):
                            st.success("✅ Mis à jour.")
                            _load_patients_all.clear()
                            st.rerun()
                        else:
                            st.error("❌ Erreur.")

            st.markdown("---")

            # Désactiver / réactiver
            if is_actif:
                st.warning("⚠️ Désactiver un patient le masque dans toutes les vues. Ses données sont conservées.")
                if st.button("🚫 Désactiver ce patient", use_container_width=True):
                    if set_patient_actif(pid, False):
                        st.success("Patient désactivé.")
                        _load_patients_all.clear()
                        st.rerun()
                    else:
                        st.error("❌ Erreur.")
            else:
                st.info("Ce patient est inactif.")
                if st.button("✅ Réactiver ce patient", type="primary", use_container_width=True):
                    if set_patient_actif(pid, True):
                        st.success("Patient réactivé.")
                        _load_patients_all.clear()
                        st.rerun()
                    else:
                        st.error("❌ Erreur.")

            st.markdown("---")
            # Aller dans les bilans
            if st.button("📋 Ouvrir dans Bilans", type="primary", use_container_width=True):
                S["patient_id"]   = pid
                S["patient_info"] = row.to_dict()
                S["mode"]         = "dossier"
                st.switch_page("pages/2_Bilans.py")

    else:
        # ── Liste des patients ────────────────────────────────────────────────
        if df_view.empty:
            st.info("Aucun patient ne correspond aux filtres.")
        else:
            # Affichage par lettres
            current_letter = None
            for _, row in df_view.iterrows():
                pid    = row.get("patient_id","")
                nom    = row.get("nom","—")
                prenom = row.get("prenom","")
                dn     = str(row.get("date_naissance",""))[:10]
                sexe   = row.get("sexe","")
                actif  = str(row.get("actif","1")) != "0"
                letter = nom[0].upper() if nom else "?"

                if letter != current_letter:
                    current_letter = letter
                    st.markdown(
                        f'<div style="font-size:11px;font-weight:700;color:#2B57A7;'
                        f'text-transform:uppercase;letter-spacing:.1em;'
                        f'margin:12px 0 4px;padding-bottom:2px;'
                        f'border-bottom:1px solid var(--color-border-tertiary)">{letter}</div>',
                        unsafe_allow_html=True)

                inactive_cls = "" if actif else "inactive"
                ca, cb, cc = st.columns([5, 1.5, 1])
                ca.markdown(
                    f'<div class="patient-row {inactive_cls}">'
                    f'<div><div class="patient-nom">{nom} {prenom}</div>'
                    f'<div class="patient-info">Né(e) {dn} · {sexe}'
                    f'{" · <em>Inactif</em>" if not actif else ""}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True)
                if cb.button("📋 Bilans", key=f"go_bilans_{pid}", use_container_width=True):
                    S["patient_id"]   = pid
                    S["patient_info"] = row.to_dict()
                    S["mode"]         = "dossier"
                    st.switch_page("pages/2_Bilans.py")
                if cc.button("👁️", key=f"see_{pid}", use_container_width=True,
                             help="Voir la fiche patient"):
                    S["pt_selected"] = pid
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# VUE MES CAS — filtrés par thérapeute
# ═══════════════════════════════════════════════════════════════════════════════
with tab_moi:
    thera = st.session_state.get("therapeute","").strip()

    if not thera:
        st.warning("⚠️ Renseignez votre nom dans la sidebar de la page d'accueil.")
        st.stop()

    st.markdown(f"### 👤 Cas de **{thera}**")

    @st.cache_data(ttl=30)
    def _load_mes_cas(praticien):
        try:
            from utils.db import get_sheet
            df_cas = get_sheet("Cas")
            df_pat = get_sheet("Patients")
            if df_cas.empty: return pd.DataFrame()
            mes = df_cas[df_cas["praticien_creation"].str.strip() == praticien.strip()]
            if mes.empty: return pd.DataFrame()
            merged = mes.merge(
                df_pat[["patient_id","nom","prenom"]],
                on="patient_id", how="left")
            return merged.sort_values("date_ouverture", ascending=False).reset_index(drop=True)
        except Exception:
            return pd.DataFrame()

    filt_statut = st.radio("Statut", ["Ouverts","Clôturés","Tous"],
        horizontal=True, key="moi_statut")

    df_mes = _load_mes_cas(thera)

    if df_mes.empty:
        st.info(f"Aucun cas trouvé pour {thera}.")
    else:
        if filt_statut == "Ouverts":
            df_mes = df_mes[df_mes["statut"]=="ouvert"]
        elif filt_statut == "Clôturés":
            df_mes = df_mes[df_mes["statut"]=="clos"]

        st.caption(f"{len(df_mes)} cas")

        import json as _j
        for _, cas in df_mes.iterrows():
            try:
                snap = _j.loads(cas.get("template_snapshot","{}") or "{}")
                tmpl_nom = snap.get("nom", cas.get("template_id","—"))
            except Exception:
                tmpl_nom = cas.get("template_id","—")

            nom_pat = f"{cas.get('nom','')} {cas.get('prenom','')}".strip() or "—"
            statut  = cas.get("statut","ouvert")
            s_ico   = "🟢" if statut=="ouvert" else "⚫"
            date_o  = str(cas.get("date_ouverture",""))[:10]

            col_i, col_b = st.columns([5, 1.5])
            col_i.markdown(
                f"**{s_ico} {nom_pat}** — {tmpl_nom} "
                f"<span style='color:var(--color-text-secondary);font-size:12px'>· {date_o}</span>",
                unsafe_allow_html=True)
            if statut == "ouvert":
                pid = cas.get("patient_id","")
                pat_row = df_all[df_all["patient_id"]==pid] if not df_all.empty else pd.DataFrame()
                if col_b.button("📋 Ouvrir", key=f"moi_{cas['cas_id']}", use_container_width=True):
                    if not pat_row.empty:
                        S["patient_id"]   = pid
                        S["patient_info"] = pat_row.iloc[0].to_dict()
                    S["cas_id"]   = cas["cas_id"]
                    S["cas_info"] = cas.to_dict()
                    S["mode"]     = "cas"
                    st.switch_page("pages/2_Bilans.py")
            else:
                col_b.markdown("")
