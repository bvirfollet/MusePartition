# Guide d'Installation - MusePartition avec venv

**Date** : 2025-11-09  
**Python requis** : 3.10+

---

## 🐍 Setup avec Environnement Virtuel (Recommandé)

L'utilisation d'un environnement virtuel Python (venv) est **fortement recommandée** pour :
- Isoler les dépendances du projet
- Éviter les conflits avec d'autres projets
- Faciliter la reproduction de l'environnement
- Garder le système Python propre

---

## 📋 Installation Complète

### Étape 1 : Vérifier Python

```bash
# Vérifier version Python (3.10+ requis)
python3 --version

# Si Python 3.10+ n'est pas disponible, installer :
# Ubuntu/Debian :
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# macOS (avec Homebrew) :
brew install python@3.10

# Windows : Télécharger depuis python.org
```

### Étape 2 : Créer l'Environnement Virtuel

```bash
# Aller dans le répertoire du projet
cd /chemin/vers/MusePartition

# Créer le venv
python3 -m venv venv

# Alternative si python3 ne marche pas :
python -m venv venv
```

**Structure créée** :
```
MusePartition/
├── venv/                    # ← Environnement virtuel (ignoré par Git)
│   ├── bin/                 # Scripts d'activation (Linux/macOS)
│   ├── Scripts/             # Scripts d'activation (Windows)
│   ├── lib/                 # Packages Python installés
│   └── ...
├── src/
├── tests/
└── ...
```

### Étape 3 : Activer l'Environnement Virtuel

#### Linux / macOS
```bash
source venv/bin/activate
```

#### Windows (PowerShell)
```powershell
.\venv\Scripts\Activate.ps1
```

#### Windows (CMD)
```cmd
venv\Scripts\activate.bat
```

**Indication d'activation réussie** :
```bash
(venv) user@machine:~/MusePartition$
#  ^^^^^ Le préfixe (venv) apparaît
```

### Étape 4 : Installer les Dépendances

```bash
# Avec venv activé :
pip install --upgrade pip
pip install -r requirements.txt
```

**Temps d'installation** : ~5-10 minutes (selon connexion)

**Packages installés** :
- librosa (audio processing)
- soundfile (I/O audio)
- crepe (pitch detection)
- tensorflow (ML backend)
- music21 (notation musicale)
- pytest (tests)
- rich (CLI interface)
- + toutes les dépendances

### Étape 5 : Vérifier l'Installation

```bash
# Vérifier que tous les packages sont installés
pip list | grep -E "librosa|soundfile|crepe|tensorflow|music21|pytest"

# Test import Python
python -c "
from src.audio_processor import AudioProcessor
from src.types import PitchFrame, Note
print('✅ Imports OK!')
"

# Lancer les tests
pytest tests/test_audio_processor.py -v
```

**Résultat attendu** : 25/25 tests passants

---

## 🔄 Workflow Quotidien

### Démarrer une session de travail
```bash
cd /chemin/vers/MusePartition
source venv/bin/activate  # ou équivalent Windows
```

### Travailler sur le projet
```bash
# Éditer code
vim src/audio_processor.py

# Lancer tests
pytest tests/test_audio_processor.py -v

# Exécuter scripts
python -m src.cli transcribe input.wav
```

### Terminer la session
```bash
deactivate
```

---

## 📦 Gestion des Dépendances

### Ajouter une nouvelle dépendance
```bash
# Activer venv
source venv/bin/activate

# Installer package
pip install nouveau-package

# Mettre à jour requirements.txt
pip freeze > requirements.txt
```

### Mettre à jour les dépendances
```bash
# Activer venv
source venv/bin/activate

# Mettre à jour tous les packages
pip install --upgrade -r requirements.txt

# Ou package spécifique
pip install --upgrade librosa
```

### Réinstallation propre
```bash
# Désactiver venv si actif
deactivate

# Supprimer venv
rm -rf venv

# Recréer venv
python3 -m venv venv
source venv/bin/activate

# Réinstaller dépendances
pip install -r requirements.txt
```

---

## 🔧 Configuration IDE

### Visual Studio Code

Créer `.vscode/settings.json` :
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing environment
3. Sélectionner `MusePartition/venv/bin/python`
4. Apply → OK

### Vim/Neovim

Ajouter dans `.vimrc` ou `init.vim` :
```vim
" Utiliser le venv du projet
let g:python3_host_prog = expand('~/MusePartition/venv/bin/python')
```

---

## 🐛 Dépannage

### Problème : `venv` non reconnu
```bash
# Installer module venv
sudo apt install python3-venv  # Ubuntu/Debian
```

