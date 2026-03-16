import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_NAME = "36.9_Bilans"


@st.cache_resource
def get_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


YOUR_EMAIL = "votre.email@gmail.com"  # ← Remplacez par votre adresse Gmail


def get_spreadsheet():
    client = get_client()
    try:
        return client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        ss = client.create(SPREADSHEET_NAME)
        # Partage automatique avec votre compte Google personnel
        ss.share(YOUR_EMAIL, perm_type="user", role="writer", notify=True)
        return ss


# ─── Headers ────────────────────────────────────────────────────────────────

PATIENTS_HEADERS = [
    "patient_id", "nom", "prenom", "date_naissance",
    "sexe", "profession", "date_creation",
]

def get_shv_headers():
    return [
        # Identification
        "bilan_id", "patient_id", "date_bilan", "type_bilan", "praticien", "notes_generales",
        # HAD – Anxiété
        "had_a1", "had_a2", "had_a3", "had_a4", "had_a5", "had_a6", "had_a7",
        # HAD – Dépression
        "had_d1", "had_d2", "had_d3", "had_d4", "had_d5", "had_d6", "had_d7",
        # HAD scores
        "had_score_anxiete", "had_score_depression",
        # SF-12 – items
        "sf12_q1", "sf12_q2a", "sf12_q2b",
        "sf12_q3a", "sf12_q3b", "sf12_q4a", "sf12_q4b",
        "sf12_q5", "sf12_q6a", "sf12_q6b", "sf12_q6c", "sf12_q7",
        # SF-12 scores
        "sf12_pf", "sf12_rp", "sf12_bp", "sf12_gh",
        "sf12_vt", "sf12_sf", "sf12_re", "sf12_mh",
        "sf12_pcs", "sf12_mcs",
        # BOLT
        "bolt_score", "bolt_interpretation",
        # Test d'hyperventilation volontaire
        "hvt_symptomes_reproduits", "hvt_symptomes_list",
        "hvt_duree_retour", "hvt_notes",
        # HVT – Grille de mesures (PetCO2, FR, SpO2, FC)
        # Repos : 0, 1, 2, 3 min
        "hvt_repos_0_petco2","hvt_repos_0_fr","hvt_repos_0_spo2","hvt_repos_0_fc",
        "hvt_repos_1_petco2","hvt_repos_1_fr","hvt_repos_1_spo2","hvt_repos_1_fc",
        "hvt_repos_2_petco2","hvt_repos_2_fr","hvt_repos_2_spo2","hvt_repos_2_fc",
        "hvt_repos_3_petco2","hvt_repos_3_fr","hvt_repos_3_spo2","hvt_repos_3_fc",
        # HV : 1, 2, 3 min
        "hvt_hv_1_petco2","hvt_hv_1_fr","hvt_hv_1_spo2","hvt_hv_1_fc",
        "hvt_hv_2_petco2","hvt_hv_2_fr","hvt_hv_2_spo2","hvt_hv_2_fc",
        "hvt_hv_3_petco2","hvt_hv_3_fr","hvt_hv_3_spo2","hvt_hv_3_fc",
        # Récupération : 1, 2, 3, 4, 5 min
        "hvt_rec_1_petco2","hvt_rec_1_fr","hvt_rec_1_spo2","hvt_rec_1_fc",
        "hvt_rec_2_petco2","hvt_rec_2_fr","hvt_rec_2_spo2","hvt_rec_2_fc",
        "hvt_rec_3_petco2","hvt_rec_3_fr","hvt_rec_3_spo2","hvt_rec_3_fc",
        "hvt_rec_4_petco2","hvt_rec_4_fr","hvt_rec_4_spo2","hvt_rec_4_fc",
        "hvt_rec_5_petco2","hvt_rec_5_fr","hvt_rec_5_spo2","hvt_rec_5_fc",
        # Nijmegen (16 items + score)
        "nij_1","nij_2","nij_3","nij_4","nij_5","nij_6","nij_7","nij_8",
        "nij_9","nij_10","nij_11","nij_12","nij_13","nij_14","nij_15","nij_16",
        "nij_score", "nij_interpretation",
        # Gazométrie
        "gazo_type", "gazo_ph", "gazo_paco2", "gazo_pao2",
        "gazo_hco3", "gazo_sato2", "gazo_fio2", "gazo_notes",
        # Capnographie
        "etco2_repos", "etco2_post_effort", "etco2_pattern", "etco2_notes",
        # Pattern respiratoire
        "pattern_frequence", "pattern_amplitude", "pattern_mode",
        "pattern_rythme", "pattern_paradoxal", "pattern_notes",
        # SNIF / PImax / PEmax
        "snif_val", "snif_pred", "snif_pct",
        "pimax_val", "pimax_pred", "pimax_pct",
        "pemax_val", "pemax_pred", "pemax_pct",
        "snif_pimax_pemax_notes",
        # MRC dyspnée
        "mrc_score",
        # Comorbidités
        "comorb_list", "comorb_traitements", "comorb_notes",
    ]


