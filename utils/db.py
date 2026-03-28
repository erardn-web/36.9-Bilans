"""
utils/db.py — Couche données (Google Sheets)

Structure :
  Patients  : un patient par ligne
  Cas       : un cas par pathologie par patient
  Bilans    : un bilan à plat (tous les champs en colonnes directes, comme v1)
  Audit_Log : qui a fait quoi et quand
"""

import uuid, json
import streamlit as st
import pandas as pd
from datetime import datetime, date

SPREADSHEET_NAME = "36.9_Bilans"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Champs plats des tests (générés depuis les classes de test) ───────────────
try:
    from utils._bilans_fields import ALL_TEST_FIELDS
except ImportError:
    try:
        from _bilans_fields import ALL_TEST_FIELDS
    except ImportError:
        ALL_TEST_FIELDS = []

# ── Client ────────────────────────────────────────────────────────────────────

@st.cache_resource(ttl=300)
def _get_client():
    import gspread
    from google.oauth2.service_account import Credentials
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
    return gspread.authorize(creds)


@st.cache_resource(ttl=600)
def _get_spreadsheet():
    import gspread
    client = _get_client()
    try:
        ss = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        raise Exception(f"Google Sheet '{SPREADSHEET_NAME}' introuvable.")
    # _ensure_sheet seulement au premier appel (cache_resource = une fois par session)
    _ensure_sheet(ss, "Patients",  PATIENTS_HEADERS)
    _ensure_sheet(ss, "Cas",       CAS_HEADERS)
    _ensure_sheet(ss, "Bilans",    BILANS_BASE_HEADERS + ALL_TEST_FIELDS)
    _ensure_sheet(ss, "Audit_Log", AUDIT_HEADERS)
    return ss

# ── Headers ───────────────────────────────────────────────────────────────────

PATIENTS_HEADERS = [
    "patient_id","cabinet_id","nom","prenom",
    "date_naissance","sexe","date_creation","actif",
]

CAS_HEADERS = [
    "cas_id","patient_id","cabinet_id",
    "template_id","template_snapshot","tests_actifs",
    "statut","praticien_creation","date_ouverture","date_cloture","notes_cas","analyse_ia",
]

# Colonnes de base du bilan — les champs des tests suivent directement
BILANS_BASE_HEADERS = [
    "bilan_id","cas_id","patient_id","cabinet_id",
    "praticien","date_bilan",
    "tests_actifs","diagnostic_prescription","poids_kg","taille_cm","bmi","fc_repos","fr_repos","ta_repos","spo2_repos","notes_generales","analyse_ia",
]

# Headers complets de la feuille Bilans
BILANS_HEADERS = BILANS_BASE_HEADERS + ALL_TEST_FIELDS

