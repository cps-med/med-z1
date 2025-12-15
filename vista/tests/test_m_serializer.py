# ---------------------------------------------------------------------
# vista/tests/test_m_serializer.py
# ---------------------------------------------------------------------
# Unit tests for VistA M-Language data format serializer
# ---------------------------------------------------------------------

import pytest
from vista.app.utils.m_serializer import (
    pack_vista_string,
    pack_vista_list,
    pack_vista_array,
    format_rpc_error,
    escape_vista_string,
    parse_vista_string,
    parse_vista_list,
    format_patient_inquiry_response,
    FIELD_DELIMITER,
    LIST_DELIMITER,
)


class TestPackVistaString:
    """Test suite for pack_vista_string function"""

    def test_basic_string_packing(self):
        """Test packing basic string fields"""
        fields = ["SMITH,JOHN", "123456789", "19450315", "M"]
        result = pack_vista_string(fields)
        assert result == "SMITH,JOHN^123456789^19450315^M"

    def test_packing_with_numbers(self):
        """Test packing numeric fields"""
        fields = [120, 80, 98.6]
        result = pack_vista_string(fields)
        assert result == "120^80^98.6"

    def test_packing_with_none_values(self):
        """Test that None values become empty strings"""
        fields = ["SMITH", None, "M", None]
        result = pack_vista_string(fields)
        assert result == "SMITH^^M^"

    def test_custom_delimiter(self):
        """Test using custom delimiter"""
        fields = [120, 80]
        result = pack_vista_string(fields, delimiter="/")
        assert result == "120/80"

    def test_empty_list(self):
        """Test packing empty list"""
        result = pack_vista_string([])
        assert result == ""

    def test_single_field(self):
        """Test packing single field"""
        result = pack_vista_string(["SINGLE"])
        assert result == "SINGLE"


class TestPackVistaList:
    """Test suite for pack_vista_list function"""

    def test_basic_list_packing(self):
        """Test packing list of dictionaries"""
        items = [
            {"date": "3241201", "type": "BP", "value": "120/80"},
            {"date": "3241202", "type": "TEMP", "value": "98.6"}
        ]
        result = pack_vista_list(items, ["date", "type", "value"])
        expected = "3241201^BP^120/80\n3241202^TEMP^98.6"
        assert result == expected

    def test_missing_keys(self):
        """Test that missing dictionary keys become empty strings"""
        items = [
            {"date": "3241201", "type": "BP"},  # Missing 'value'
            {"date": "3241202", "value": "98.6"}  # Missing 'type'
        ]
        result = pack_vista_list(items, ["date", "type", "value"])
        expected = "3241201^BP^\n3241202^^98.6"
        assert result == expected

    def test_empty_list(self):
        """Test packing empty list"""
        result = pack_vista_list([], ["field1", "field2"])
        assert result == ""

    def test_single_item(self):
        """Test packing single item"""
        items = [{"name": "SMITH", "ssn": "123456789"}]
        result = pack_vista_list(items, ["name", "ssn"])
        assert result == "SMITH^123456789"

    def test_custom_delimiter(self):
        """Test using custom delimiter"""
        items = [{"a": "1", "b": "2"}]
        result = pack_vista_list(items, ["a", "b"], delimiter="|")
        assert result == "1|2"


class TestPackVistaArray:
    """Test suite for pack_vista_array function"""

    def test_basic_array_packing(self):
        """Test packing dictionary to array format"""
        data = {"NAME": "SMITH,JOHN", "SSN": "123456789", "DOB": "19450315"}
        result = pack_vista_array(data)
        lines = result.split("\n")
        assert len(lines) == 3
        assert "NAME=SMITH,JOHN" in lines
        assert "SSN=123456789" in lines
        assert "DOB=19450315" in lines

    def test_none_values(self):
        """Test that None values become empty strings"""
        data = {"KEY1": "value", "KEY2": None}
        result = pack_vista_array(data)
        assert "KEY1=value" in result
        assert "KEY2=" in result

    def test_empty_dict(self):
        """Test packing empty dictionary"""
        result = pack_vista_array({})
        assert result == ""

    def test_custom_delimiter(self):
        """Test using custom key-value delimiter"""
        data = {"A": "1", "B": "2"}
        result = pack_vista_array(data, key_value_delimiter=":")
        lines = result.split("\n")
        assert "A:1" in lines
        assert "B:2" in lines


class TestFormatRPCError:
    """Test suite for format_rpc_error function"""

    def test_default_error_code(self):
        """Test error formatting with default code"""
        result = format_rpc_error("Patient not found")
        assert result == "-1^Patient not found"

    def test_custom_error_code(self):
        """Test error formatting with custom code"""
        result = format_rpc_error("Invalid parameter", code="-100")
        assert result == "-100^Invalid parameter"

    def test_empty_message(self):
        """Test error with empty message"""
        result = format_rpc_error("")
        assert result == "-1^"


