# ---------------------------------------------------------------------
# app/services/realtime_overlay.py
# ---------------------------------------------------------------------
# Real-Time Data Overlay Service
# Merges historical PostgreSQL data (T-1 and earlier) with real-time
# VistA RPC data (T-0, today) to provide unified patient vitals view.
# ---------------------------------------------------------------------

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def parse_fileman_datetime(fileman_str: str) -> Optional[datetime]:
    """
    Parse VistA FileMan date/time format to Python datetime.

    FileMan format: YYYMMDD.HHMM where YYY = year - 1700
    Example: 3241217.0930 = December 17, 2024 at 09:30

    Args:
        fileman_str: FileMan formatted date/time string

    Returns:
        Python datetime object or None if parsing fails
    """
    try:
        if not fileman_str or "." not in fileman_str:
            return None

        date_part, time_part = fileman_str.split(".")

        # Parse date: YYYMMDD
        yyy = int(date_part[:3])  # Years since 1700
        mm = int(date_part[3:5])  # Month
        dd = int(date_part[5:7])  # Day

        year = 1700 + yyy

        # Parse time: HHMM
        hh = int(time_part[:2])
        mi = int(time_part[2:4])

        return datetime(year, mm, dd, hh, mi)

    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to parse FileMan date '{fileman_str}': {e}")
        return None


def parse_vista_vitals(vista_response: str, site_sta3n: str) -> List[Dict[str, Any]]:
    """
    Parse VistA GMV LATEST VM response into standardized vital records.

    VistA format: Multi-line response, one vital per line
    Each line: TYPE^VALUE^UNITS^DATE_TIME^ENTERED_BY

    Args:
        vista_response: Raw VistA RPC response string
        site_sta3n: Site station number (e.g., "200", "500", "630")

    Returns:
        List of parsed vital dictionaries matching PostgreSQL schema
    """
    vitals = []

    if not vista_response or vista_response.startswith("-1^"):
        # Error response or no vitals
        return vitals

    lines = vista_response.strip().split("\n")

    for line in lines:
        if not line or "^" not in line:
            continue

        parts = line.split("^")
        if len(parts) != 5:
            logger.warning(f"Invalid Vista vital format: {line}")
            continue

        vital_type, value, units, fileman_datetime, entered_by = parts

        # Parse FileMan datetime to Python datetime
        taken_dt = parse_fileman_datetime(fileman_datetime)
        if not taken_dt:
            logger.warning(f"Skipping vital with invalid date: {line}")
            continue

        # Extract vital components
        vital_abbr = _get_vital_abbr(vital_type)
        numeric_value = _extract_numeric_value(value, vital_type)
        systolic = _extract_systolic(value, vital_type)
        diastolic = _extract_diastolic(value, vital_type)

        # Compute abnormal flag based on vital type and value
        abnormal_flag = _compute_abnormal_flag(vital_abbr, numeric_value, systolic, diastolic)

        # Create standardized vital record (matching PostgreSQL schema)
        vital = {
            "vital_id": None,  # No persistent ID for Vista data
            "patient_key": None,  # Will be set by caller
            "vital_sign_id": None,
            "vital_type": vital_type,
            "vital_abbr": vital_abbr,
            "taken_datetime": taken_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "entered_datetime": taken_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "result_value": value,
            "numeric_value": numeric_value,
            "systolic": systolic,
            "diastolic": diastolic,
            "metric_value": None,  # Could be computed if needed
            "unit_of_measure": units,
            "qualifiers": None,
            "location_id": None,
            "location_name": f"VistA Site {site_sta3n}",
            "location_type": "VistA",
            "entered_by": entered_by,
            "abnormal_flag": abnormal_flag,  # Computed based on clinical ranges
            "bmi": None,
            # Data source for badge display (template expects 'data_source' field)
            "data_source": "CDWWork",  # VistA vitals show as CDWWork (blue badge)
            # Vista-specific metadata for tracking
            "source": "vista",
            "source_site": site_sta3n,
            "is_realtime": True,
        }

        vitals.append(vital)

    return vitals


def _get_vital_abbr(vital_type: str) -> str:
    """Map vital type to standard abbreviation."""
    abbr_map = {
        "BLOOD PRESSURE": "BP",
        "TEMPERATURE": "T",
        "PULSE": "P",
        "RESPIRATION": "R",
        "PULSE OXIMETRY": "POX",
        "PAIN": "PN",
        "HEIGHT": "HT",
        "WEIGHT": "WT",
    }
    return abbr_map.get(vital_type, vital_type[:3].upper())