AUDIT_HEADERS = [
    "log_id","cas_id","bilan_id","patient_id",
    "cabinet_id","therapeute","action","timestamp",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ensure_sheet(ss, name, headers):
    """Crée la feuille si elle n'existe pas, ajoute les colonnes manquantes.
    Optimisé : skip header check si le nombre de colonnes est déjà correct."""
    import gspread
    try:
        ws = ss.worksheet(name)
        # Vérification légère : compter les colonnes sans lire tout le contenu
        if ws.col_count >= len(headers):
            return ws  # Headers déjà en place — ne pas relire
        # Colonnes manquantes — lire et corriger
        existing = ws.row_values(1)
        if not existing:
            ws.append_row(headers)
        else:
            missing = [h for h in headers if h not in existing]
            if missing:
                new_hdrs = existing + missing
                ws.resize(cols=len(new_hdrs))
                ws.update([new_hdrs], "A1")
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(name, rows=5000, cols=max(len(headers), 50))
        ws.append_row(headers)
    return ws


def _ws(name):
    """Retourne un worksheet avec retry + backoff."""
    import time
    last_exc = None
    for attempt in range(4):
        try:
            return _get_spreadsheet().worksheet(name)
        except Exception as e:
            last_exc = e
            try:
                _get_spreadsheet.clear()
                _get_client.clear()
            except Exception:
                pass
            if attempt < 3:
                time.sleep(1.5 ** attempt)
    raise last_exc


@st.cache_data(ttl=60)
def _cached_sheet_values(ws_title: str, spreadsheet_id: str):
    """Cache les valeurs brutes d'une feuille 60 secondes."""
    ws = _get_spreadsheet().worksheet(ws_title)
    return ws.get_all_values()


def _ws_to_df(ws, headers):
    try:
        rows = _cached_sheet_values(ws.title, ws.spreadsheet.id)
    except Exception:
        rows = ws.get_all_values()
    if len(rows) <= 1:
        return pd.DataFrame(columns=headers)
    actual  = rows[0]
    col_map = {h: actual.index(h) for h in headers if h in actual}
    records = []
    for row in rows[1:]:
        if not any(row): continue
        rec = {h: (row[col_map[h]] if h in col_map and col_map[h] < len(row) else "")
               for h in headers}
        records.append(rec)
    return pd.DataFrame(records, columns=headers)


def _new_id(prefix=""):
    return prefix + str(uuid.uuid4())[:8].upper()

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _append_row(ws_name, data: dict):
    ws  = _ws(ws_name)
    hdr = ws.row_values(1)
    row = [str(data.get(h, "")) for h in hdr]
    ws.append_row(row)
    _invalidate_read_cache()

def _update_row(ws_name, id_col, id_val, updates: dict) -> bool:
    ws = _ws(ws_name)
    try:
        rows = _cached_sheet_values(ws.title, ws.spreadsheet.id)
    except Exception:
        rows = ws.get_all_values()
    if not rows: return False
    hdr = rows[0]
    if id_col not in hdr: return False
    col_id = hdr.index(id_col)
    for i, row in enumerate(rows[1:], start=2):
        if row and len(row) > col_id and row[col_id] == id_val:
            row = list(row)  # copy
            while len(row) < len(hdr):
                row.append("")
            for k, v in updates.items():
                if k in hdr:
                    row[hdr.index(k)] = str(v)
            ws.update([row], f"A{i}")
            _invalidate_read_cache()
            return True
    return False

def _get_row(ws_name, id_col, id_val) -> dict:
    ws = _ws(ws_name)
    try:
        rows = _cached_sheet_values(ws.title, ws.spreadsheet.id)
    except Exception:
        rows = ws.get_all_values()
    if not rows: return {}
    hdr = rows[0]
    if id_col not in hdr: return {}
    col_id = hdr.index(id_col)
    for row in rows[1:]:
        if row and len(row) > col_id and row[col_id] == id_val:
            return dict(zip(hdr, row))
    return {}

def _invalidate_read_cache():
    try:
        get_all_patients.clear()
        get_patient_cas.clear()
        get_cas_bilans.clear()
        get_bilan.clear()
        get_cas.clear()
        _get_all_cas.clear()
        _cached_sheet_values.clear()
        try: get_cas_bilans_meta.clear()
        except: pass
    except Exception:
        pass

# ── Patients ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_all_patients(cabinet_id="default") -> pd.DataFrame:
    df = _ws_to_df(_ws("Patients"), PATIENTS_HEADERS)
    df = df[(df["cabinet_id"] == cabinet_id) & (df["actif"] != "0")]
    return df.reset_index(drop=True)

def search_patients(query, cabinet_id="default") -> pd.DataFrame:
    df = get_all_patients(cabinet_id)
    if not query.strip(): return df
    q    = query.upper().strip()
    mask = (df["nom"].str.upper().str.contains(q, na=False) |
            df["prenom"].str.upper().str.contains(q, na=False))
    return df[mask].reset_index(drop=True)

def create_patient(nom, prenom, date_naissance, sexe,
                   cabinet_id="default") -> str:
    pid = _new_id("P")
    _append_row("Patients", {
        "patient_id": pid, "cabinet_id": cabinet_id,
        "nom": nom.upper().strip(), "prenom": prenom.strip(),
        "date_naissance": str(date_naissance), "sexe": sexe,
        "date_creation": _now(), "actif": "1",
    })
    return pid

def update_patient(patient_id: str, nom: str, prenom: str,
                   date_naissance: str, sexe: str) -> bool:
    ok = _update_row("Patients", "patient_id", patient_id, {
        "nom": nom.upper().strip(),
        "prenom": prenom.strip(),
        "date_naissance": date_naissance,
        "sexe": sexe,
    })
    if ok:
        _invalidate_read_cache()
        get_all_patients.clear()
    return ok

# ── Cas ───────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def _get_all_cas(cabinet_id="default") -> pd.DataFrame:
    df = _ws_to_df(_ws("Cas"), CAS_HEADERS)
    return df[df["cabinet_id"] == cabinet_id].reset_index(drop=True)

@st.cache_data(ttl=60)
def get_patient_cas(patient_id) -> pd.DataFrame:
    df = _ws_to_df(_ws("Cas"), CAS_HEADERS)
    return df[df["patient_id"] == patient_id].reset_index(drop=True)

def create_cas(patient_id, template, praticien="",
               cabinet_id="default") -> str:
    cid      = _new_id("C")
    snapshot = template.snapshot()
    _append_row("Cas", {
        "cas_id": cid, "patient_id": patient_id, "cabinet_id": cabinet_id,
        "template_id": template.template_id,
        "template_snapshot": json.dumps(snapshot, ensure_ascii=False),
        "tests_actifs":      json.dumps(snapshot["tests"], ensure_ascii=False),
        "statut": "ouvert", "praticien_creation": praticien,
        "date_ouverture": str(date.today()), "date_cloture": "", "notes_cas": "",
    })
    _log_audit(cid, "", patient_id, cabinet_id, praticien, "creation_cas")
    return cid

@st.cache_data(ttl=60)
def get_cas(cas_id) -> dict:
    return _get_row("Cas", "cas_id", cas_id)

def set_cas_statut(cas_id, statut, therapeute="") -> bool:
    updates = {"statut": statut,
               "date_cloture": str(date.today()) if statut == "clos" else ""}
    ok = _update_row("Cas", "cas_id", cas_id, updates)
    if ok:
        cas    = get_cas(cas_id)
        action = "cloture_cas" if statut == "clos" else "reouverture_cas"
        _log_audit(cas_id, "", cas.get("patient_id",""),
                   cas.get("cabinet_id","default"), therapeute, action)
    return ok

def get_tests_actifs(cas_id) -> list:
    cas = get_cas(cas_id)
    if not cas: return []
    try:    return json.loads(cas.get("tests_actifs","[]") or "[]")
    except: return []

# ── Bilans (structure plate) ──────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_cas_bilans(cas_id) -> pd.DataFrame:
    """Retourne tous les bilans d'un cas avec tous les champs à plat."""
    ws = _ws("Bilans")
    # Utilise _cached_sheet_values — une seule requête réseau pour toute la feuille
    df = _ws_to_df(ws, BILANS_HEADERS)
    df = df[df["cas_id"] == cas_id]
    df["date_bilan"] = pd.to_datetime(df["date_bilan"], errors="coerce")
    return df.sort_values("date_bilan").reset_index(drop=True)


@st.cache_data(ttl=60)
def get_cas_bilans_meta(cas_id) -> pd.DataFrame:
    """Version légère — seulement les métadonnées (pas les 163 champs de tests).
    Utilisée pour afficher la liste des bilans sans charger toutes les données."""
    ws = _ws("Bilans")
    df = _ws_to_df(ws, BILANS_BASE_HEADERS)
    df = df[df["cas_id"] == cas_id]
    df["date_bilan"] = pd.to_datetime(df["date_bilan"], errors="coerce")
    return df.sort_values("date_bilan").reset_index(drop=True)


def get_cas_bilans_with_donnees(cas_id) -> pd.DataFrame:
    """Alias — en structure plate, get_cas_bilans retourne déjà tout."""
    return get_cas_bilans(cas_id)


def create_bilan(cas_id, praticien="",
                 bilan_date=None, cabinet_id="default") -> str:
    cas = get_cas(cas_id)
    bid = _new_id("B")

    # Hériter les tests_actifs du dernier bilan du même cas
    inherited_tests = ""
    try:
        bilans_existants = get_cas_bilans_meta(cas_id)
        if not bilans_existants.empty:
            dernier_bid = bilans_existants.iloc[-1]["bilan_id"]
            dernier = _get_row("Bilans", "bilan_id", dernier_bid)
            ta = dernier.get("tests_actifs","")
            if ta and ta not in ("","[]","None"):
                inherited_tests = ta
    except Exception:
        pass

    row = {
        "bilan_id":        bid,
        "cas_id":          cas_id,
        "patient_id":      cas.get("patient_id",""),
        "cabinet_id":      cabinet_id,
        "praticien":       praticien,
        "date_bilan":      str(bilan_date or date.today()),
        "tests_actifs":    inherited_tests,
        "notes_generales": "",
        "analyse_ia":      "",
    }
    # Tous les champs de tests à vide
    for f in ALL_TEST_FIELDS:
        row[f] = ""
    _append_row("Bilans", row)
    _log_audit(cas_id, bid, cas.get("patient_id",""),
               cabinet_id, praticien, "creation_bilan")
    return bid


@st.cache_data(ttl=60)
def get_bilan(bilan_id) -> dict:
    return _get_row("Bilans", "bilan_id", bilan_id)


def get_bilan_tests_actifs(bilan_id: str, snapshot: dict) -> list:
    """Retourne les tests actifs pour CE bilan.
    Si non défini → tous les tests du snapshot."""
    bilan = get_bilan(bilan_id)
    if not bilan:
        return list(snapshot.get("tests", []))
    raw = bilan.get("tests_actifs","")
    if raw and raw not in ("","[]","None"):
        try:
            return json.loads(raw)
        except Exception:
            pass
    return list(snapshot.get("tests", []))


def save_bilan_tests_actifs(bilan_id: str, test_ids: list) -> bool:
    return _update_row("Bilans", "bilan_id", bilan_id,
                       {"tests_actifs": json.dumps(test_ids)})


def get_bilan_donnees(bilan_id) -> dict:
    """Retourne les données du bilan — directement depuis la ligne plate."""
    bilan = get_bilan(bilan_id)
    if not bilan: return {}
    # Retourner uniquement les champs de tests (pas les métadonnées)
    donnees = {}
    for f in ALL_TEST_FIELDS:
        if f in bilan:
            donnees[f] = bilan[f]
    # Compatibilité : si ancienne structure JSON encore présente
    raw_donnees = bilan.get("donnees","")
    if raw_donnees and raw_donnees not in ("{}",""):
        try:
            old_data = json.loads(raw_donnees)
            # Merger avec priorité aux colonnes plates
            for k, v in old_data.items():
                if k not in donnees or not donnees[k]:
                    donnees[k] = v
        except Exception:
            pass
    return donnees


def save_bilan_donnees(bilan_id, donnees: dict, therapeute="") -> bool:
    """Sauvegarde les données du bilan directement dans les colonnes plates."""
    # Filtrer uniquement les champs connus
    updates = {}
    for k, v in donnees.items():
        updates[k] = str(v) if v is not None else ""
    # Inclure aussi notes_generales si présent
    if "notes_generales" in donnees:
        updates["notes_generales"] = str(donnees["notes_generales"])

    ok = _update_row("Bilans", "bilan_id", bilan_id, updates)
    if ok:
        bilan = get_bilan(bilan_id)
        _log_audit(bilan.get("cas_id",""), bilan_id,
                   bilan.get("patient_id",""),
                   bilan.get("cabinet_id","default"),
                   therapeute, "modification_bilan")
    return ok


def delete_bilan(bilan_id: str, therapeute: str = "") -> bool:
    ws   = _ws("Bilans")
    rows = ws.get_all_values()
    if not rows: return False
    hdr = rows[0]
    if "bilan_id" not in hdr: return False
    col_bid = hdr.index("bilan_id")
    for i, row in enumerate(rows[1:], start=2):
        if row and len(row) > col_bid and row[col_bid] == bilan_id:
            bilan = dict(zip(hdr, row))
            ws.delete_rows(i)
            _invalidate_read_cache()
            _log_audit(bilan.get("cas_id",""), bilan_id,
                       bilan.get("patient_id",""),
                       bilan.get("cabinet_id","default"),
                       therapeute, "suppression_bilan")
            return True
    return False

# ── Analyse IA ────────────────────────────────────────────────────────────────

def save_analyse_ia(bilan_id, texte) -> bool:
    return _update_row("Bilans","bilan_id", bilan_id, {"analyse_ia": texte})

def load_analyse_ia(bilan_id) -> str:
    bilan = get_bilan(bilan_id)
    return bilan.get("analyse_ia","") if bilan else ""

# ── Audit ─────────────────────────────────────────────────────────────────────

def _log_audit(cas_id, bilan_id, patient_id, cabinet_id,
               therapeute, action):
    try:
        _append_row("Audit_Log", {
            "log_id": _new_id("L"), "cas_id": cas_id,
            "bilan_id": bilan_id, "patient_id": patient_id,
            "cabinet_id": cabinet_id, "therapeute": therapeute,
            "action": action, "timestamp": _now(),
        })
    except Exception:
        pass

def get_audit_log(cas_id) -> pd.DataFrame:
    df = _ws_to_df(_ws("Audit_Log"), AUDIT_HEADERS)
    df = df[df["cas_id"] == cas_id].sort_values("timestamp", ascending=False)
    return df[["timestamp","therapeute","action"]].reset_index(drop=True)

# ── Compatibilité — migration JSON → plat ─────────────────────────────────────

def migrate_bilan_to_flat(bilan_id: str) -> bool:
    """Migre un bilan de l'ancien format JSON vers le format plat."""
    ws   = _ws("Bilans")
    rows = ws.get_all_values()
    if not rows: return False
    hdr = rows[0]
    if "bilan_id" not in hdr or "donnees" not in hdr: return False
    col_bid     = hdr.index("bilan_id")
    col_donnees = hdr.index("donnees")
    for i, row in enumerate(rows[1:], start=2):
        if not row or len(row) <= col_bid: continue
        if row[col_bid] != bilan_id: continue
        raw = row[col_donnees] if col_donnees < len(row) else ""
        if not raw or raw in ("{}",""): return True  # Déjà migré
        try:
            donnees = json.loads(raw)
        except Exception:
            return False
        while len(row) < len(hdr):
            row.append("")
        for k, v in donnees.items():
            if k in hdr:
                row[hdr.index(k)] = str(v)
        row[col_donnees] = ""  # Vider l'ancienne colonne JSON
        ws.update([row], f"A{i}")
        _invalidate_read_cache()
        return True
    return False
