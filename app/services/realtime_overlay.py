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
