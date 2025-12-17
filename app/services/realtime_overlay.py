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

        # Create standardized vital record (matching PostgreSQL schema)
        vital = {
            "vital_id": None,  # No persistent ID for Vista data
            "patient_key": None,  # Will be set by caller
            "vital_sign_id": None,
            "vital_type": vital_type,
            "vital_abbr": _get_vital_abbr(vital_type),
            "taken_datetime": taken_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "entered_datetime": taken_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "result_value": value,
            "numeric_value": _extract_numeric_value(value, vital_type),
            "systolic": _extract_systolic(value, vital_type),
            "diastolic": _extract_diastolic(value, vital_type),
            "metric_value": None,  # Could be computed if needed
            "unit_of_measure": units,
            "qualifiers": None,
            "location_id": None,
            "location_name": f"VistA Site {site_sta3n}",
            "location_type": "VistA",
            "entered_by": entered_by,
            "abnormal_flag": None,  # Could be computed based on ranges
            "bmi": None,
            # Vista-specific metadata
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
        # Mark PostgreSQL vitals with source metadata
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
