# ---------------------------------------------------------------------
# vista/app/utils/m_serializer.py
# ---------------------------------------------------------------------
# VistA M-Language Data Format Serializer
# Converts Python data structures to VistA RPC response format
# ---------------------------------------------------------------------

from typing import Any, Dict, List, Optional, Union


# VistA Delimiters
FIELD_DELIMITER = "^"      # Caret - separates fields within a record
LIST_DELIMITER = "\n"      # Newline - separates list items (multi-line responses)
SUBFIELD_DELIMITER = ";"   # Semicolon - separates sub-fields


def pack_vista_string(fields: List[Any], delimiter: str = FIELD_DELIMITER) -> str:
    """
    Pack a list of fields into a VistA-formatted string.

    VistA uses caret (^) as the standard field delimiter. Fields are converted
    to strings and joined with the delimiter. None values become empty strings.

    Args:
        fields: List of field values (strings, numbers, None, etc.)
        delimiter: Field delimiter (default: "^")

    Returns:
        VistA-formatted string (e.g., "SMITH,JOHN^123456789^19450315^M")

    Example:
        >>> pack_vista_string(["SMITH,JOHN", "123456789", "19450315", "M"])
        'SMITH,JOHN^123456789^19450315^M'

        >>> pack_vista_string([120, 80], delimiter="/")
        '120/80'
    """
    # Convert all fields to strings, treating None as empty string
    str_fields = [str(field) if field is not None else "" for field in fields]
    return delimiter.join(str_fields)


def pack_vista_list(
    items: List[Dict[str, Any]],
    field_order: List[str],
    delimiter: str = FIELD_DELIMITER
) -> str:
    """
    Pack a list of dictionaries into VistA multi-line format.

    Each dictionary becomes one line, with fields extracted in the specified order
    and joined with the delimiter. Lines are separated by newlines.

    Args:
        items: List of dictionaries containing item data
        field_order: List of dictionary keys specifying field order
        delimiter: Field delimiter (default: "^")

    Returns:
        Multi-line VistA-formatted string

    Example:
        >>> items = [
        ...     {"date": "3241201", "type": "BP", "value": "120/80"},
        ...     {"date": "3241202", "type": "TEMP", "value": "98.6"}
        ... ]
        >>> pack_vista_list(items, ["date", "type", "value"])
        '3241201^BP^120/80\\n3241202^TEMP^98.6'
    """
    lines = []
    for item in items:
        # Extract fields in specified order, using None for missing keys
        fields = [item.get(key) for key in field_order]
        line = pack_vista_string(fields, delimiter)
        lines.append(line)

    return LIST_DELIMITER.join(lines)


def pack_vista_array(
    data: Dict[str, Any],
    key_value_delimiter: str = "="
) -> str:
    """
    Pack a dictionary into VistA array format.

    VistA arrays are multi-line with key=value pairs. Used for returning
    associative arrays or named parameters.

    Args:
        data: Dictionary to convert to VistA array format
        key_value_delimiter: Delimiter between key and value (default: "=")

    Returns:
        Multi-line string with key=value pairs

    Example:
        >>> pack_vista_array({"NAME": "SMITH,JOHN", "SSN": "123456789", "DOB": "19450315"})
        'NAME=SMITH,JOHN\\nSSN=123456789\\nDOB=19450315'
    """
    lines = []
    for key, value in data.items():
        # Convert value to string, handling None
        value_str = str(value) if value is not None else ""
        lines.append(f"{key}{key_value_delimiter}{value_str}")

    return LIST_DELIMITER.join(lines)


def format_rpc_error(message: str, code: str = "-1") -> str:
    """
    Format an RPC error response in VistA format.

    VistA error responses typically start with a negative error code followed
    by the error message, separated by caret.

    Args:
        message: Error message
        code: Error code (default: "-1" for generic error)

    Returns:
        VistA-formatted error string

    Example:
        >>> format_rpc_error("Patient not found", "-1")
        '-1^Patient not found'

        >>> format_rpc_error("Invalid parameter", "-100")
        '-100^Invalid parameter'
    """
    return pack_vista_string([code, message])


