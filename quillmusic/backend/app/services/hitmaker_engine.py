"""
HitMaker Engine - Intelligent song analysis and improvement suggestions.

This service provides deterministic, heuristic-based analysis of songs
from both AI blueprints and Manual Creator projects. It models "Song DNA"
including energy curves, tension, hooks, and predicts commercial viability.
"""

import re
from typing import Optional
from app.schemas.hitmaker import (
    SectionEnergy,
    SongDNA,
    HitScoreBreakdown,
    HitMakerAnalysis,
    InfluenceDescriptor,
    HitMakerInfluenceResponse,
)
from app.schemas.song import SongBlueprintResponse
from app.models.manual import ManualProjectModel, TrackModel, PatternModel, NoteModel


class HitMakerEngine:
    """
    Analyzes songs and provides AI-driven insights for hit potential.

    Currently uses deterministic heuristics. Future versions may integrate
    LLM-based analysis for deeper insights.
    """

    # Genre-tempo mappings (BPM ranges)
    GENRE_TEMPO_RANGES = {
        "hiphop": (80, 110),
        "trap": (130, 170),
        "pop": (100, 130),
        "rock": (110, 140),
        "edm": (120, 140),
        "house": (120, 130),
        "dubstep": (135, 145),
        "indie": (90, 130),
        "ballad": (60, 90),
    }

    # Emotional keywords for lyrics analysis
    EMOTIONAL_KEYWORDS = {
        "positive": ["love", "happy", "joy", "bright", "smile", "free", "dream", "shine"],
        "negative": ["pain", "hurt", "lost", "dark", "alone", "broken", "cry", "fade"],
        "intense": ["fire", "burn", "explode", "scream", "fight", "rage", "wild"],
        "calm": ["soft", "gentle", "quiet", "peace", "still", "whisper", "calm"],
    }

    def analyze_blueprint(
        self,
        blueprint: SongBlueprintResponse,
        project: Optional[ManualProjectModel] = None
    ) -> HitMakerAnalysis:
        """Analyze an AI-generated song blueprint."""

        # Extract section-level analysis
        sections = self._analyze_blueprint_sections(blueprint)

        # Build energy/tension curves
        energy_curve = [s.energy for s in sections]
        tension_curve = [s.tension for s in sections]

        # Determine mood and genre
        dominant_mood = self._infer_mood_from_blueprint(blueprint)
        genre_guess = self._infer_genre_from_blueprint(blueprint)

        # Generate structure notes
        structure_notes = self._generate_structure_notes_blueprint(blueprint, sections)

        # Build DNA
        dna = SongDNA(
            blueprint_id=blueprint.song_id,
            manual_project_id=None,
            sections=sections,
            global_energy_curve=energy_curve,
            global_tension_curve=tension_curve,
            dominant_mood=dominant_mood,
            genre_guess=genre_guess,
            structure_notes=structure_notes,
        )

        # Calculate HitScore
        score = self._calculate_hitscore_blueprint(blueprint, sections)

        # Generate insights
        commentary = self._generate_commentary(dna, score)
        risks = self._identify_risks(dna, score)
        opportunities = self._identify_opportunities(dna, score)

        return HitMakerAnalysis(
            dna=dna,
            score=score,
            commentary=commentary,
            risks=risks,
            opportunities=opportunities,
        )

    def analyze_manual_project(self, project: ManualProjectModel) -> HitMakerAnalysis:
        """Analyze a Manual Creator project."""

        # Extract section-level analysis from patterns
        sections = self._analyze_manual_sections(project)

        # Build energy/tension curves
        energy_curve = [s.energy for s in sections]
        tension_curve = [s.tension for s in sections]

        # Determine mood and genre
        dominant_mood = self._infer_mood_from_project(project)
        genre_guess = self._infer_genre_from_project(project)

        # Generate structure notes
        structure_notes = self._generate_structure_notes_manual(project, sections)

        # Build DNA
        dna = SongDNA(
            blueprint_id=None,
            manual_project_id=project.id,
            sections=sections,
            global_energy_curve=energy_curve,
            global_tension_curve=tension_curve,
            dominant_mood=dominant_mood,
            genre_guess=genre_guess,
            structure_notes=structure_notes,
        )

        # Calculate HitScore
        score = self._calculate_hitscore_manual(project, sections)

        # Generate insights
        commentary = self._generate_commentary(dna, score)
        risks = self._identify_risks(dna, score)
        opportunities = self._identify_opportunities(dna, score)

        return HitMakerAnalysis(
            dna=dna,
            score=score,
            commentary=commentary,
            risks=risks,
            opportunities=opportunities,
        )

    def apply_influences_to_blueprint(
        self,
        blueprint: SongBlueprintResponse,
        influences: list[InfluenceDescriptor],
        target_mood: Optional[str] = None,
        target_genre: Optional[str] = None,
    ) -> HitMakerInfluenceResponse:
        """Apply artistic influences to adjust a blueprint."""

        # Analyze current state
        current_analysis = self.analyze_blueprint(blueprint)
        adjusted_dna = current_analysis.dna

        # Modify DNA based on influences
        if target_mood:
            adjusted_dna.dominant_mood = target_mood
        if target_genre:
            adjusted_dna.genre_guess = target_genre

        # Adjust energy curves based on influences
        for influence in influences:
            if "weeknd" in influence.name.lower():
                # Apply dark, moody R&B characteristics
                adjusted_dna.global_energy_curve = [
                    e * (0.7 + 0.3 * (1 - influence.weight)) for e in adjusted_dna.global_energy_curve
                ]
            elif "billie" in influence.name.lower() or "eilish" in influence.name.lower():
                # Apply minimalist, tension-based characteristics
                adjusted_dna.global_tension_curve = [
                    t * (1.0 + 0.3 * influence.weight) for t in adjusted_dna.global_tension_curve
                ]

        # Generate creative suggestions
        hook_suggestions = self._generate_hook_suggestions(blueprint, influences)
        chorus_rewrite_ideas = self._generate_chorus_ideas(blueprint, influences)
        structure_suggestions = self._generate_structure_suggestions(current_analysis.dna, influences)
        instrumentation_ideas = self._generate_instrumentation_ideas(influences, target_genre)
        vocal_style_notes = self._generate_vocal_style_notes(influences)

        return HitMakerInfluenceResponse(
            adjusted_dna=adjusted_dna,
            hook_suggestions=hook_suggestions,
            chorus_rewrite_ideas=chorus_rewrite_ideas,
            structure_suggestions=structure_suggestions,
            instrumentation_ideas=instrumentation_ideas,
            vocal_style_notes=vocal_style_notes,
        )

    def apply_influences_to_project(
        self,
        project: ManualProjectModel,
        influences: list[InfluenceDescriptor],
        target_mood: Optional[str] = None,
        target_genre: Optional[str] = None,
    ) -> HitMakerInfluenceResponse:
        """Apply artistic influences to adjust a manual project."""

        # Analyze current state
        current_analysis = self.analyze_manual_project(project)
        adjusted_dna = current_analysis.dna

        # Modify DNA based on influences
        if target_mood:
            adjusted_dna.dominant_mood = target_mood
        if target_genre:
            adjusted_dna.genre_guess = target_genre

        # Generate suggestions (similar to blueprint but adapted for manual)
        hook_suggestions = self._generate_hook_suggestions_manual(project, influences)
        chorus_rewrite_ideas = self._generate_chorus_ideas_manual(project, influences)
        structure_suggestions = self._generate_structure_suggestions(current_analysis.dna, influences)
        instrumentation_ideas = self._generate_instrumentation_ideas(influences, target_genre)
        vocal_style_notes = self._generate_vocal_style_notes(influences)

        return HitMakerInfluenceResponse(
            adjusted_dna=adjusted_dna,
            hook_suggestions=hook_suggestions,
            chorus_rewrite_ideas=chorus_rewrite_ideas,
            structure_suggestions=structure_suggestions,
            instrumentation_ideas=instrumentation_ideas,
            vocal_style_notes=vocal_style_notes,
        )

    # ========== Helper Methods - Blueprint Analysis ==========

    def _analyze_blueprint_sections(self, blueprint: SongBlueprintResponse) -> list[SectionEnergy]:
        """Extract section energy/tension from blueprint."""
        sections = []

        for idx, section in enumerate(blueprint.sections):
            # Calculate energy based on section type and BPM
            energy = self._calculate_section_energy(section.name, blueprint.bpm)

            # Calculate tension based on position (builds toward middle/end)
            tension = self._calculate_section_tension(idx, len(blueprint.sections), section.name)

            # Hook density higher for chorus
            hook_density = 0.8 if "chorus" in section.name.lower() else 0.4

            sections.append(SectionEnergy(
                name=section.name,
                position_index=idx,
                energy=energy,
                tension=tension,
                hook_density=hook_density,
                notes=f"{section.bars} bars, {section.description}" if hasattr(section, 'description') else None,
            ))

        return sections

    def _calculate_section_energy(self, section_name: str, bpm: int) -> float:
        """Calculate energy level for a section."""
        base_energy = 0.5

        # Section type modifiers
        name_lower = section_name.lower()
        if "intro" in name_lower:
            base_energy = 0.3
        elif "verse" in name_lower:
            base_energy = 0.5
        elif "chorus" in name_lower:
            base_energy = 0.8
        elif "bridge" in name_lower:
            base_energy = 0.6
        elif "outro" in name_lower:
            base_energy = 0.4
        elif "drop" in name_lower:
            base_energy = 0.9

        # BPM modifier
        if bpm > 140:
            base_energy *= 1.2
        elif bpm < 90:
            base_energy *= 0.8

        return min(1.0, max(0.0, base_energy))

    def _calculate_section_tension(self, index: int, total: int, section_name: str) -> float:
        """Calculate tension for a section based on position."""
        # Natural arc: builds to 60-70% through song
        if total == 0:
            return 0.5

        position_ratio = index / total

        # Parabolic tension curve peaking at 0.65
        base_tension = 1.0 - abs(position_ratio - 0.65) * 1.5
        base_tension = max(0.1, min(0.9, base_tension))

        # Bridge typically has high tension
        if "bridge" in section_name.lower():
            base_tension = min(1.0, base_tension * 1.3)

        return base_tension

    def _infer_mood_from_blueprint(self, blueprint: SongBlueprintResponse) -> str:
        """Infer dominant mood from blueprint."""
        # Check genre and mood fields
        mood = blueprint.mood.lower() if hasattr(blueprint, 'mood') else "energetic"

        # Analyze lyrics for emotional content
        all_lyrics = " ".join([s.lyrics for s in blueprint.sections if hasattr(s, 'lyrics')])

        positive_count = sum(all_lyrics.lower().count(word) for word in self.EMOTIONAL_KEYWORDS["positive"])
        negative_count = sum(all_lyrics.lower().count(word) for word in self.EMOTIONAL_KEYWORDS["negative"])

        if negative_count > positive_count:
            return "melancholic"
        elif positive_count > negative_count:
            return "uplifting"

        return mood

    def _infer_genre_from_blueprint(self, blueprint: SongBlueprintResponse) -> str:
        """Infer genre from blueprint."""
        if hasattr(blueprint, 'genre'):
            return blueprint.genre.lower()

        # Use BPM to guess
        bpm = blueprint.bpm
        for genre, (min_bpm, max_bpm) in self.GENRE_TEMPO_RANGES.items():
            if min_bpm <= bpm <= max_bpm:
                return genre

        return "pop"  # default

    def _generate_structure_notes_blueprint(
        self,
        blueprint: SongBlueprintResponse,
        sections: list[SectionEnergy]
    ) -> list[str]:
        """Generate structural observations."""
        notes = []

        # Check for chorus
        has_chorus = any("chorus" in s.name.lower() for s in sections)
        if not has_chorus:
            notes.append("No clear chorus section detected - consider adding one for catchiness")

        # Check for variety
        if len(sections) < 3:
            notes.append("Simple structure - consider adding more variety (bridge, pre-chorus)")

        # Check energy arc
        if len(sections) >= 3:
            mid_energy = sections[len(sections)//2].energy
            end_energy = sections[-1].energy
            if mid_energy < 0.5:
                notes.append("Energy dips in the middle - consider a lift or drop")
            if end_energy > 0.7:
                notes.append("High energy ending - good for exciting finales")

        return notes

    def _calculate_hitscore_blueprint(
        self,
        blueprint: SongBlueprintResponse,
        sections: list[SectionEnergy]
    ) -> HitScoreBreakdown:
        """Calculate hit potential scores for blueprint."""

        # Hook strength: based on chorus presence and energy
        has_chorus = any("chorus" in s.name.lower() for s in sections)
        chorus_energy = max([s.energy for s in sections if "chorus" in s.name.lower()], default=0.5)
        hook_strength = (70.0 if has_chorus else 40.0) + (chorus_energy * 20.0)

        # Structure: variety and clear arc
        section_variety = min(100.0, len(sections) * 15.0)
        energy_variance = self._calculate_variance([s.energy for s in sections])
        structure = (section_variety * 0.6) + (energy_variance * 40.0)

        # Lyrics emotion: based on keyword analysis
        all_lyrics = " ".join([s.lyrics for s in blueprint.sections if hasattr(s, 'lyrics')])
        lyrics_emotion = min(100.0, 60.0 + len(all_lyrics.split()) * 0.5)

        # Genre fit: based on BPM matching
        genre_fit = 75.0  # baseline
        bpm = blueprint.bpm
        genre_lower = blueprint.genre.lower() if hasattr(blueprint, 'genre') else ""
        if genre_lower in self.GENRE_TEMPO_RANGES:
            min_bpm, max_bpm = self.GENRE_TEMPO_RANGES[genre_lower]
            if min_bpm <= bpm <= max_bpm:
                genre_fit = 85.0

        # Originality: penalize very predictable structures
        originality = 65.0
        if len(sections) > 5:
            originality += 15.0
        if energy_variance > 0.15:
            originality += 10.0

        # Replay value: balance of repetition and variety
        replay_value = (hook_strength * 0.4) + (structure * 0.3) + (originality * 0.3)

        # Overall: weighted average
        overall = (
            hook_strength * 0.25 +
            structure * 0.20 +
            lyrics_emotion * 0.15 +
            genre_fit * 0.15 +
            originality * 0.10 +
            replay_value * 0.15
        )

        return HitScoreBreakdown(
            overall=min(100.0, overall),
            hook_strength=min(100.0, hook_strength),
            structure=min(100.0, structure),
            lyrics_emotion=min(100.0, lyrics_emotion),
            genre_fit=min(100.0, genre_fit),
            originality=min(100.0, originality),
            replay_value=min(100.0, replay_value),
        )

    # ========== Helper Methods - Manual Project Analysis ==========

    def _analyze_manual_sections(self, project: ManualProjectModel) -> list[SectionEnergy]:
        """Analyze manual project by dividing into sections."""
        # Divide the 16-bar grid into 4-bar sections
        sections = []
        max_bar = self._get_max_bar(project)
        section_size = 4

        for start_bar in range(0, max_bar, section_size):
            end_bar = min(start_bar + section_size, max_bar)

            # Calculate energy based on pattern density in this range
            energy = self._calculate_manual_section_energy(project, start_bar, end_bar)

            # Calculate tension (builds toward middle)
            section_idx = start_bar // section_size
            total_sections = (max_bar + section_size - 1) // section_size
            tension = self._calculate_section_tension(section_idx, total_sections, "")

            # Hook density based on energy and repetition
            hook_density = energy * 0.7

            sections.append(SectionEnergy(
                name=f"Section {section_idx + 1} (bars {start_bar}-{end_bar})",
                position_index=section_idx,
                energy=energy,
                tension=tension,
                hook_density=hook_density,
                notes=f"Bars {start_bar}-{end_bar}",
            ))

        return sections if sections else [SectionEnergy(
            name="Full Project",
            position_index=0,
            energy=0.5,
            tension=0.5,
            hook_density=0.4,
            notes="Empty or minimal project",
        )]

    def _calculate_manual_section_energy(
        self,
        project: ManualProjectModel,
        start_bar: int,
        end_bar: int
    ) -> float:
        """Calculate energy for a bar range in manual project."""
        # Count patterns and notes in this range
        pattern_count = 0
        total_notes = 0
        has_drums = False
        has_lead = False

        for track in project.tracks:
            for pattern in track.patterns:
                # Check if pattern overlaps with this range
                pattern_end = pattern.start_bar + pattern.length_bars
                if pattern.start_bar < end_bar and pattern_end > start_bar:
                    pattern_count += 1
                    total_notes += len(pattern.notes)

                    if track.instrument_type == "drums":
                        has_drums = True
                    elif track.instrument_type in ["lead", "chords"]:
                        has_lead = True

        # Base energy from pattern density
        base_energy = min(1.0, pattern_count * 0.15)

        # Boost if both drums and melodic elements present
        if has_drums and has_lead:
            base_energy = min(1.0, base_energy * 1.3)

        # Boost based on note density
        avg_notes_per_pattern = total_notes / max(1, pattern_count)
        note_boost = min(0.3, avg_notes_per_pattern * 0.02)

        return min(1.0, base_energy + note_boost)

    def _get_max_bar(self, project: ManualProjectModel) -> int:
        """Get the last bar position in the project."""
        max_bar = 16  # default

        for track in project.tracks:
            for pattern in track.patterns:
                pattern_end = pattern.start_bar + pattern.length_bars
                max_bar = max(max_bar, pattern_end)

        return max_bar

    def _infer_mood_from_project(self, project: ManualProjectModel) -> str:
        """Infer mood from manual project."""
        # Use tempo to guess mood
        bpm = project.tempo_bpm

        if bpm < 80:
            return "melancholic"
        elif bpm < 100:
            return "chill"
        elif bpm < 130:
            return "energetic"
        else:
            return "intense"

    def _infer_genre_from_project(self, project: ManualProjectModel) -> str:
        """Infer genre from manual project."""
        bpm = project.tempo_bpm

        # Check track types
        track_types = {track.instrument_type for track in project.tracks}

        # Simple heuristics
        if "drums" in track_types and bpm > 130:
            return "edm"
        elif bpm < 90:
            return "ballad"
        elif 80 <= bpm <= 110:
            return "hiphop"
        else:
            return "pop"

    def _generate_structure_notes_manual(
        self,
        project: ManualProjectModel,
        sections: list[SectionEnergy]
    ) -> list[str]:
        """Generate structural observations for manual project."""
        notes = []

        # Check for sparse sections
        sparse_sections = [s for s in sections if s.energy < 0.3]
        if len(sparse_sections) > len(sections) // 2:
            notes.append("Many sparse sections - consider adding more patterns for energy")

        # Check for variety
        if len(sections) >= 3:
            energy_range = max([s.energy for s in sections]) - min([s.energy for s in sections])
            if energy_range < 0.3:
                notes.append("Energy levels are quite flat - add dynamic contrast")

        # Check track diversity
        track_types = {track.instrument_type for track in project.tracks}
        if len(track_types) < 3:
            notes.append(f"Limited instrumentation ({len(track_types)} track types) - consider adding more variety")

        return notes

    def _calculate_hitscore_manual(
        self,
        project: ManualProjectModel,
        sections: list[SectionEnergy]
    ) -> HitScoreBreakdown:
        """Calculate hit potential scores for manual project."""

        # Hook strength: based on pattern repetition and energy
        max_energy = max([s.energy for s in sections], default=0.5)
        hook_strength = 50.0 + (max_energy * 40.0)

        # Structure: variety in sections
        energy_variance = self._calculate_variance([s.energy for s in sections])
        structure = 50.0 + (energy_variance * 40.0) + (len(sections) * 5.0)

        # Lyrics emotion: N/A for manual, use baseline
        lyrics_emotion = 60.0

        # Genre fit: based on BPM
        genre_fit = 70.0

        # Originality: based on track diversity and patterns
        track_count = len(project.tracks)
        pattern_count = sum(len(track.patterns) for track in project.tracks)
        originality = min(100.0, 50.0 + (track_count * 5.0) + (pattern_count * 2.0))

        # Replay value
        replay_value = (hook_strength * 0.4) + (structure * 0.4) + (originality * 0.2)

        # Overall
        overall = (
            hook_strength * 0.25 +
            structure * 0.25 +
            lyrics_emotion * 0.10 +
            genre_fit * 0.15 +
            originality * 0.10 +
            replay_value * 0.15
        )

        return HitScoreBreakdown(
            overall=min(100.0, overall),
            hook_strength=min(100.0, hook_strength),
            structure=min(100.0, structure),
            lyrics_emotion=lyrics_emotion,
            genre_fit=genre_fit,
            originality=min(100.0, originality),
            replay_value=min(100.0, replay_value),
        )

    # ========== Helper Methods - Common ==========

    def _calculate_variance(self, values: list[float]) -> float:
        """Calculate variance of a list of values."""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return min(1.0, variance ** 0.5)  # Return standard deviation, capped at 1.0

    def _generate_commentary(self, dna: SongDNA, score: HitScoreBreakdown) -> list[str]:
        """Generate commentary based on analysis."""
        commentary = []

        commentary.append(f"Overall hit potential: {score.overall:.1f}/100")
        commentary.append(f"Dominant mood is {dna.dominant_mood}, fitting {dna.genre_guess} genre")

        if score.hook_strength > 75:
            commentary.append("Strong hooks - highly memorable")
        elif score.hook_strength < 50:
            commentary.append("Hooks need strengthening - focus on catchy melodies")

        if score.structure > 75:
            commentary.append("Well-structured with good dynamic flow")
        elif score.structure < 50:
            commentary.append("Structure feels repetitive or disjointed")

        return commentary

    def _identify_risks(self, dna: SongDNA, score: HitScoreBreakdown) -> list[str]:
        """Identify potential weaknesses."""
        risks = []

        if score.hook_strength < 60:
            risks.append("Weak hooks may limit radio/streaming appeal")

        if score.structure < 55:
            risks.append("Structural issues may cause listener drop-off")

        if score.originality < 50:
            risks.append("May sound too generic - needs unique elements")

        # Check for flat energy
        if len(dna.global_energy_curve) >= 3:
            energy_range = max(dna.global_energy_curve) - min(dna.global_energy_curve)
            if energy_range < 0.2:
                risks.append("Flat energy curve - needs more dynamic contrast")

        return risks if risks else ["No major risks identified"]

    def _identify_opportunities(self, dna: SongDNA, score: HitScoreBreakdown) -> list[str]:
        """Identify strengths to amplify."""
        opportunities = []

        if score.hook_strength > 70:
            opportunities.append("Strong hooks - perfect for playlists and TikTok")

        if score.originality > 70:
            opportunities.append("Unique sound - could start trends")

        if score.structure > 70:
            opportunities.append("Great flow - ideal for full album listens")

        if "energetic" in dna.dominant_mood or "intense" in dna.dominant_mood:
            opportunities.append("High energy - great for workout/party playlists")

        return opportunities if opportunities else ["Solid foundation - room for polish"]

    # ========== Influence Application ==========

    def _generate_hook_suggestions(
        self,
        blueprint: SongBlueprintResponse,
        influences: list[InfluenceDescriptor]
    ) -> list[str]:
        """Generate hook suggestions based on influences."""
        suggestions = []

        for influence in influences:
            name_lower = influence.name.lower()

            if "weeknd" in name_lower:
                suggestions.append("Use falsetto runs on sustained notes")
                suggestions.append("Layer dark, atmospheric vocal ad-libs")
            elif "billie" in name_lower or "eilish" in name_lower:
                suggestions.append("Whispered, intimate delivery in verses")
                suggestions.append("Minimal, bass-heavy production")
            elif "drake" in name_lower:
                suggestions.append("Melodic rap verses with sung hooks")
                suggestions.append("Introspective, emotional lyrics")
            else:
                suggestions.append(f"Incorporate {influence.name}-inspired melodic motifs")

        return suggestions if suggestions else ["Focus on memorable, repeating melodic phrases"]

    def _generate_chorus_ideas(
        self,
        blueprint: SongBlueprintResponse,
        influences: list[InfluenceDescriptor]
    ) -> list[str]:
        """Generate chorus rewrite ideas."""
        ideas = []

        # Get existing chorus if any
        chorus_sections = [s for s in blueprint.sections if "chorus" in s.name.lower()]

        for influence in influences:
            name_lower = influence.name.lower()

            if "taylor" in name_lower or "swift" in name_lower:
                ideas.append("Use storytelling bridge that reveals emotional climax")
                ideas.append("Add personal, confessional details in pre-chorus")
            elif "weeknd" in name_lower:
                ideas.append("Build tension with dark, moody pre-chorus")
                ideas.append("Release in soaring, melismatic chorus")
            else:
                ideas.append(f"Apply {influence.name}'s signature melodic patterns")

        ideas.append("Repeat chorus title 2-3 times for memorability")
        ideas.append("Simplify chord progression for maximum impact")

        return ideas

    def _generate_structure_suggestions(
        self,
        dna: SongDNA,
        influences: list[InfluenceDescriptor]
    ) -> list[str]:
        """Generate structural modification suggestions."""
        suggestions = []

        # Check current structure
        if len(dna.sections) < 4:
            suggestions.append("Consider adding a bridge for variety")

        # Analyze energy curve
        if len(dna.global_energy_curve) >= 3:
            early_energy = dna.global_energy_curve[0]
            mid_energy = sum(dna.global_energy_curve) / len(dna.global_energy_curve)

            if early_energy > 0.7:
                suggestions.append("High energy intro - consider slower build for contrast")
            if mid_energy < 0.5:
                suggestions.append("Add a lift or drop at the 50% mark to maintain interest")

        for influence in influences:
            if "pop" in dna.genre_guess:
                suggestions.append("Move chorus earlier (within first 30 seconds)")

        return suggestions if suggestions else ["Current structure is well-balanced"]

    def _generate_instrumentation_ideas(
        self,
        influences: list[InfluenceDescriptor],
        target_genre: Optional[str] = None
    ) -> list[str]:
        """Generate instrumentation suggestions."""
        ideas = []

        for influence in influences:
            name_lower = influence.name.lower()

            if "billie" in name_lower or "eilish" in name_lower:
                ideas.append("Minimal production: sub-bass, sparse beats, intimate vocals")
            elif "weeknd" in name_lower:
                ideas.append("80s-inspired synths with modern R&B drums")
                ideas.append("Heavy reverb and atmospheric pads")
            elif "drake" in name_lower:
                ideas.append("Trap-influenced hi-hats with melodic piano")
            elif "tame" in name_lower or "impala" in name_lower:
                ideas.append("Psychedelic synths, phaser effects, vintage drum machines")

        if target_genre:
            if "edm" in target_genre.lower():
                ideas.append("Add sweeping filters and build-ups before drops")
            elif "rock" in target_genre.lower():
                ideas.append("Layer distorted guitars with driving drums")

        return ideas if ideas else ["Focus on genre-appropriate instrumentation"]

    def _generate_vocal_style_notes(self, influences: list[InfluenceDescriptor]) -> list[str]:
        """Generate vocal delivery suggestions."""
        notes = []

        for influence in influences:
            name_lower = influence.name.lower()

            if "billie" in name_lower or "eilish" in name_lower:
                notes.append("Breathy, close-mic'd delivery in verses")
                notes.append("Occasional powerful belts for contrast")
            elif "weeknd" in name_lower:
                notes.append("Falsetto runs and melismatic phrases")
                notes.append("Dark, emotional tone throughout")
            elif "adele" in name_lower:
                notes.append("Power vocals with emotional vulnerability")
                notes.append("Strong belting in chorus")
            else:
                notes.append(f"Study {influence.name}'s vocal phrasing and dynamics")

        return notes if notes else ["Match vocal intensity to energy curve"]

    def _generate_hook_suggestions_manual(
        self,
        project: ManualProjectModel,
        influences: list[InfluenceDescriptor]
    ) -> list[str]:
        """Generate hook suggestions for manual project."""
        suggestions = []

        suggestions.append("Add a catchy melodic riff in the lead track")
        suggestions.append("Create a memorable rhythmic pattern in drums")

        for influence in influences:
            suggestions.append(f"Incorporate {influence.name}-style melodic patterns")

        return suggestions

    def _generate_chorus_ideas_manual(
        self,
        project: ManualProjectModel,
        influences: list[InfluenceDescriptor]
    ) -> list[str]:
        """Generate chorus ideas for manual project."""
        ideas = []

        ideas.append("Increase pattern density in the chorus section")
        ideas.append("Layer chords with lead melody for fuller sound")
        ideas.append("Add rhythmic variation in drums during chorus")

        return ideas
