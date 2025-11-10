#!/usr/bin/env python3
"""
MusePartition CLI
Interface ligne de commande pour transcription audio → partition
"""

import argparse
import sys
from pathlib import Path
import json

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  rich non installé. Interface basique utilisée.")

from src.transcription_pipeline import TranscriptionPipeline


def create_parser() -> argparse.ArgumentParser:
    """Crée l'argument parser."""
    parser = argparse.ArgumentParser(
        prog="musepartition",
        description="🎵 MusePartition - Transcription audio vers partition musicale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Basique
  %(prog)s transcribe input.wav

  # Avec config personnalisée
  %(prog)s transcribe input.wav --config my_config.json

  # Override paramètres
  %(prog)s transcribe input.wav --bpm 120 --time-signature 3/4

  # Sortie personnalisée
  %(prog)s transcribe input.wav -o results/ --filename my_song

  # Mode verbose
  %(prog)s transcribe input.wav -v
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande: transcribe
    transcribe_parser = subparsers.add_parser(
        'transcribe',
        help='Transcrire fichier audio en partition'
    )
    
    # Positional
    transcribe_parser.add_argument(
        'input_file',
        type=str,
        help='Fichier audio à transcrire (WAV, MP3, FLAC)'
    )
    
    # Output
    transcribe_parser.add_argument(
        '-o', '--output',
        type=str,
        default='output',
        help='Répertoire de sortie (défaut: output/)'
    )
    
    transcribe_parser.add_argument(
        '--filename',
        type=str,
        default='score',
        help='Nom de base fichiers générés (défaut: score)'
    )
    
    # Config
    transcribe_parser.add_argument(
        '-c', '--config',
        type=str,
        help='Fichier config JSON (optionnel)'
    )
    
    # Override params - Quantization
    transcribe_parser.add_argument(
        '--bpm',
        type=float,
        help='Tempo fixe en BPM (override auto-détection)'
    )
    
    transcribe_parser.add_argument(
        '--time-signature',
        type=str,
        help='Signature temporelle (ex: 4/4, 3/4, 6/8)'
    )
    
    transcribe_parser.add_argument(
        '--quantization-grid',
        type=str,
        choices=['1/4', '1/8', '1/16', '1/32', '1/12', '1/24'],
        help='Grille de quantification'
    )
    
    transcribe_parser.add_argument(
        '--feel',
        type=str,
        choices=['straight', 'triplet'],
        help='Type rythmique (straight=binaire, triplet=ternaire)'
    )
    
    # Override params - Score
    transcribe_parser.add_argument(
        '--key',
        type=str,
        help='Tonalité (ex: C, G, D, Am, Em)'
    )
    
    transcribe_parser.add_argument(
        '--clef',
        type=str,
        choices=['treble', 'bass', 'alto', 'tenor'],
        help='Clef (sol, fa, ut3, ut4)'
    )
    
    transcribe_parser.add_argument(
        '--title',
        type=str,
        help='Titre de la partition'
    )
    
    transcribe_parser.add_argument(
        '--composer',
        type=str,
        help='Nom du compositeur'
    )
    
    # Override params - Pitch Detection
    transcribe_parser.add_argument(
        '--model',
        type=str,
        choices=['tiny', 'small', 'medium', 'large', 'full'],
        help='Taille modèle CREPE (medium=recommandé)'
    )
    
    # Debug
    transcribe_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mode verbeux (affiche logs détaillés)'
    )
    
    transcribe_parser.add_argument(
        '--save-intermediate',
        action='store_true',
        help='Sauvegarder résultats intermédiaires'
    )
    
    return parser