# ─── Sheet initialization ────────────────────────────────────────────────────

def _ws_to_df(ws, expected_headers: list) -> pd.DataFrame:
    """
    Lit une feuille avec get_all_values() (plus robuste que get_all_records).
    Aligne les colonnes sur expected_headers — ajoute les colonnes manquantes à vide.
    """
    all_values = ws.get_all_values()
    if not all_values or len(all_values) < 1:
        return pd.DataFrame(columns=expected_headers)

    sheet_headers = all_values[0]
    rows          = all_values[1:]

    if not rows:
        return pd.DataFrame(columns=expected_headers)

    # Construire un DataFrame avec les headers réels de la feuille
    df = pd.DataFrame(rows, columns=sheet_headers)

    # Ajouter les colonnes attendues qui manquent (nouveaux champs)
    for col in expected_headers:
        if col not in df.columns:
            df[col] = ""

    return df[expected_headers]


def _sync_headers(ws, expected_headers: list):
    """
    Ajoute les colonnes manquantes en une seule opération batch.
    """
    try:
        existing = ws.row_values(1)
        missing  = [h for h in expected_headers if h not in existing]
        if not missing:
            return
        new_headers = existing + missing
        # Resize si nécessaire
        if len(new_headers) > ws.col_count:
            ws.resize(cols=len(new_headers))
        # Écrire tous les headers en une seule requête
        ws.update([new_headers], "A1")
    except Exception:
        # Si la sync échoue, on continue sans bloquer l'app
        pass


def ensure_sheets():
    ss = get_spreadsheet()

    try:
        ws_p = ss.worksheet("Patients")
        _sync_headers(ws_p, PATIENTS_HEADERS)
    except gspread.WorksheetNotFound:
        ws_p = ss.add_worksheet("Patients", rows=1000, cols=len(PATIENTS_HEADERS))
        ws_p.append_row(PATIENTS_HEADERS)

    try:
        ws_b = ss.worksheet("Bilans_SHV")
        _sync_headers(ws_b, get_shv_headers())
    except gspread.WorksheetNotFound:
        ws_b = ss.add_worksheet("Bilans_SHV", rows=5000, cols=len(get_shv_headers()))
        ws_b.append_row(get_shv_headers())

    return ss


# ─── Patients ────────────────────────────────────────────────────────────────

def get_all_patients() -> pd.DataFrame:
    ss = ensure_sheets()
    ws = ss.worksheet("Patients")
    return _ws_to_df(ws, PATIENTS_HEADERS)


def create_patient(nom, prenom, date_naissance, sexe, profession) -> str:
    ss = ensure_sheets()
    ws = ss.worksheet("Patients")
    patient_id = str(uuid.uuid4())[:8].upper()
    date_creation = datetime.now().strftime("%Y-%m-%d %H:%M")
    ws.append_row([
        patient_id, nom.strip().upper(), prenom.strip().capitalize(),
        str(date_naissance), sexe, profession.strip(), date_creation,
    ])
    return patient_id


# ─── Bilans SHV ──────────────────────────────────────────────────────────────

def get_patient_bilans(patient_id: str) -> pd.DataFrame:
    ss = ensure_sheets()
    ws = ss.worksheet("Bilans_SHV")
    df = _ws_to_df(ws, get_shv_headers())
    if df.empty:
        return df
    result = df[df["patient_id"] == patient_id].copy()
    return result.reset_index(drop=True)


def save_bilan(bilan_data: dict) -> str:
    ss = ensure_sheets()
    ws = ss.worksheet("Bilans_SHV")
    headers = get_shv_headers()

    bilan_id = bilan_data.get("bilan_id")

    if bilan_id:
        # Mise à jour d'une ligne existante
        all_data = ws.get_all_records()
        for i, record in enumerate(all_data):
            if record.get("bilan_id") == bilan_id:
                row = [str(bilan_data.get(h, "")) for h in headers]
                ws.update(f"A{i + 2}", [row])
                return bilan_id

    # Nouveau bilan
    new_id = str(uuid.uuid4())[:8].upper()
    bilan_data["bilan_id"] = new_id
    row = [str(bilan_data.get(h, "")) for h in headers]
    ws.append_row(row)
    return new_id