def escape_vista_string(value: str, delimiter: str = FIELD_DELIMITER) -> str:
    """
    Escape special characters in VistA string values.

    If the value contains the delimiter character, it may need escaping
    depending on the RPC context. This is a basic implementation that
    replaces delimiters with a space (common VistA pattern).

    Args:
        value: String value to escape
        delimiter: Delimiter to escape (default: "^")

    Returns:
        Escaped string safe for VistA format

    Example:
        >>> escape_vista_string("120/80 (sitting^resting)")
        '120/80 (sitting resting)'
    """
    # Replace delimiter with space (common VistA escape pattern)
    # More sophisticated escaping can be added as needed
    return value.replace(delimiter, " ")


def parse_vista_string(
    vista_string: str,
    delimiter: str = FIELD_DELIMITER
) -> List[str]:
    """
    Parse a VistA-formatted string into a list of fields.

    This is the inverse of pack_vista_string, used when parsing VistA
    responses or parameters.

    Args:
        vista_string: VistA-formatted string
        delimiter: Field delimiter (default: "^")

    Returns:
        List of field values

    Example:
        >>> parse_vista_string("SMITH,JOHN^123456789^19450315^M")
        ['SMITH,JOHN', '123456789', '19450315', 'M']
    """
    return vista_string.split(delimiter)


def parse_vista_list(
    vista_list: str,
    delimiter: str = FIELD_DELIMITER
) -> List[List[str]]:
    """
    Parse a VistA multi-line list into a list of field lists.

    This is the inverse of pack_vista_list, used when parsing multi-line
    VistA responses.

    Args:
        vista_list: Multi-line VistA string
        delimiter: Field delimiter (default: "^")

    Returns:
        List of field lists (one per line)

    Example:
        >>> parse_vista_list("3241201^BP^120/80\\n3241202^TEMP^98.6")
        [['3241201', 'BP', '120/80'], ['3241202', 'TEMP', '98.6']]
    """
    lines = vista_list.strip().split(LIST_DELIMITER)
    return [parse_vista_string(line, delimiter) for line in lines if line]


def format_patient_inquiry_response(patient: Dict[str, Any]) -> str:
    """
    Format patient data for ORWPT PTINQ RPC response.

    ORWPT PTINQ returns patient demographics in VistA format:
    NAME^SSN^DOB^SEX^VETERAN_STATUS

    Args:
        patient: Patient dictionary with demographic fields

    Returns:
        VistA-formatted patient string

    Example:
        >>> patient = {
        ...     "name_display": "SMITH,JOHN Q",
        ...     "ssn": "666-12-1234",
        ...     "dob": "1945-03-15",
        ...     "sex": "M",
        ...     "veteran_status": "VETERAN"
        ... }
        >>> format_patient_inquiry_response(patient)
        'SMITH,JOHN Q^666-12-1234^19450315^M^VETERAN'
    """
    # Get name_display, or construct from name_last and name_first
    name_display = patient.get("name_display")
    if not name_display:
        name_last = patient.get("name_last", "")
        name_first = patient.get("name_first", "")
        name_middle = patient.get("name_middle", "")

        # Construct name as "LAST,FIRST MIDDLE"
        if name_last and name_first:
            name_display = f"{name_last},{name_first}"
            if name_middle:
                name_display += f" {name_middle}"
        else:
            name_display = name_last or name_first or ""

    # Format DOB to FileMan format (YYYY-MM-DD -> YYYMMDD where YYY = year - 1700)
    dob = patient.get("dob", "")
    if dob and len(dob) == 10:  # YYYY-MM-DD format
        year, month, day = dob.split("-")
        fileman_year = int(year) - 1700
        dob_fileman = f"{fileman_year:03d}{month}{day}"
    else:
        dob_fileman = ""

    fields = [
        name_display,
        patient.get("ssn", ""),
        dob_fileman,
        patient.get("sex", ""),
        patient.get("veteran_status", "VETERAN")  # Default to VETERAN
    ]

    return pack_vista_string(fields)
