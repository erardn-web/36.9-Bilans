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
SPREADSHEET_NAME = "Physio_App"


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
        # HAD – Anxiété (items impairs du questionnaire)
        "had_a1", "had_a2", "had_a3", "had_a4", "had_a5", "had_a6", "had_a7",
        # HAD – Dépression (items pairs)
        "had_d1", "had_d2", "had_d3", "had_d4", "had_d5", "had_d6", "had_d7",
        # HAD scores
        "had_score_anxiete", "had_score_depression",
        # SF-36 – item par item
        "sf36_q1",
        "sf36_q2",
        "sf36_q3a","sf36_q3b","sf36_q3c","sf36_q3d","sf36_q3e",
        "sf36_q3f","sf36_q3g","sf36_q3h","sf36_q3i","sf36_q3j",
        "sf36_q4a","sf36_q4b","sf36_q4c","sf36_q4d",
        "sf36_q5a","sf36_q5b","sf36_q5c",
        "sf36_q6",
        "sf36_q7","sf36_q8",
        "sf36_q9a","sf36_q9b","sf36_q9c","sf36_q9d","sf36_q9e",
        "sf36_q9f","sf36_q9g","sf36_q9h","sf36_q9i",
        "sf36_q10",
        "sf36_q11a","sf36_q11b","sf36_q11c","sf36_q11d",
        # SF-36 scores dimensionnels (0-100)
        "sf36_pf","sf36_rp","sf36_bp","sf36_gh",
        "sf36_vt","sf36_sf","sf36_re","sf36_mh",
        # BOLT
        "bolt_score", "bolt_interpretation",
        # Test d'hyperventilation volontaire
        "hvt_symptomes_reproduits",
        "hvt_symptomes_list",
        "hvt_duree_retour",
        "hvt_notes",
    ]


# ─── Sheet initialization ────────────────────────────────────────────────────

def ensure_sheets():
    ss = get_spreadsheet()

    try:
        ss.worksheet("Patients")
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet("Patients", rows=1000, cols=len(PATIENTS_HEADERS))
        ws.append_row(PATIENTS_HEADERS)

    try:
        ss.worksheet("Bilans_SHV")
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet("Bilans_SHV", rows=5000, cols=len(get_shv_headers()))
        ws.append_row(get_shv_headers())

    return ss


# ─── Patients ────────────────────────────────────────────────────────────────

def get_all_patients() -> pd.DataFrame:
    ss = ensure_sheets()
    ws = ss.worksheet("Patients")
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=PATIENTS_HEADERS)
    return pd.DataFrame(data)


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
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=get_shv_headers())
    df = pd.DataFrame(data)
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