### Problème : Activation Windows ne marche pas
```powershell
# Autoriser exécution scripts PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problème : Packages ne s'installent pas
```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer setuptools et wheel
pip install --upgrade setuptools wheel

# Réessayer installation
pip install -r requirements.txt
```

### Problème : TensorFlow trop lent (CPU)
```bash
# Version CPU de TensorFlow est installée par défaut
# Pour GPU (si CUDA disponible) :
pip uninstall tensorflow
pip install tensorflow-gpu
```

### Problème : Tests échouent
```bash
# Vérifier que venv est actif
which python  # Doit pointer vers venv/bin/python

# Vérifier imports
python -c "import librosa; import pytest; print('OK')"

# Relancer tests avec verbose
pytest tests/test_audio_processor.py -vv
```

---

## 📝 Fichier .gitignore (Mise à Jour)

Le fichier `.gitignore` du projet doit inclure :

```gitignore
# Virtual Environment
venv/
env/
ENV/
.venv/
env.bak/
venv.bak/

# Python
__pycache__/
*.py[cod]
*.so
.Python
*.egg-info/
```

**Déjà configuré** dans le `.gitignore` fourni ✅

---

## 🚀 Script d'Installation Automatique

Créer `setup.sh` (Linux/macOS) :
```bash
#!/bin/bash
set -e

echo "🐍 MusePartition - Installation avec venv"
echo "=========================================="

# Vérifier Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé. Installer Python 3.10+."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.10" | bc -l) )); then
    echo "❌ Python 3.10+ requis. Version actuelle : $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION détecté"

# Créer venv
echo "📦 Création environnement virtuel..."
python3 -m venv venv

# Activer venv
echo "🔌 Activation venv..."
source venv/bin/activate

# Mettre à jour pip
echo "⬆️  Mise à jour pip..."
pip install --quiet --upgrade pip

# Installer dépendances
echo "📚 Installation dépendances..."
pip install -r requirements.txt

# Vérifier installation
echo "✅ Vérification installation..."
python -c "from src.audio_processor import AudioProcessor; print('✅ Imports OK')"

# Lancer tests
echo "🧪 Lancement tests..."
pytest tests/test_audio_processor.py -v

echo ""
echo "✨ Installation terminée avec succès !"
echo ""
echo "Pour activer l'environnement :"
echo "  source venv/bin/activate"
echo ""
echo "Pour lancer les tests :"
echo "  pytest tests/test_audio_processor.py -v"
```

Rendre exécutable :
```bash
chmod +x setup.sh
./setup.sh
```

---

## 📊 Résumé Commandes Essentielles

| Action | Commande (Linux/macOS) | Commande (Windows) |
|--------|------------------------|---------------------|
| Créer venv | `python3 -m venv venv` | `python -m venv venv` |
| Activer venv | `source venv/bin/activate` | `venv\Scripts\activate.bat` |
| Désactiver venv | `deactivate` | `deactivate` |
| Installer deps | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Lancer tests | `pytest tests/ -v` | `pytest tests/ -v` |
| Mettre à jour deps | `pip install --upgrade -r requirements.txt` | `pip install --upgrade -r requirements.txt` |

---

## 🎯 Checklist Validation Setup

- [ ] Python 3.10+ installé
- [ ] Venv créé (`python3 -m venv venv`)
- [ ] Venv activé (préfixe `(venv)` visible)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Imports fonctionnent (`python -c "from src.audio_processor import AudioProcessor"`)
- [ ] Tests passent (`pytest tests/test_audio_processor.py -v`)
- [ ] 25/25 tests passants ✅

---

## 💡 Bonnes Pratiques

### ✅ À FAIRE
- Toujours activer venv avant de travailler
- Mettre à jour `requirements.txt` après ajout package
- Tester dans venv avant commit
- Ignorer `venv/` dans Git (`.gitignore`)

### ❌ À ÉVITER
- Installer packages globalement (`sudo pip install`)
- Commiter le dossier `venv/`
- Oublier d'activer venv avant tests
- Mélanger Python 2 et Python 3

---

## 🆘 Support

Si problèmes persistent :
1. Vérifier version Python : `python3 --version`
2. Vérifier venv actif : `which python` (doit pointer vers venv)
3. Supprimer et recréer venv : `rm -rf venv && python3 -m venv venv`
4. Consulter logs d'erreur : `pip install -r requirements.txt 2>&1 | tee install.log`

---

**Version** : 1.0  
**Date** : 2025-11-09  
**Auteur** : Claude pour MusePartition