def build_config_from_args(args) -> dict:
    """Construit config à partir des arguments CLI."""
    config = {}
    
    # Charger config JSON si fournie
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Override avec args CLI
    if args.bpm:
        config.setdefault('quantization', {})['bpm'] = args.bpm
    
    if args.time_signature:
        config.setdefault('quantization', {})['time_signature'] = args.time_signature
        config.setdefault('score_generation', {})['time_signature'] = args.time_signature
    
    if args.quantization_grid:
        config.setdefault('quantization', {})['quantization_grid'] = args.quantization_grid
    
    if args.feel:
        config.setdefault('quantization', {})['feel'] = args.feel
    
    if args.key:
        config.setdefault('score_generation', {})['key_signature'] = args.key
    
    if args.clef:
        config.setdefault('score_generation', {})['clef'] = args.clef
    
    if args.title:
        config.setdefault('score_generation', {})['title'] = args.title
    
    if args.composer:
        config.setdefault('score_generation', {})['composer'] = args.composer
    
    if args.model:
        config.setdefault('pitch_detection', {})['model_capacity'] = args.model
    
    if args.filename:
        config.setdefault('output', {})['base_filename'] = args.filename
    
    # Debug
    config.setdefault('debug', {})['enabled'] = args.verbose
    config.setdefault('debug', {})['save_intermediate'] = args.save_intermediate
    
    return config


def print_result(result, console=None):
    """Affiche résultat de la transcription."""
    if RICH_AVAILABLE and console:
        # Affichage rich
        table = Table(title="✅ Transcription Terminée", show_header=True)
        table.add_column("Fichier", style="cyan")
        table.add_column("Chemin", style="green")
        
        table.add_row("MusicXML", result.musicxml_path)
        table.add_row("MIDI", result.midi_path)
        if result.pdf_path:
            table.add_row("PDF", result.pdf_path)
        else:
            table.add_row("PDF", "[yellow]Non généré (MuseScore requis)[/yellow]")
        
        console.print(table)
        
        # Stats
        stats = Table(title="📊 Statistiques", show_header=False)
        stats.add_column("Métrique", style="blue")
        stats.add_column("Valeur", style="white")
        
        stats.add_row("Tempo détecté", f"{result.bpm:.1f} BPM")
        stats.add_row("Notes transcrites", str(result.num_notes))
        stats.add_row("Temps de traitement", f"{result.processing_time:.2f}s")
        
        console.print(stats)
    else:
        # Affichage basique
        print("\n" + "="*60)
        print("✅ TRANSCRIPTION TERMINÉE")
        print("="*60)
        print(f"MusicXML : {result.musicxml_path}")
        print(f"MIDI     : {result.midi_path}")
        if result.pdf_path:
            print(f"PDF      : {result.pdf_path}")
        else:
            print(f"PDF      : Non généré (MuseScore requis)")
        print()
        print(f"Tempo    : {result.bpm:.1f} BPM")
        print(f"Notes    : {result.num_notes}")
        print(f"Durée    : {result.processing_time:.2f}s")
        print("="*60 + "\n")


def cmd_transcribe(args):
    """Exécute commande transcribe."""
    if RICH_AVAILABLE:
        console = Console()
    else:
        console = None
    
    # Validation input
    input_path = Path(args.input_file)
    if not input_path.exists():
        if console:
            console.print(f"[red]❌ Erreur:[/red] Fichier introuvable: {args.input_file}")
        else:
            print(f"❌ Erreur: Fichier introuvable: {args.input_file}")
        return 1
    
    # Construire config
    config = build_config_from_args(args)
    
    # Afficher démarrage
    if console:
        console.print(Panel.fit(
            f"🎵 [bold]MusePartition[/bold]\n"
            f"Transcription: [cyan]{args.input_file}[/cyan]",
            border_style="blue"
        ))
    else:
        print(f"\n🎵 MusePartition - Transcription: {args.input_file}\n")
    
    try:
        # Créer pipeline
        pipeline = TranscriptionPipeline(config)
        
        # Transcription avec progress bar
        if RICH_AVAILABLE and console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Transcription en cours...", total=None)
                result = pipeline.transcribe(args.input_file, args.output)
                progress.update(task, completed=True)
        else:
            print("⏳ Transcription en cours...")
            result = pipeline.transcribe(args.input_file, args.output)
        
        # Afficher résultat
        print_result(result, console)
        
        return 0
    
    except Exception as e:
        if console:
            console.print(f"\n[red]❌ Erreur:[/red] {e}")
            if args.verbose:
                console.print_exception()
        else:
            print(f"\n❌ Erreur: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
        return 1


def main():
    """Point d'entrée principal."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == 'transcribe':
        return cmd_transcribe(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
