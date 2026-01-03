"""
Patient Context Builder Service

Wraps existing app/db query functions to provide LLM-friendly text summaries
of patient clinical data across all domains.

This service:
1. Queries PostgreSQL via existing app/db functions
2. Formats structured data (dicts/lists) as natural language text
3. Provides both individual domain summaries and comprehensive overviews
4. Handles missing data gracefully (returns "None on record" messages)

Design Reference: docs/spec/ai-insight-design.md Section 7.2

Implementation Note:
- Uses synchronous functions (matching existing app/db pattern)
- Future consideration: Refactor to async/await for concurrent queries
"""

from typing import Dict, List, Any
import logging

# Import existing database query functions
from app.db.patient import get_patient_demographics
from app.db.medications import get_patient_medications
from app.db.vitals import get_recent_vitals
from app.db.patient_allergies import get_patient_allergies
from app.db.encounters import get_recent_encounters
from app.db.notes import get_recent_notes_for_ai

logger = logging.getLogger(__name__)


class PatientContextBuilder:
    """
    Builds LLM-friendly context from existing med-z1 database services.

    Wraps existing data access layer without duplicating logic.
    Formats clinical data as natural language text suitable for LLM consumption.

    Attributes:
        icn: Patient ICN (Integrated Care Number)

    Example:
        >>> builder = PatientContextBuilder("ICN100010")
        >>> demographics = builder.get_demographics_summary()
        >>> print(demographics)
        "45-year-old male veteran, service-connected disability 70%..."

        >>> full_summary = builder.build_comprehensive_summary()
        >>> print(full_summary)
        "PATIENT DEMOGRAPHICS\n45-year-old male veteran...\n\nMEDICATIONS..."
    """

    def __init__(self, patient_icn: str):
        """
        Initialize PatientContextBuilder for a specific patient.

        Args:
            patient_icn: Patient ICN (Integrated Care Number)
        """
        self.icn = patient_icn
        logger.debug(f"Initialized PatientContextBuilder for {patient_icn}")

    def get_demographics_summary(self) -> str:
        """
        Get patient demographics formatted as natural language text.

        Returns:
            Natural language demographics summary

        Example:
            "45-year-old male veteran, service-connected disability 70%
             Primary care: Alexandria VA Medical Center
             Address: Alexandria, VA 22314"
        """
        demo = get_patient_demographics(self.icn)

        if not demo:
            return "No demographic data on record"

        # Build age/gender/veteran status line
        age = demo.get('age', 'unknown age')
        sex = demo.get('sex', 'unknown').lower()
        text = f"{age}-year-old {sex} veteran"

        # Add service-connected percentage if available
        sc_pct = demo.get('service_connected_percent')
        if sc_pct is not None:
            text += f", service-connected disability {int(sc_pct)}%"

        # Add primary care station
        station_name = demo.get('primary_station_name')
        if station_name:
            text += f"\nPrimary care: {station_name}"

        # Add address (city, state, zip)
        city = demo.get('address_city')
        state = demo.get('address_state')
        zip_code = demo.get('address_zip')
        if city and state:
            address_parts = [city, state]
            if zip_code:
                address_parts.append(zip_code)
            text += f"\nAddress: {', '.join(address_parts)}"

        return text

    def get_medication_summary(self) -> str:
        """
        Get current medications formatted as natural language text.

        Shows up to 10 most recent medications with drug name, sig, and start date.

        Returns:
            Natural language medication summary

        Example:
            "Currently on 7 active medications:
             - GABAPENTIN 300MG CAP (oral, 3x daily), started 2024-01-15
             - ALPRAZOLAM 0.5MG TAB (oral, as needed), started 2024-02-20
             ..."
        """
        # Get up to 10 most recent medications (limit for LLM context)
        meds = get_patient_medications(self.icn, limit=10)

        if not meds:
            return "No active medications on record"

        total_count = len(meds)
        text = f"Currently on {total_count} active medication{'s' if total_count != 1 else ''}:\n"

        # Format each medication
        for med in meds[:10]:  # Show max 10 for brevity
            # Support multiple drug name fields
            drug_name = (
                med.get('drug_name_national') or
                med.get('drug_name_local') or
                med.get('drug_name') or
                med.get('generic_name') or
                'Unknown medication'
            )

            # Add sig (directions) if available
            sig = med.get('sig')
            if sig:
                text += f"- {drug_name} ({sig})"
            else:
                text += f"- {drug_name}"

            # Add start date if available
            start_date = med.get('issue_date') or med.get('start_date')
            if start_date:
                text += f", started {start_date}"

            text += "\n"

        # Note if there are more medications not shown
        if total_count > 10:
            text += f"... and {total_count - 10} more medication{'s' if total_count - 10 != 1 else ''}\n"

        return text.strip()

    def get_vitals_summary(self) -> str:
        """
        Get recent vital signs formatted as natural language text.

        Shows most recent vital sign measurements (last 7 days).

        Returns:
            Natural language vitals summary

        Example:
            "Latest reading (2025-12-28):
             - BP: 128/82 mmHg
             - HR: 72 bpm
             - Temp: 98.4°F
             - Weight: 185 lbs"
        """
        vitals_data = get_recent_vitals(self.icn)

        if not vitals_data or not vitals_data.get('vitals'):
            return "No recent vitals recorded (last 7 days)"

        vitals_list = vitals_data['vitals']
        if not vitals_list:
            return "No recent vitals recorded (last 7 days)"

        # Get most recent vital sign
        latest = vitals_list[0]  # Assumed to be sorted by date descending

        taken_date = latest.get('vital_taken_date', 'unknown date')
        text = f"Latest reading ({taken_date}):\n"

        # Blood pressure
        systolic = latest.get('systolic')
        diastolic = latest.get('diastolic')
        if systolic and diastolic:
            text += f"- BP: {systolic}/{diastolic} mmHg\n"

        # Heart rate
        pulse = latest.get('pulse')
        if pulse:
            text += f"- HR: {pulse} bpm\n"

        # Temperature
        temp = latest.get('temperature')
        if temp:
            text += f"- Temp: {temp}°F\n"

        # Weight
        weight = latest.get('weight')
        if weight:
            text += f"- Weight: {weight} lbs\n"

        # Height
        height = latest.get('height')
        if height:
            text += f"- Height: {height} inches\n"

        return text.strip()

    def get_allergies_summary(self) -> str:
        """
        Get patient allergies formatted as natural language text.

        Returns:
            Natural language allergies summary

        Example:
            "Known allergies:
             - PENICILLIN (reaction: rash, severity: moderate)
             - LATEX (reaction: hives, severity: mild)"
        """
        allergies = get_patient_allergies(self.icn)

        if not allergies:
            return "No known allergies on record"

        text = "Known allergies:\n"

        for allergy in allergies:
            allergen = allergy.get('allergen_name', 'Unknown allergen')
            text += f"- {allergen}"

            # Add reaction type if available
            reaction = allergy.get('reaction_type')
            if reaction:
                text += f" (reaction: {reaction.lower()}"

                # Add severity if available
                severity = allergy.get('severity')
                if severity:
                    text += f", severity: {severity.lower()}"

                text += ")"

            text += "\n"

        return text.strip()

    def get_encounters_summary(self) -> str:
        """
        Get recent encounters formatted as natural language text.

        Shows last 5 encounters (or fewer if not available).

        Returns:
            Natural language encounters summary

        Example:
            "Recent encounters (last 90 days, 3 shown):
             - Primary Care Visit on 2025-12-15 (Alexandria VAMC)
             - Mental Health Follow-up on 2025-11-28 (Telehealth)
             - Lab Draw on 2025-11-10 (Alexandria VAMC)"
        """
        encounters = get_recent_encounters(self.icn, limit=5)

        if not encounters:
            return "No recent encounters on record (last 90 days)"

        count = len(encounters)
        text = f"Recent encounters (last 90 days, {count} shown):\n"

        for enc in encounters:
            # Encounter type or category (admission_category from PostgreSQL)
            enc_type = enc.get('admission_category', 'Unknown encounter type')

            # Date (admit_datetime from PostgreSQL)
            enc_date_raw = enc.get('admit_datetime')
            if enc_date_raw:
                # Extract date part from datetime (format: "2025-11-30 08:00:00" -> "2025-11-30")
                enc_date = str(enc_date_raw).split(' ')[0]
            else:
                enc_date = 'unknown date'

            text += f"- {enc_type} on {enc_date}"

            # Location (facility_name from PostgreSQL)
            location = enc.get('facility_name')
            if location:
                text += f" ({location})"

            text += "\n"

        return text.strip()

    def get_notes_summary(self) -> str:
        """
        Get recent clinical notes formatted as natural language text.

        Shows up to 3 most recent notes with preview text (500 chars).
        Includes note type, date, author, facility, and clinical preview.

        Returns:
            Natural language notes summary

        Example:
            "Recent Clinical Notes (Last 3):
             - 2025-12-28 Progress Note by Dr. Smith (VA Alexandria):
               'SUBJECTIVE: Patient presents for follow-up of hypertension and diabetes...'
             - 2025-12-15 Cardiology Consult by Dr. Johnson (VA Alexandria):
               'REASON FOR CONSULT: Evaluate for coronary artery disease...'
             - 2025-11-20 Discharge Summary by Dr. Williams (VA Alexandria):
               'ADMISSION DATE: 11/17/2025. DISCHARGE DATE: 11/20/2025...'"
        """
        from config import AI_NOTES_SUMMARY_LIMIT, AI_NOTES_PREVIEW_LENGTH

        notes = get_recent_notes_for_ai(
            self.icn,
            limit=AI_NOTES_SUMMARY_LIMIT,
            preview_length=AI_NOTES_PREVIEW_LENGTH
        )

        if not notes:
            return "No recent clinical notes on record (last 90 days)"

        count = len(notes)
        text = f"Recent Clinical Notes (Last {count}):\n"

        for note in notes:
            # Date and note type
            note_date = note.get('reference_datetime', 'unknown date')
            if note_date and ' ' in note_date:
                # Extract date part from datetime (format: "2025-12-28 10:30:00" -> "2025-12-28")
                note_date = note_date.split(' ')[0]

            note_type = note.get('document_class', 'Clinical Note')
            text += f"- {note_date} {note_type}"

            # Author
            author = note.get('author_name')
            if author:
                text += f" by {author}"

            # Facility
            facility = note.get('facility_name')
            if facility:
                text += f" ({facility})"

            text += ":\n"

            # Preview text (500 chars, captures SOAP opening)
            preview = note.get('text_preview')
            if preview:
                # Clean up preview text (remove extra whitespace, limit line breaks)
                preview_clean = ' '.join(preview.split())
                # Truncate if still too long and add ellipsis
                if len(preview_clean) > 500:
                    preview_clean = preview_clean[:497] + "..."
                text += f"  '{preview_clean}'\n"
            else:
                text += f"  (No text preview available)\n"

            text += "\n"

        return text.strip()

    def build_comprehensive_summary(self) -> str:
        """
        Build comprehensive patient summary combining all clinical domains.

        Queries all domains in sequence and formats as a multi-section summary
        suitable for LLM analysis.

        Returns:
            Comprehensive multi-section patient summary

        Example:
            "PATIENT DEMOGRAPHICS
             45-year-old male veteran...

             CURRENT MEDICATIONS (7 active)
             - GABAPENTIN 300MG CAP...

             RECENT VITALS (last 7 days)
             Latest reading...

             ALLERGIES
             Known allergies...

             RECENT ENCOUNTERS (last 90 days)
             Recent encounters...

             Data sources: PostgreSQL (demographics, medications, vitals, allergies, encounters)"
        """
        logger.info(f"Building comprehensive summary for patient {self.icn}")

        # Query all domains
        demographics = self.get_demographics_summary()
        medications = self.get_medication_summary()
        vitals = self.get_vitals_summary()
        allergies = self.get_allergies_summary()
        encounters = self.get_encounters_summary()
        notes = self.get_notes_summary()  # Phase 4: Add clinical notes

        # Build multi-section summary
        summary = f"""PATIENT DEMOGRAPHICS
{demographics}

CURRENT MEDICATIONS
{medications}

RECENT VITALS (last 7 days)
{vitals}

ALLERGIES
{allergies}

RECENT ENCOUNTERS (last 90 days)
{encounters}

RECENT CLINICAL NOTES (last 90 days)
{notes}

Data sources: PostgreSQL (demographics, medications, vitals, allergies, encounters, clinical_notes)"""

        logger.info(f"Comprehensive summary built for patient {self.icn} ({len(summary)} characters)")

        return summary