def _extract_numeric_value(value: str, vital_type: str) -> Optional[float]:
    """Extract numeric value from result string."""
    try:
        if vital_type == "BLOOD PRESSURE":
            # Extract systolic from "120/80"
            return float(value.split("/")[0])
        else:
            # Direct numeric conversion
            return float(value)
    except (ValueError, IndexError, AttributeError):
        return None


def _extract_systolic(value: str, vital_type: str) -> Optional[int]:
    """Extract systolic BP from value string."""
    if vital_type == "BLOOD PRESSURE":
        try:
            return int(value.split("/")[0])
        except (ValueError, IndexError, AttributeError):
            return None
    return None


def _extract_diastolic(value: str, vital_type: str) -> Optional[int]:
    """Extract diastolic BP from value string."""
    if vital_type == "BLOOD PRESSURE":
        try:
            return int(value.split("/")[1])
        except (ValueError, IndexError, AttributeError):
            return None
    return None


def _compute_abnormal_flag(vital_abbr: str, numeric_value: Optional[float],
                          systolic: Optional[int], diastolic: Optional[int]) -> Optional[str]:
    """
    Compute abnormal flag based on vital type and value.

    Reference Ranges:
    - BP Systolic: 100-139 (normal), 90-99 (low), 140-179 (high), <90 or ≥180 (critical)
    - BP Diastolic: 70-89 (normal), 60-69 (low), 90-119 (high), <60 or ≥120 (critical)
    - Temperature: 97.0-99.9°F (normal), 95.0-96.9 (low), 100.5-103.0 (high), <95.0 or >103.0 (critical)
    - Pulse: 60-100 (normal), 40-59 (low), 101-130 (high), <40 or >130 (critical)
    - Respiration: 12-20 (normal), 8-11 (low), 21-28 (high), <8 or >28 (critical)
    - Pulse Ox: ≥92% (normal), 88-91 (low), <88 (critical)
    - Pain: 0-3 (normal), 4-7 (high), 8-10 (critical)

    Returns: 'NORMAL', 'LOW', 'HIGH', 'CRITICAL', or None
    """
    if vital_abbr == "BP":
        # Check both systolic and diastolic
        if systolic is None or diastolic is None:
            return None

        # Critical
        if systolic < 90 or systolic >= 180 or diastolic < 60 or diastolic >= 120:
            return "CRITICAL"
        # High
        elif systolic >= 140 or diastolic >= 90:
            return "HIGH"
        # Low
        elif systolic < 100 or diastolic < 70:
            return "LOW"
        # Normal
        else:
            return "NORMAL"

    elif vital_abbr == "T":
        if numeric_value is None:
            return None
        # Assume Fahrenheit (temperature should be in F)
        if numeric_value < 95.0 or numeric_value > 103.0:
            return "CRITICAL"
        elif numeric_value >= 100.5:
            return "HIGH"
        elif numeric_value < 97.0:
            return "LOW"
        else:
            return "NORMAL"

    elif vital_abbr == "P":
        if numeric_value is None:
            return None
        if numeric_value < 40 or numeric_value > 130:
            return "CRITICAL"
        elif numeric_value > 100:
            return "HIGH"
        elif numeric_value < 60:
            return "LOW"
        else:
            return "NORMAL"

    elif vital_abbr == "R":
        if numeric_value is None:
            return None
        if numeric_value < 8 or numeric_value > 28:
            return "CRITICAL"
        elif numeric_value > 20:
            return "HIGH"
        elif numeric_value < 12:
            return "LOW"
        else:
            return "NORMAL"

    elif vital_abbr == "POX":
        if numeric_value is None:
            return None
        if numeric_value < 88:
            return "CRITICAL"
        elif numeric_value < 92:
            return "LOW"
        else:
            return "NORMAL"

    elif vital_abbr == "PN":
        if numeric_value is None:
            return None
        if numeric_value >= 8:
            return "CRITICAL"
        elif numeric_value >= 4:
            return "HIGH"
        else:
            return "NORMAL"

    elif vital_abbr == "BMI":
        if numeric_value is None:
            return None
        # BMI ranges (CDC/WHO adult guidelines):
        # < 18.5: Underweight (LOW)
        # 18.5-24.9: Normal weight (NORMAL)
        # 25.0-29.9: Overweight (HIGH)
        # 30.0-39.9: Obese (HIGH)
        # ≥ 40.0: Severely obese (CRITICAL)
        if numeric_value >= 40.0:
            return "CRITICAL"
        elif numeric_value >= 25.0:
            return "HIGH"
        elif numeric_value < 18.5:
            return "LOW"
        else:
            return "NORMAL"

    # For HT, WT, BG - no abnormal flags
    else:
        return None


