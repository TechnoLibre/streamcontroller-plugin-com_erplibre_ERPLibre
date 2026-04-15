# StreamController Plugin — ERPLibre

Plugin [StreamController](https://github.com/StreamController/StreamController) pour contrôler [ERPLibre](https://github.com/ERPLibre/erplibre)/Odoo depuis un Elgato Stream Deck.

## Actions disponibles

### ERPLibre / Odoo

| Action | Description |
|--------|------------|
| **Odoo Status** | Statut serveur Odoo (en ligne / hors ligne) via XML-RPC. Rafraîchi chaque seconde. |
| **Odoo Counter** | Compteur dynamique de records Odoo (commandes, factures, tickets, CRM, tâches). 7 presets + mode custom avec modèle/domaine JSON configurable. |
| **Odoo Workflow** | Déclenche des actions Odoo : confirmer devis, publier facture, confirmer achat. 4 presets + mode custom avec modèle/méthode/domaine configurable. |
| **TODO Launcher** | Lance le CLI interactif `todo.py` d'ERPLibre dans un terminal. |
| **Make Target** | Exécute une cible Makefile configurable (`run`, `test`, `format`, etc.). |
| **Database** | Opérations de base de données : restore, drop, list. Supporte les images de restauration. |
| **Module** | Install, update ou update_all de modules Odoo. |

### Utilitaires

| Action | Description |
|--------|------------|
| **Webcam** | Flux webcam live sur un bouton. Source locale (OpenCV) ou caméra IP. FPS configurable. Toggle on/off par appui. |
| **Brightness** | Contrôle luminosité du Stream Deck. Direction (up/down) et pas configurables. |
| **Keyboard Talk** | Lance le script d'automatisation clavier `keyboard_talk.py` dans un terminal. |

## Prérequis

- [StreamController](https://github.com/StreamController/StreamController) installé (Flatpak ou depuis les sources)
- Elgato Stream Deck (Original, MK.2, Mini, XL, Plus, Neo)
- Python 3.12+
- Règles udev configurées pour accès non-root :

```bash
sudo tee /etc/udev/rules.d/70-streamdeck.rules << 'EOF'
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", TAG+="uaccess"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Installation

### Depuis les sources (développement)

```bash
git clone https://github.com/StreamController/StreamController.git
cd StreamController
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data/plugins
cd data/plugins
git clone https://github.com/TechnoLibre/streamcontroller-plugin-com_erplibre_ERPLibre.git com_erplibre_ERPLibre
cd ../..
python main.py --data data
```

### Dépendances système (Debian/Ubuntu)

```bash
sudo apt install -y libdbus-1-dev libudev-dev libusb-1.0-0-dev libhidapi-libusb0
```

## Configuration

Chaque action se configure via l'interface StreamController :

### Connexion Odoo (OdooCounter, OdooWorkflow)

- **URL** : `http://localhost:8069`
- **Base de données** : nom de la DB Odoo
- **Utilisateur** : login Odoo (défaut : `admin`)
- **Mot de passe** : mot de passe Odoo (défaut : `admin`)

### OdooCounter — Presets disponibles

| Preset | Modèle | Filtre |
|--------|--------|--------|
| `sale_order` | sale.order | Commandes confirmées |
| `invoice` | account.move | Factures publiées |
| `draft_invoice` | account.move | Factures brouillon |
| `purchase_order` | purchase.order | Achats confirmés |
| `helpdesk_ticket` | helpdesk.ticket | Tickets ouverts |
| `crm_lead` | crm.lead | Opportunités actives |
| `project_task` | project.task | Tâches ouvertes |
| `custom` | configurable | Modèle + domaine JSON libre |

### OdooWorkflow — Presets disponibles

| Preset | Action | Cible |
|--------|--------|-------|
| `confirm_sale` | action_confirm | Devis draft |
| `confirm_purchase` | button_confirm | Achats draft |
| `validate_invoice` | action_post | Factures draft |
| `cancel_sale` | _action_cancel | Devis draft |
| `custom` | configurable | Modèle + méthode + domaine libre |

### Actions ERPLibre

- **TODO Launcher** : chemin vers l'installation ERPLibre (`~/erplibre01`)
- **Make Target** : cible Makefile à exécuter, chemin ERPLibre
- **Database** : opération (restore/drop/list), nom de la base, image de restauration, chemin ERPLibre
- **Module** : opération (install/update/update_all), nom du module, base de données, chemin ERPLibre

### Utilitaires

- **Webcam** : source (local/ip), index caméra, URL caméra IP, FPS
- **Brightness** : direction (up/down), pas en %
- **Keyboard Talk** : chemin ERPLibre

## Structure du plugin

```
com_erplibre_ERPLibre/
├── main.py                              # Point d'entrée, enregistrement des 10 actions
├── manifest.json                        # Métadonnées du plugin
├── api/
│   ├── __init__.py
│   └── odoo_rpc.py                      # Client XML-RPC Odoo (auth, search, execute)
├── actions/
│   ├── OdooStatus/OdooStatus.py         # Statut serveur Odoo
│   ├── OdooCounter/OdooCounter.py       # Compteurs dynamiques Odoo
│   ├── OdooWorkflow/OdooWorkflow.py     # Déclencheur actions workflow Odoo
│   ├── TodoLauncher/TodoLauncher.py     # Lanceur todo.py
│   ├── MakeTarget/MakeTarget.py         # Exécution cible Makefile
│   ├── DbAction/DbAction.py            # Opérations base de données
│   ├── ModuleAction/ModuleAction.py     # Install/update modules Odoo
│   ├── WebcamAction/WebcamAction.py     # Flux webcam live sur bouton
│   ├── BrightnessAction/BrightnessAction.py  # Contrôle luminosité
│   └── KeyboardAction/KeyboardAction.py # Automatisation clavier
├── locales/
│   ├── en_US.json                       # Traductions anglais
│   └── fr_FR.json                       # Traductions français
├── assets/                              # Icônes et images
├── store/                               # Assets pour le StreamController Store
├── about.json                           # Informations auteur
└── attribution.json                     # Crédits et licence
```

## Développement

### Lancer en mode développement

```bash
cd ~/git/streamcontroller-erplibre
source .venv/bin/activate
python main.py --data data
```

### Lancer les tests

```bash
cd ~/git/streamcontroller-erplibre/data/plugins/com_erplibre_ERPLibre
python -m pytest tests/ -v
```

### Vérification du code

```bash
python -m py_compile main.py
python -m py_compile api/odoo_rpc.py
for f in actions/*//*.py; do python -m py_compile "$f"; done
```

## Licence

AGPL-3.0 — [TechnoLibre](http://www.technolibre.ca)
