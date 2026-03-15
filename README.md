# 🫁 PhysioApp — Bilans Physiothérapeutiques

Application web Streamlit pour la gestion des bilans physiothérapeutiques, avec stockage des données dans Google Sheets.

## ✨ Fonctionnalités (v0.1)

- **Page d'accueil** avec accès aux différents modules de bilan
- **Module SHV** (Syndrome d'Hyperventilation) comprenant :
  - Gestion des patients (création, recherche)
  - Bilans horodatés (initial, intermédiaire, final)
  - Échelle HAD (anxiété & dépression) avec calcul automatique des scores
  - SF-36 (qualité de vie, 8 dimensions) avec graphique radar
  - Test BOLT avec interprétation
  - Test d'hyperventilation volontaire avec liste de symptômes
  - Sauvegarde et rechargement des bilans via Google Sheets

---

## 🚀 Installation & déploiement

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-user/physio-app.git
cd physio-app
```

### 2. Installer les dépendances (développement local)

```bash
pip install -r requirements.txt
```

### 3. Configurer Google Sheets

#### a. Créer un projet Google Cloud

1. Allez sur [console.cloud.google.com](https://console.cloud.google.com)
2. Créez un nouveau projet (ex. `physio-app`)
3. Activez les APIs suivantes :
   - **Google Sheets API**
   - **Google Drive API**

#### b. Créer un compte de service

1. Menu → IAM & Admin → Comptes de service → **Créer**
2. Donnez-lui un nom (ex. `physio-app`)
3. Créez et téléchargez une **clé JSON**

#### c. Configurer les secrets Streamlit

Copiez `.streamlit/secrets.toml.example` vers `.streamlit/secrets.toml` :

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Puis remplissez les valeurs avec le contenu de votre fichier JSON :

```toml
[gcp_service_account]
type                        = "service_account"
project_id                  = "votre-project-id"
private_key_id              = "..."
private_key                 = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email                = "physio-app@votre-project.iam.gserviceaccount.com"
# ... (autres champs du JSON)
```

> ⚠️ `secrets.toml` est dans `.gitignore` — **ne le commitez jamais** !

#### d. Partager le Google Sheet avec le compte de service

1. L'application crée automatiquement le classeur **"Physio_App"** au premier lancement
2. Après création, partagez-le avec l'adresse `client_email` de votre compte de service (rôle Éditeur)
   — *ou* partagez-le à l'avance en créant vous-même un classeur nommé exactement `Physio_App`

### 4. Lancer en local

```bash
streamlit run app.py
```

---

## ☁️ Déploiement sur Streamlit Community Cloud

1. Pushez votre code sur GitHub (sans `secrets.toml`)
2. Allez sur [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Sélectionnez votre dépôt, branche `main`, fichier `app.py`
4. Dans **Advanced settings → Secrets**, collez le contenu de `secrets.toml`
5. Cliquez **Deploy** 🚀

---

## 📁 Structure du projet

```
physio-app/
├── app.py                         # Page d'accueil
├── pages/
│   └── 1_SHV_Bilan.py            # Module Bilan SHV
├── utils/
│   ├── __init__.py
│   ├── google_sheets.py           # Connexion & CRUD Google Sheets
│   ├── had.py                     # Questionnaire HAD
│   ├── sf36.py                    # Questionnaire SF-36
│   └── shv_tests.py               # Tests BOLT & HVT
├── .streamlit/
│   └── secrets.toml.example       # Modèle de configuration
├── requirements.txt
├── .gitignore
└── README.md
```

## 🗄️ Structure Google Sheets

### Feuille `Patients`

| Colonne | Description |
|---|---|
| `patient_id` | Identifiant unique (8 caractères) |
| `nom` | Nom en majuscules |
| `prenom` | Prénom |
| `date_naissance` | Date de naissance |
| `sexe` | Féminin / Masculin / Autre |
| `profession` | Profession |
| `date_creation` | Horodatage de création |

### Feuille `Bilans_SHV`

Contient une ligne par bilan avec :
- Identification (bilan_id, patient_id, date, type, praticien)
- 14 items HAD + scores anxiété/dépression
- 36 items SF-36 + 8 scores dimensionnels
- Score BOLT + interprétation
- Résultats THV (symptômes, durée de retour, notes)

---

## 📈 Évolutions prévues

- [ ] Graphiques d'évolution des scores dans le temps
- [ ] Export PDF du bilan
- [ ] Bilan musculo-squelettique
- [ ] Bilan cardio-respiratoire
- [ ] Questionnaire de Nijmegen (SHV)
- [ ] Authentification praticien

---

## 🔒 Sécurité & confidentialité

- Les données sont stockées dans **votre propre Google Sheet** (vous en gardez le contrôle)
- Le fichier `secrets.toml` ne doit jamais être partagé ni commité
- Sur Streamlit Cloud, les secrets sont chiffrés