def create_canonical_key(vital: Dict[str, Any]) -> str:
    """
    Create canonical deduplication key for a vital sign.

    Key components:
    - vital_type (e.g., "BLOOD PRESSURE")
    - taken_datetime (date + hour, ignore minutes for fuzzy matching)
    - location (or source site)

    This allows detection of duplicate vitals across PostgreSQL and Vista sources.

    Args:
        vital: Vital sign dictionary

    Returns:
        Canonical key string
    """
    vital_type = vital.get("vital_type", "").upper()

    # Parse taken_datetime to hour precision (fuzzy matching)
    taken_str = vital.get("taken_datetime", "")
    try:
        taken_dt = datetime.fromisoformat(taken_str.replace(" ", "T"))
        taken_key = taken_dt.strftime("%Y%m%d%H")  # YYYYMMDDHH
    except (ValueError, AttributeError):
        taken_key = taken_str[:13] if taken_str else "UNKNOWN"

    # Use location or source site as third component
    location = vital.get("location_name") or vital.get("source_site") or "UNKNOWN"

    return f"{vital_type}|{taken_key}|{location}"


def merge_vitals_data(
    pg_vitals: List[Dict[str, Any]],
    vista_vitals_by_site: Dict[str, str],
    patient_icn: str
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Merge PostgreSQL vitals (T-1 and earlier) with Vista vitals (T-0, today).

    Merge strategy:
    1. Parse Vista responses from all sites
    2. Deduplicate using canonical event keys
    3. Vista preferred for T-1+ conflicts (fresher data)
    4. Add source metadata for site badges

    Args:
        pg_vitals: List of vitals from PostgreSQL (historical data)
        vista_vitals_by_site: Dict mapping site sta3n to Vista RPC response
            Example: {"200": "BP^120/80^mmHg^3241217.0930^NURSE,JANE\n...", ...}
        patient_icn: Patient ICN for metadata

    Returns:
        Tuple of (merged_vitals, stats)
        - merged_vitals: Unified list of vital dictionaries, sorted by date descending
        - stats: Dictionary with merge statistics
    """
    logger.info(f"Merging vitals for {patient_icn}: {len(pg_vitals)} PG + {len(vista_vitals_by_site)} Vista sites")

    merged = []
    seen_keys = set()
    stats = {
        "pg_count": len(pg_vitals),
        "vista_count": 0,
        "vista_sites": list(vista_vitals_by_site.keys()),
        "duplicates_removed": 0,
        "total_merged": 0,
    }

    # Parse all Vista responses
    all_vista_vitals = []
    for site_sta3n, response in vista_vitals_by_site.items():
        site_vitals = parse_vista_vitals(response, site_sta3n)
        for vital in site_vitals:
            vital["patient_key"] = patient_icn
        all_vista_vitals.extend(site_vitals)
        logger.debug(f"Parsed {len(site_vitals)} vitals from Vista site {site_sta3n}")

    stats["vista_count"] = len(all_vista_vitals)

    # Add Vista vitals first (preferred for T-1+ duplicates)
    for vital in all_vista_vitals:
        key = create_canonical_key(vital)
        if key not in seen_keys:
            merged.append(vital)
            seen_keys.add(key)
        else:
            stats["duplicates_removed"] += 1
            logger.debug(f"Skipped duplicate Vista vital: {key}")

    # Add PostgreSQL vitals (only if not already present)
    for vital in pg_vitals:
        # PostgreSQL vitals already have 'data_source' field from database
        # Don't overwrite it - preserve CDWWork/CDWWork2/CALCULATED values
        # Add tracking metadata for debugging (doesn't affect template rendering)
        vital["source"] = "postgresql"
        vital["source_site"] = None
        vital["is_realtime"] = False

        key = create_canonical_key(vital)
        if key not in seen_keys:
            merged.append(vital)
            seen_keys.add(key)
        else:
            stats["duplicates_removed"] += 1
            logger.debug(f"Skipped duplicate PG vital (Vista preferred): {key}")

    # Sort by taken_datetime descending (most recent first)
    merged.sort(key=lambda v: v.get("taken_datetime") or "", reverse=True)

    stats["total_merged"] = len(merged)

    logger.info(
        f"Merge complete: {stats['total_merged']} vitals "
        f"({stats['pg_count']} PG + {stats['vista_count']} Vista - {stats['duplicates_removed']} duplicates)"
    )

    return merged, stats


def parse_fileman_date_only(fileman_str: str) -> Optional[datetime]:
    """
    Parse VistA FileMan date format (without time) to Python datetime.

    FileMan format: YYYMMDD where YYY = year - 1700
    Example: 3270106 = January 6, 2027

    Args:
        fileman_str: FileMan formatted date string

    Returns:
        Python datetime object or None if parsing fails
    """
    try:
        if not fileman_str:
            return None

        # Handle both YYYMMDD and YYYMMDD.HHMM formats
        if "." in fileman_str:
            return parse_fileman_datetime(fileman_str)

        # Parse date only: YYYMMDD
        yyy = int(fileman_str[:3])  # Years since 1700
        mm = int(fileman_str[3:5])  # Month
        dd = int(fileman_str[5:7])  # Day

        year = 1700 + yyy

        return datetime(year, mm, dd)

    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to parse FileMan date '{fileman_str}': {e}")
        return None


def parse_vista_medications(vista_response: str, site_sta3n: str) -> List[Dict[str, Any]]:
    """
    Parse VistA ORWPS COVER response into standardized medication records.

    VistA format: Multi-line response, one medication per line
    Each line: RX_NUMBER^DRUG_NAME^STATUS^QUANTITY/DAYS_SUPPLY^REFILLS_REMAINING^ISSUE_DATE^EXPIRATION_DATE

    Args:
        vista_response: Raw VistA RPC response string
        site_sta3n: Site station number (e.g., "200", "500", "630")

    Returns:
        List of parsed medication dictionaries matching PostgreSQL schema
    """
    medications = []

    if not vista_response or vista_response.startswith("-1^"):
        # Error response or no medications
        return medications

    lines = vista_response.strip().split("\n")

    for line in lines:
        if not line or "^" not in line:
            continue

        parts = line.split("^")
        if len(parts) != 7:
            logger.warning(f"Invalid Vista medication format: {line}")
            continue

        rx_number, drug_name, status, qty_days, refills_remaining, issue_date_fm, expiration_date_fm = parts

        # Parse FileMan dates
        issue_dt = parse_fileman_datetime(issue_date_fm)
        expiration_dt = parse_fileman_date_only(expiration_date_fm)

        if not issue_dt:
            logger.warning(f"Skipping medication with invalid issue date: {line}")
            continue

        # Parse quantity/days_supply
        try:
            quantity, days_supply = qty_days.split("/")
            quantity = int(quantity)
            days_supply = int(days_supply)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid quantity/days_supply format: {qty_days}")
            quantity = None
            days_supply = None

        # Parse refills
        try:
            refills = int(refills_remaining)
        except ValueError:
            refills = 0

        # Create standardized medication record (matching PostgreSQL schema)
        issue_date_str = issue_dt.strftime("%Y-%m-%d %H:%M:%S") if issue_dt else None
        expiration_date_str = expiration_dt.strftime("%Y-%m-%d") if expiration_dt else None

        # Map Vista site numbers to facility names (matching format: "(sta3n) City, State")
        facility_names = {
            "200": "(200) Alexandria, VA",
            "500": "(500) Anchorage, AK",
            "630": "(630) Palo Alto, CA"
        }
        facility_name = facility_names.get(site_sta3n, f"VistA Site {site_sta3n}")

        medication = {
            "medication_id": f"vista_{site_sta3n}_{rx_number}",  # Unique ID for Vista data
            "patient_key": None,  # Will be set by caller
            "prescription_number": rx_number,
            "drug_name": drug_name,
            "drug_name_local": drug_name,  # Template uses this field
            "drug_name": drug_name,  # Also set base field
            "status": status,
            "type": "outpatient",  # Vista ORWPS COVER returns outpatient only
            "quantity": quantity,
            "days_supply": days_supply,
            "refills_remaining": refills,
            "issue_date": issue_date_str,
            "date": issue_date_str,  # Template uses this for display
            "expiration_date": expiration_date_str,
            "location_id": None,
            "location_name": f"VistA Site {site_sta3n}",
            "location_type": "VistA",
            "facility_name": facility_name,  # Facility for display column
            "provider_name": "VistA Realtime",  # Provider not available from ORWPS COVER RPC
            "pharmacy_name": facility_name,  # Show facility as pharmacy (second line)
            "is_controlled": False,  # Template uses this field name
            "is_controlled_substance": False,  # Database field name (for compatibility)
            "dea_schedule": None,
            "generic_name": None,  # Not provided by ORWPS COVER RPC
            "sig": None,  # Sig not provided by ORWPS COVER (would need ORWPS DETAIL)
            "drug_strength": None,  # Would need drug database lookup
            "drug_unit": None,  # Would need drug database lookup
            "dosage": None,  # For inpatient meds (N/A for outpatient)
            "route": None,  # Would need ORWPS DETAIL RPC
            # Data source for badge display
            "data_source": "CDWWork",  # VistA meds show as CDWWork (blue badge)
            # Vista-specific metadata for tracking
            "source": "vista",
            "source_site": site_sta3n,
            "is_realtime": True,
        }

        medications.append(medication)

    return medications


def create_canonical_medication_key(medication: Dict[str, Any]) -> str:
    """
    Create canonical deduplication key for a medication.

    Key components:
    - source_site (or location_name if from PostgreSQL)
    - prescription_number

    Format: {site}:{prescription_number}
    Example: "200:2860066"

    This allows detection of:
    - Exact duplicates (same RX at same site in both PG and Vista)
    - Multi-site prescriptions (same RX number at different sites - NOT duplicates)

    Args:
        medication: Medication dictionary

    Returns:
        Canonical key string
    """
    # Get site identifier
    site = medication.get("source_site")
    if not site:
        # For PostgreSQL data, try to extract from location_name
        location = medication.get("location_name", "")
        if "Site" in location:
            try:
                site = location.split("Site")[1].strip().split()[0]
            except IndexError:
                site = "UNKNOWN"
        else:
            site = "PG"

    # Get prescription number
    rx_number = medication.get("prescription_number", "UNKNOWN")

    return f"{site}:{rx_number}"


def merge_medications_data(
    pg_medications: List[Dict[str, Any]],
    vista_medications_by_site: Dict[str, str],
    patient_icn: str
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Merge PostgreSQL medications (T-1 and earlier) with Vista medications (T-0, today).

    Merge strategy:
    1. Parse Vista responses from all sites
    2. Deduplicate using canonical event keys: {site}:{prescription_number}
    3. Vista preferred for T-1+ conflicts (fresher data)
    4. Add source metadata for site badges
    5. Sort by issue_date descending

    Args:
        pg_medications: List of medications from PostgreSQL (historical data)
        vista_medications_by_site: Dict mapping site sta3n to Vista RPC response
            Example: {"200": "2860066^LISINOPRIL 10MG TAB^ACTIVE^60/90^3^...\n...", ...}
        patient_icn: Patient ICN for metadata

    Returns:
        Tuple of (merged_medications, stats)
        - merged_medications: Unified list of medication dictionaries, sorted by date descending
        - stats: Dictionary with merge statistics
    """
    logger.info(f"Merging medications for {patient_icn}: {len(pg_medications)} PG + {len(vista_medications_by_site)} Vista sites")

    merged = []
    seen_keys = set()
    stats = {
        "pg_count": len(pg_medications),
        "vista_count": 0,
        "vista_sites": list(vista_medications_by_site.keys()),
        "duplicates_removed": 0,
        "total_merged": 0,
    }

    # Parse all Vista responses
    all_vista_medications = []
    for site_sta3n, response in vista_medications_by_site.items():
        site_medications = parse_vista_medications(response, site_sta3n)
        for medication in site_medications:
            medication["patient_key"] = patient_icn
        all_vista_medications.extend(site_medications)
        logger.debug(f"Parsed {len(site_medications)} medications from Vista site {site_sta3n}")

    stats["vista_count"] = len(all_vista_medications)

    # Add Vista medications first (preferred for T-1+ duplicates)
    for medication in all_vista_medications:
        key = create_canonical_medication_key(medication)
        if key not in seen_keys:
            merged.append(medication)
            seen_keys.add(key)
        else:
            stats["duplicates_removed"] += 1
            logger.debug(f"Skipped duplicate Vista medication: {key}")

    # Add PostgreSQL medications (only if not already present)
    for medication in pg_medications:
        # PostgreSQL medications already have 'data_source' field from database
        # Don't overwrite it - preserve CDWWork/CDWWork2 values
        # Add tracking metadata for debugging (doesn't affect template rendering)
        medication["source"] = "postgresql"
        medication["source_site"] = None
        medication["is_realtime"] = False

        key = create_canonical_medication_key(medication)
        if key not in seen_keys:
            merged.append(medication)
            seen_keys.add(key)
        else:
            stats["duplicates_removed"] += 1
            logger.debug(f"Skipped duplicate PG medication (Vista preferred): {key}")

    # Sort by issue_date descending (most recent first)
    merged.sort(key=lambda m: m.get("issue_date") or "", reverse=True)

    stats["total_merged"] = len(merged)

    logger.info(
        f"Merge complete: {stats['total_merged']} medications "
        f"({stats['pg_count']} PG + {stats['vista_count']} Vista - {stats['duplicates_removed']} duplicates)"
    )

    return merged, stats


# -----------------------------------------------------------------------------
# PROBLEMS DOMAIN - Real-time Merge/Dedupe (Added 2026-02-07)
# -----------------------------------------------------------------------------

def parse_vista_problems(vista_response: str, site_sta3n: str) -> List[Dict[str, Any]]:
    """
    Parse VistA ORQQPL LIST response into standardized problem records.

    VistA format: Multi-line response, one problem per line
    Each line: PROBLEM_IEN^PROBLEM_TEXT^ICD10_CODE^STATUS^ONSET_DATE^SERVICE_CONNECTED^SNOMED_CODE^UPDATED_TODAY

    Args:
        vista_response: Raw VistA RPC response string
        site_sta3n: Site station number (e.g., "200", "500", "630")

    Returns:
        List of parsed problem dictionaries matching PostgreSQL schema
    """
    problems = []

    if not vista_response or vista_response.startswith("-1^"):
        # Error response or no problems
        return problems

    lines = vista_response.strip().split("\n")

    for line in lines:
        if not line or "^" not in line:
            continue

        parts = line.split("^")
        if len(parts) != 8:
            logger.warning(f"Invalid Vista problem format: {line}")
            continue

        problem_ien, problem_text, icd10_code, status, onset_date_fm, service_connected, snomed_code, updated_today = parts

        # Parse FileMan date (date only, no time)
        onset_dt = parse_fileman_date_only(onset_date_fm)

        if not onset_dt:
            logger.warning(f"Skipping problem with invalid onset date: {line}")
            continue

        # Convert flags to boolean
        service_connected_bool = (service_connected == "1")
        updated_today_bool = (updated_today == "1")

        # Map status to PostgreSQL values (normalize casing)
        status_mapped = status.capitalize()  # Active, Inactive, Resolved

        # Construct problem record matching PostgreSQL schema
        problem = {
            "problem_ien": problem_ien,
            "problem_text": problem_text,
            "icd10_code": icd10_code,
            "icd10_description": None,  # Not available in Vista response
            "snomed_code": snomed_code,
            "snomed_description": None,  # Not available in Vista response
            "problem_status": status_mapped,
            "onset_date": onset_dt.strftime("%Y-%m-%d"),
            "service_connected": service_connected_bool,
            "updated_today": updated_today_bool,
            "source_site": site_sta3n,
            "source": "vista",
            "is_realtime": True,
            "data_source": f"VistA Site {site_sta3n}",
        }

        problems.append(problem)

    logger.debug(f"Parsed {len(problems)} problems from Vista site {site_sta3n}")
    return problems


def create_canonical_problem_key(problem: Dict[str, Any]) -> str:
    """
    Create canonical deduplication key for a problem.

    Key components:
    - icd10_code
    - onset_date
    - source_site (if available)

    Format: {icd10_code}:{onset_date}:{site}
    Example: "E11.9:2018-06-15:200"

    Deduplication rules (from problems-design.md Section 5.5):
    - Same ICN + Same ICD-10 Code + Same Onset Date = Duplicate (VistA preferred)

    Args:
        problem: Problem dictionary

    Returns:
        Canonical key string
    """
    # Get ICD-10 code (required)
    icd10 = problem.get("icd10_code", "UNKNOWN")

    # Get onset date (required)
    onset = problem.get("onset_date", "UNKNOWN")

    # Get site identifier (optional - helps distinguish multi-site problems)
    site = problem.get("source_site")
    if not site:
        # For PostgreSQL data, try to extract from location_name or data_source
        data_source = problem.get("data_source", "")
        if "Site" in data_source:
            try:
                site = data_source.split("Site")[1].strip().split()[0]
            except IndexError:
                site = "UNKNOWN"
        else:
            site = "PG"

    return f"{icd10}:{onset}:{site}"


def merge_problems_data(
    pg_problems: List[Dict[str, Any]],
    vista_problems_by_site: Dict[str, str],
    patient_icn: str
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Merge PostgreSQL problems (T-1 and earlier) with Vista problems (T-0, today).

    Merge strategy:
    1. Parse Vista responses from all sites
    2. Deduplicate using canonical event keys: {icd10}:{onset_date}:{site}
    3. Vista preferred for T-1+ conflicts (fresher data)
    4. Add source metadata for site badges
    5. Sort by onset_date descending (most recent first)

    Args:
        pg_problems: List of problems from PostgreSQL (historical data)
        vista_problems_by_site: Dict mapping site sta3n to Vista RPC response
            Example: {"200": "200-123^CHF^I50.23^Active^3230115^1^42343007^0\n...", ...}
        patient_icn: Patient ICN for metadata

    Returns:
        Tuple of (merged_problems, stats)
        - merged_problems: Unified list of problem dictionaries, sorted by date descending
        - stats: Dictionary with merge statistics
    """
    logger.info(f"Merging problems for {patient_icn}: {len(pg_problems)} PG + {len(vista_problems_by_site)} Vista sites")

    merged = []
    seen_keys = set()
    stats = {
        "pg_count": len(pg_problems),
        "vista_count": 0,
        "vista_sites": list(vista_problems_by_site.keys()),
        "duplicates_removed": 0,
        "total_merged": 0,
    }

    # Parse all Vista responses
    all_vista_problems = []
    for site_sta3n, response in vista_problems_by_site.items():
        site_problems = parse_vista_problems(response, site_sta3n)
        for problem in site_problems:
            problem["patient_key"] = patient_icn
        all_vista_problems.extend(site_problems)
        logger.debug(f"Parsed {len(site_problems)} problems from Vista site {site_sta3n}")

    stats["vista_count"] = len(all_vista_problems)

    # Add Vista problems first (preferred for T-1+ duplicates)
    for problem in all_vista_problems:
        key = create_canonical_problem_key(problem)
        if key not in seen_keys:
            merged.append(problem)
            seen_keys.add(key)
        else:
            stats["duplicates_removed"] += 1
            logger.debug(f"Skipped duplicate Vista problem: {key}")

    # Add PostgreSQL problems (only if not already present)
    for problem in pg_problems:
        # PostgreSQL problems already have 'data_source' field from database
        # Don't overwrite it - preserve CDWWork/CDWWork2 values
        # Add tracking metadata for debugging (doesn't affect template rendering)
        problem["source"] = "postgresql"
        problem["source_site"] = None
        problem["is_realtime"] = False

        key = create_canonical_problem_key(problem)
        if key not in seen_keys:
            merged.append(problem)
            seen_keys.add(key)
        else:
            stats["duplicates_removed"] += 1
            logger.debug(f"Skipped duplicate PG problem (Vista preferred): {key}")

    # Sort by onset_date descending (most recent first)
    merged.sort(key=lambda p: p.get("onset_date") or "", reverse=True)

    stats["total_merged"] = len(merged)

    logger.info(
        f"Merge complete: {stats['total_merged']} problems "
        f"({stats['pg_count']} PG + {stats['vista_count']} Vista - {stats['duplicates_removed']} duplicates)"
    )

    return merged, stats
