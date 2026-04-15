# StreamController Plugin — ERPLibre

Plugin [StreamController](https://github.com/StreamController/StreamController) pour contrôler [ERPLibre](https://github.com/ERPLibre/erplibre)/Odoo depuis un Elgato Stream Deck.

## Actions disponibles

| Action | Description |
|--------|------------|
| **Odoo Status** | Affiche le statut du serveur Odoo (en ligne / hors ligne) via XML-RPC. Rafraîchi chaque seconde. |
| **TODO Launcher** | Lance le CLI interactif `todo.py` d'ERPLibre dans un terminal. |
| **Make Target** | Exécute une cible Makefile configurable (`run`, `test`, `format`, etc.). |
| **Database** | Opérations de base de données : restore, drop, list. Supporte les images de restauration. |
| **Module** | Install, update ou update_all de modules Odoo. |

## Prérequis

- [StreamController](https://github.com/StreamController/StreamController) installé (Flatpak ou depuis les sources)
- Elgato Stream Deck (Original, MK.2, Mini, XL, Plus, Neo)
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

- **Odoo Status** : URL du serveur (`http://localhost:8069`), nom de la base de données
- **TODO Launcher** : chemin vers l'installation ERPLibre (`~/erplibre01`)
- **Make Target** : cible Makefile à exécuter, chemin ERPLibre
- **Database** : opération (restore/drop/list), nom de la base, image de restauration, chemin ERPLibre
- **Module** : opération (install/update/update_all), nom du module, base de données, chemin ERPLibre

## Structure du plugin

```
com_erplibre_ERPLibre/
├── main.py                          # Point d'entrée, enregistrement des actions
├── manifest.json                    # Métadonnées du plugin
├── actions/
│   ├── OdooStatus/OdooStatus.py     # Statut serveur Odoo (XML-RPC)
│   ├── TodoLauncher/TodoLauncher.py # Lanceur todo.py
│   ├── MakeTarget/MakeTarget.py     # Exécution cible Makefile
│   ├── DbAction/DbAction.py        # Opérations base de données
│   └── ModuleAction/ModuleAction.py # Install/update modules Odoo
├── locales/
│   ├── en_US.json                   # Traductions anglais
│   └── fr_FR.json                   # Traductions français
├── assets/                          # Icônes et images
├── store/                           # Assets pour le StreamController Store
├── about.json                       # Informations auteur
└── attribution.json                 # Crédits et licence
```

## Licence

AGPL-3.0 — [TechnoLibre](http://www.technolibre.ca)
