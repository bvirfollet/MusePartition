"""
MusePartition - Score Generator Module
Génération de partitions musicales à partir de notes quantifiées
"""

import music21
from typing import List, Optional
from pathlib import Path
from src.types import QuantizedNote
from src.utils import DebugTracer


class ScoreGenerator:
    """
    Génère des partitions musicales au format MusicXML, PDF et MIDI.
    
    Convertit des notes quantifiées en partition formatée avec clef,
    armure, mesures, etc. en utilisant la bibliothèque music21.
    """
    
    def __init__(
        self,
        time_signature: str = "4/4",
        key_signature: str = "C",
        clef: str = "treble",
        instrument_name: str = "Flute",
        debug: bool = False
    ):
        """
        Initialise le ScoreGenerator.
        
        Args:
            time_signature: Signature temporelle (défaut: "4/4").
            key_signature: Tonalité (défaut: "C").
                Formats: "C", "G", "D", "A", "E", "B", "F#", "C#"
                         "F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"
                         Mineurs: "Am", "Em", "Bm", "F#m", etc.
            clef: Clef (défaut: "treble").
                Options: "treble" (sol), "bass" (fa), "alto" (ut3), "tenor" (ut4)
            instrument_name: Nom de l'instrument (défaut: "Flute").
            debug: Active le traçage debug (défaut: False).
        
        Example:
            >>> # Flûte en do majeur
            >>> generator = ScoreGenerator()
            >>> 
            >>> # Piano en ré majeur
            >>> generator = ScoreGenerator(
            ...     key_signature="D",
            ...     instrument_name="Piano"
            ... )
            >>> 
            >>> # Contrebasse en clef de fa
            >>> generator = ScoreGenerator(
            ...     clef="bass",
            ...     instrument_name="Double Bass"
            ... )
        """
        self.time_signature = time_signature
        self.key_signature = key_signature
        self.clef = clef
        self.instrument_name = instrument_name
        self.tracer = DebugTracer(output_dir="output/debug", enabled=debug)
        
        self.tracer.log_step("score_generator_init", {
            "time_signature": time_signature,
            "key_signature": key_signature,
            "clef": clef,
            "instrument": instrument_name
        })
    
    def notes_to_music21(
        self,
        quantized_notes: List[QuantizedNote],
        bpm: float,
        rest_threshold: float = 0.25
    ) -> music21.stream.Score:
        """
        Convertit notes quantifiées en objet music21 Score.
        
        Args:
            quantized_notes: Liste de notes quantifiées.
            bpm: Tempo en BPM.
            rest_threshold: Seuil minimum (en beats) pour insérer un silence (défaut: 0.25).
        
        Returns:
            music21.stream.Score avec partition complète.
        
        Raises:
            ValueError: Si quantized_notes est vide.
        
        Example:
            >>> quantized, bpm = quantizer.quantize_notes(notes, bpm=120.0)
            >>> score = generator.notes_to_music21(quantized, bpm)
            >>> score.show('text')  # Afficher en mode texte
        """
        if not quantized_notes:
            raise ValueError("Liste de notes vide")
        
        self.tracer.log_step("conversion_start", {
            "input_notes": len(quantized_notes),
            "bpm": bpm
        })
        
        # Créer structure Score → Part → Measure
        score = music21.stream.Score()
        part = music21.stream.Part()
        part.partName = self.instrument_name
        
        # Ajouter métadonnées
        score.metadata = music21.metadata.Metadata()
        score.metadata.title = "Transcription"
        score.metadata.composer = "MusePartition"
        
        # Configuration initiale de la première mesure
        first_measure = music21.stream.Measure(number=1)
        
        # Ajouter clef
        if self.clef == "treble":
            first_measure.append(music21.clef.TrebleClef())
        elif self.clef == "bass":
            first_measure.append(music21.clef.BassClef())
        elif self.clef == "alto":
            first_measure.append(music21.clef.AltoClef())
        elif self.clef == "tenor":
            first_measure.append(music21.clef.TenorClef())
        
        # Ajouter armure
        key = music21.key.Key(self.key_signature)
        first_measure.append(key)
        
        # Ajouter signature temporelle
        ts_parts = self.time_signature.split("/")
        time_sig = music21.meter.TimeSignature(f"{ts_parts[0]}/{ts_parts[1]}")
        first_measure.append(time_sig)
        
        # Ajouter tempo
        metronome = music21.tempo.MetronomeMark(number=bpm)
        first_measure.append(metronome)
        
        # Convertir notes quantifiées en notes music21
        beats_per_measure = int(ts_parts[0])
        current_measure = first_measure
        current_measure_beat = 0.0
        measure_number = 1
        
        # Tri des notes par position (sécurité)
        sorted_notes = sorted(quantized_notes, key=lambda n: n.beat_position)
        
        # Position de fin de dernière note traitée
        last_note_end = 0.0
        
        for qnote in sorted_notes:
            # Vérifier s'il faut insérer un silence avant cette note
            gap = qnote.beat_position - last_note_end
            if gap >= rest_threshold:
                # Créer silence pour le gap
                beat_unit = int(ts_parts[1])
                rest_quarter_length = gap * (4.0 / beat_unit)
                rest = music21.note.Rest(quarterLength=rest_quarter_length)
                
                # Gérer changement de mesure si nécessaire pour le silence
                while last_note_end >= (measure_number * beats_per_measure):
                    part.append(current_measure)
                    measure_number += 1
                    current_measure = music21.stream.Measure(number=measure_number)
                    current_measure_beat = (measure_number - 1) * beats_per_measure
                
                offset_in_measure = last_note_end - current_measure_beat
                offset_quarter = offset_in_measure * (4.0 / beat_unit)
                current_measure.insert(offset_quarter, rest)
            
            # Vérifier si on doit créer nouvelle mesure pour la note
            while qnote.beat_position >= (measure_number * beats_per_measure):
                # Finaliser mesure courante
                part.append(current_measure)
                
                # Créer nouvelle mesure
                measure_number += 1
                current_measure = music21.stream.Measure(number=measure_number)
                current_measure_beat = (measure_number - 1) * beats_per_measure
            
            # Créer note music21
            pitch = music21.pitch.Pitch(midi=qnote.midi_note)
            
            # Calculer durée en quarterLength (noires)
            # 1 beat = 1 quarterLength en 4/4
            # En 6/8, 1 beat (croche) = 0.5 quarterLength
            beat_unit = int(ts_parts[1])
            quarter_length = qnote.duration_beats * (4.0 / beat_unit)
            
            note = music21.note.Note(pitch, quarterLength=quarter_length)
            
            # Calculer offset dans la mesure
            offset_in_measure = qnote.beat_position - current_measure_beat
            offset_quarter = offset_in_measure * (4.0 / beat_unit)
            
            current_measure.insert(offset_quarter, note)
            
            # Mettre à jour position de fin pour prochaine itération
            last_note_end = qnote.beat_position + qnote.duration_beats
        
        # Ajouter dernière mesure
        part.append(current_measure)
        
        # Ajouter part au score
        score.append(part)
        
        self.tracer.log_step("conversion_complete", {
            "measures": measure_number,
            "notes_converted": len(quantized_notes)
        })
        
        return score
    
    def export_musicxml(
        self,
        score: music21.stream.Score,
        output_path: str
    ) -> Path:
        """
        Exporte la partition en MusicXML.
        
        Args:
            score: Partition music21.
            output_path: Chemin du fichier de sortie (.xml ou .musicxml).
        
        Returns:
            Path du fichier créé.
        
        Example:
            >>> generator.export_musicxml(score, "output/score.musicxml")
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.tracer.log_step("export_musicxml_start", {
            "output_path": str(output_path)
        })
        
        score.write('musicxml', fp=str(output_path))
        
        self.tracer.log_step("export_musicxml_complete", {
            "file_size": output_path.stat().st_size
        })
        
        return output_path
    
    def export_pdf(
        self,
        score: music21.stream.Score,
        output_path: str
    ) -> Path:
        """
        Exporte la partition en PDF via MuseScore.
        
        Args:
            score: Partition music21.
            output_path: Chemin du fichier de sortie (.pdf).
        
        Returns:
            Path du fichier créé.
        
        Raises:
            RuntimeError: Si MuseScore n'est pas installé ou configuré.
        
        Note:
            Nécessite MuseScore 3+ installé et configuré dans music21.
            Configuration: music21.environment.set('musescoreDirectPNGPath', '/path/to/musescore')
        
        Example:
            >>> generator.export_pdf(score, "output/score.pdf")
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.tracer.log_step("export_pdf_start", {
            "output_path": str(output_path)
        })
        
        try:
            score.write('musicxml.pdf', fp=str(output_path))
            
            self.tracer.log_step("export_pdf_complete", {
                "file_size": output_path.stat().st_size if output_path.exists() else 0
            })
            
            return output_path
        except Exception as e:
            raise RuntimeError(
                f"Échec export PDF. MuseScore installé et configuré ? Erreur: {e}"
            )
    
    def export_midi(
        self,
        score: music21.stream.Score,
        output_path: str
    ) -> Path:
        """
        Exporte la partition en MIDI.
        
        Args:
            score: Partition music21.
            output_path: Chemin du fichier de sortie (.mid ou .midi).
        
        Returns:
            Path du fichier créé.
        
        Example:
            >>> generator.export_midi(score, "output/score.mid")
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.tracer.log_step("export_midi_start", {
            "output_path": str(output_path)
        })
        
        score.write('midi', fp=str(output_path))
        
        self.tracer.log_step("export_midi_complete", {
            "file_size": output_path.stat().st_size
        })
        
        return output_path
    
    def generate_score(
        self,
        quantized_notes: List[QuantizedNote],
        bpm: float,
        output_dir: str = "output",
        base_filename: str = "score",
        title: str = "Transcription",
        composer: str = "MusePartition"
    ) -> dict:
        """
        Génère partition complète avec exports MusicXML, MIDI et PDF (optionnel).
        
        Args:
            quantized_notes: Notes quantifiées.
            bpm: Tempo.
            output_dir: Répertoire de sortie (défaut: "output").
            base_filename: Nom de base des fichiers (défaut: "score").
            title: Titre de la partition (défaut: "Transcription").
            composer: Nom du compositeur (défaut: "MusePartition").
        
        Returns:
            Dictionnaire avec chemins des fichiers générés:
            {
                'musicxml': Path,
                'midi': Path,
                'pdf': Path ou None (si échec)
            }
        
        Example:
            >>> paths = generator.generate_score(
            ...     quantized_notes,
            ...     bpm=120.0,
            ...     output_dir="output",
            ...     base_filename="my_transcription",
            ...     title="My Song",
            ...     composer="John Doe"
            ... )
            >>> print(f"MusicXML: {paths['musicxml']}")
            >>> print(f"MIDI: {paths['midi']}")
        """
        self.tracer.log_step("generate_score_start", {
            "notes": len(quantized_notes),
            "bpm": bpm,
            "output_dir": output_dir
        })
        
        # Créer score
        score = self.notes_to_music21(quantized_notes, bpm)
        
        # Mettre à jour metadata
        score.metadata.title = title
        score.metadata.composer = composer
        
        # Exports
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        paths = {}
        
        # MusicXML (toujours)
        paths['musicxml'] = self.export_musicxml(
            score,
            str(output_dir / f"{base_filename}.musicxml")
        )
        
        # MIDI (toujours)
        paths['midi'] = self.export_midi(
            score,
            str(output_dir / f"{base_filename}.mid")
        )
        
        # PDF (optionnel, peut échouer si MuseScore absent)
        try:
            paths['pdf'] = self.export_pdf(
                score,
                str(output_dir / f"{base_filename}.pdf")
            )
        except RuntimeError as e:
            self.tracer.log_step("pdf_export_skipped", {
                "reason": str(e)
            })
            paths['pdf'] = None
        
        self.tracer.log_step("generate_score_complete", {
            "musicxml": str(paths['musicxml']),
            "midi": str(paths['midi']),
            "pdf": str(paths['pdf']) if paths['pdf'] else "skipped"
        })
        
        return paths
