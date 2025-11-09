#!/bin/bash
# MusePartition - Script d'installation automatique avec venv
# Usage: ./setup.sh

set -e  # Arrêter en cas d'erreur

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🎵 MusePartition - Installation avec venv 🐍          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher messages
info() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# 1. Vérifier Python 3.10+
echo "1️⃣  Vérification Python..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 non trouvé"
    echo "   Installer Python 3.10+ depuis https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    error "Python 3.10+ requis. Version actuelle: $PYTHON_VERSION"
    exit 1
fi

info "Python $PYTHON_VERSION détecté"

# 2. Vérifier module venv
echo ""
echo "2️⃣  Vérification module venv..."
if ! python3 -m venv --help &> /dev/null; then
    error "Module venv non disponible"
    echo "   Installer avec: sudo apt install python3-venv (Ubuntu/Debian)"
    exit 1
fi
info "Module venv disponible"

# 3. Créer environnement virtuel
echo ""
echo "3️⃣  Création environnement virtuel..."
if [ -d "venv" ]; then
    warn "venv existe déjà. Suppression et recréation..."
    rm -rf venv
fi

python3 -m venv venv
info "Environnement virtuel créé"

# 4. Activer venv
echo ""
echo "4️⃣  Activation environnement virtuel..."
source venv/bin/activate
info "Environnement activé"

# 5. Mettre à jour pip
echo ""
echo "5️⃣  Mise à jour pip..."
pip install --quiet --upgrade pip setuptools wheel
info "pip mis à jour: $(pip --version | cut -d' ' -f2)"

# 6. Installer dépendances
echo ""
echo "6️⃣  Installation dépendances..."
echo "   (Cela peut prendre 5-10 minutes...)"

# Installation avec barre de progression
pip install -r requirements.txt | grep -E "Successfully|Requirement already satisfied" || true

info "Dépendances installées"

# 7. Vérifier imports
echo ""
echo "7️⃣  Vérification imports..."
if python -c "from src.audio_processor import AudioProcessor; from src.types import PitchFrame" 2>/dev/null; then
    info "Imports Python OK"
else
    error "Erreur imports Python"
    exit 1
fi

# 8. Lancer tests
echo ""
echo "8️⃣  Lancement tests unitaires..."
if [ -f "tests/test_audio_processor.py" ]; then
    if pytest tests/test_audio_processor.py -v --tb=short; then
        info "Tests passés avec succès"
    else
        warn "Certains tests ont échoué (voir ci-dessus)"
    fi
else
    warn "Fichier de tests non trouvé"
fi

# 9. Résumé
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ✨ Installation terminée ! ✨              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Prochaines étapes :"
echo ""
echo "   1. Activer l'environnement virtuel :"
echo "      ${GREEN}source venv/bin/activate${NC}"
echo ""
echo "   2. Lancer les tests :"
echo "      ${GREEN}pytest tests/test_audio_processor.py -v${NC}"
echo ""
echo "   3. Tester avec un fichier audio :"
echo "      ${GREEN}python -m src.cli transcribe input.wav${NC}"
echo ""
echo "   4. Désactiver l'environnement :"
echo "      ${GREEN}deactivate${NC}"
echo ""
echo "📚 Documentation :"
echo "   - INSTALL_GUIDE.md : Guide installation détaillé"
echo "   - ARCHITECTURE.md  : Architecture du projet"
echo "   - README.md        : Vue d'ensemble"
echo ""

# Afficher packages installés
echo "📦 Packages principaux installés :"
pip list | grep -E "librosa|soundfile|crepe|tensorflow|music21|pytest|numpy|scipy" | sed 's/^/   /'
echo ""

# Note finale
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    info "Environnement prêt à l'emploi !"
    echo ""
    echo "   N'oubliez pas d'activer le venv avant chaque session :"
    echo "   ${GREEN}source venv/bin/activate${NC}"
else
    error "Problème lors de la création du venv"
    exit 1
fi