class TestEscapeVistaString:
    """Test suite for escape_vista_string function"""

    def test_escape_caret(self):
        """Test escaping caret delimiter"""
        value = "120/80 (sitting^resting)"
        result = escape_vista_string(value)
        assert result == "120/80 (sitting resting)"
        assert "^" not in result

    def test_no_escape_needed(self):
        """Test string with no special characters"""
        value = "SMITH,JOHN"
        result = escape_vista_string(value)
        assert result == "SMITH,JOHN"

    def test_custom_delimiter(self):
        """Test escaping custom delimiter"""
        value = "data|with|pipes"
        result = escape_vista_string(value, delimiter="|")
        assert result == "data with pipes"


class TestParseVistaString:
    """Test suite for parse_vista_string function"""

    def test_basic_parsing(self):
        """Test parsing VistA string"""
        vista_string = "SMITH,JOHN^123456789^19450315^M"
        result = parse_vista_string(vista_string)
        assert result == ["SMITH,JOHN", "123456789", "19450315", "M"]

    def test_parse_with_empty_fields(self):
        """Test parsing string with empty fields"""
        vista_string = "SMITH^^M^"
        result = parse_vista_string(vista_string)
        assert result == ["SMITH", "", "M", ""]

    def test_custom_delimiter(self):
        """Test parsing with custom delimiter"""
        vista_string = "120/80"
        result = parse_vista_string(vista_string, delimiter="/")
        assert result == ["120", "80"]


class TestParseVistaList:
    """Test suite for parse_vista_list function"""

    def test_basic_list_parsing(self):
        """Test parsing multi-line VistA list"""
        vista_list = "3241201^BP^120/80\n3241202^TEMP^98.6"
        result = parse_vista_list(vista_list)
        assert result == [
            ["3241201", "BP", "120/80"],
            ["3241202", "TEMP", "98.6"]
        ]

    def test_parse_single_line(self):
        """Test parsing single-line list"""
        vista_list = "SMITH^123456789"
        result = parse_vista_list(vista_list)
        assert result == [["SMITH", "123456789"]]

    def test_parse_with_trailing_newline(self):
        """Test parsing list with trailing newline"""
        vista_list = "LINE1^A\nLINE2^B\n"
        result = parse_vista_list(vista_list)
        assert result == [["LINE1", "A"], ["LINE2", "B"]]

    def test_parse_empty_string(self):
        """Test parsing empty string"""
        result = parse_vista_list("")
        assert result == []


class TestFormatPatientInquiryResponse:
    """Test suite for format_patient_inquiry_response function"""

    def test_complete_patient_data(self):
        """Test formatting complete patient record"""
        patient = {
            "name_display": "SMITH,JOHN Q",
            "ssn": "666-12-1234",
            "dob": "1945-03-15",
            "sex": "M",
            "veteran_status": "VETERAN"
        }
        result = format_patient_inquiry_response(patient)
        # DOB 1945-03-15 -> FileMan 2450315 (1945-1700=245)
        assert result == "SMITH,JOHN Q^666-12-1234^2450315^M^VETERAN"

    def test_missing_optional_fields(self):
        """Test with missing optional fields"""
        patient = {
            "name_display": "DOE,JANE",
            "ssn": "123-45-6789",
            "dob": "1980-01-02",
            "sex": "F"
            # veteran_status missing - should default to VETERAN
        }
        result = format_patient_inquiry_response(patient)
        assert result == "DOE,JANE^123-45-6789^2800102^F^VETERAN"

    def test_missing_dob(self):
        """Test with missing DOB"""
        patient = {
            "name_display": "TEST,PATIENT",
            "ssn": "999-99-9999",
            "sex": "M"
        }
        result = format_patient_inquiry_response(patient)
        # Empty DOB should result in empty field
        assert "^^" in result  # Two consecutive carets indicate empty DOB

    def test_fileman_date_conversion(self):
        """Test FileMan date conversion for various years"""
        # Year 2000
        patient = {"name_display": "TEST", "ssn": "123", "dob": "2000-06-15", "sex": "M"}
        result = format_patient_inquiry_response(patient)
        assert "3000615" in result  # 2000-1700=300

        # Year 1965
        patient = {"name_display": "TEST", "ssn": "123", "dob": "1965-07-15", "sex": "M"}
        result = format_patient_inquiry_response(patient)
        assert "2650715" in result  # 1965-1700=265


class TestRoundTripConversion:
    """Test round-trip conversion (pack -> parse -> pack)"""

    def test_string_round_trip(self):
        """Test pack and parse are inverse operations"""
        original = ["SMITH", "123", "M"]
        packed = pack_vista_string(original)
        parsed = parse_vista_string(packed)
        assert parsed == original

    def test_list_round_trip(self):
        """Test list pack and parse round trip"""
        original_items = [
            {"a": "1", "b": "2"},
            {"a": "3", "b": "4"}
        ]
        packed = pack_vista_list(original_items, ["a", "b"])
        parsed = parse_vista_list(packed)
        assert parsed == [["1", "2"], ["3", "4"]]
