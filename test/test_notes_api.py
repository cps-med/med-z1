#!/usr/bin/env python3
# ---------------------------------------------------------------------
# test_notes_api.py
# ---------------------------------------------------------------------
# Test script for clinical notes database queries and API functions
# Tests Day 4 deliverables: database query layer
# ---------------------------------------------------------------------

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.notes import (
    get_recent_notes,
    get_notes_summary,
    get_all_notes,
    get_note_detail,
    get_note_authors
)

def test_recent_notes():
    """Test get_recent_notes function"""
    print("=" * 70)
    print("TEST: get_recent_notes(ICN100001, limit=4)")
    print("=" * 70)

    try:
        notes = get_recent_notes("ICN100001", limit=4)
        print(f"✅ Success: Retrieved {len(notes)} recent notes")

        for i, note in enumerate(notes, 1):
            print(f"\nNote {i}:")
            print(f"  ID: {note['note_id']}")
            print(f"  Title: {note['document_title']}")
            print(f"  Class: {note['document_class']}")
            print(f"  Date: {note['reference_datetime']}")
            print(f"  Author: {note['author_name']}")
            print(f"  Preview: {note['text_preview'][:80]}...")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_notes_summary():
    """Test get_notes_summary function"""
    print("\n" + "=" * 70)
    print("TEST: get_notes_summary(ICN100001)")
    print("=" * 70)

    try:
        summary = get_notes_summary("ICN100001")
        print(f"✅ Success: Retrieved notes summary")
        print(f"  Total Notes: {summary['total_notes']}")
        print(f"  Notes by Class:")
        for note_class, count in summary['notes_by_class'].items():
            print(f"    {note_class}: {count}")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_all_notes():
    """Test get_all_notes function with various filters"""
    print("\n" + "=" * 70)
    print("TEST: get_all_notes(ICN100001, limit=10)")
    print("=" * 70)

    try:
        result = get_all_notes(
            icn="ICN100001",
            note_class='all',
            date_range=None,  # All time
            author=None,
            status='all',
            sort_by='reference_datetime',
            sort_order='desc',
            limit=10,
            offset=0
        )

        notes = result['notes']
        pagination = result['pagination']

        print(f"✅ Success: Retrieved {len(notes)} notes")
        print(f"  Total Count: {pagination['total_count']}")
        print(f"  Current Page: {pagination['current_page']}/{pagination['total_pages']}")
        print(f"  Per Page: {pagination['per_page']}")

        print(f"\nFirst 3 notes:")
        for i, note in enumerate(notes[:3], 1):
            print(f"  {i}. {note['document_title']} - {note['reference_datetime']}")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_all_notes_filtered():
    """Test get_all_notes with filters"""
    print("\n" + "=" * 70)
    print("TEST: get_all_notes(ICN100001, note_class='Progress Notes', date_range=90)")
    print("=" * 70)

    try:
        result = get_all_notes(
            icn="ICN100001",
            note_class='Progress Notes',
            date_range=90,
            author=None,
            status='all',
            sort_by='reference_datetime',
            sort_order='desc',
            limit=20,
            offset=0
        )

        notes = result['notes']
        pagination = result['pagination']

        print(f"✅ Success: Retrieved {len(notes)} Progress Notes from last 90 days")
        print(f"  Total Matching: {pagination['total_count']}")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_note_detail():
    """Test get_note_detail function"""
    print("\n" + "=" * 70)
    print("TEST: get_note_detail(ICN100001, note_id=1)")
    print("=" * 70)

    try:
        # First get a valid note_id
        recent = get_recent_notes("ICN100001", limit=1)
        if not recent:
            print("⚠️  No notes found for patient")
            return False

        note_id = recent[0]['note_id']
        note = get_note_detail("ICN100001", note_id)

        if note:
            print(f"✅ Success: Retrieved full note details")
            print(f"  Note ID: {note['note_id']}")
            print(f"  Title: {note['document_title']}")
            print(f"  Class: {note['document_class']}")
            print(f"  Author: {note['author_name']}")
            print(f"  Facility: {note['facility_name']}")
            print(f"  Text Length: {note['text_length']} characters")
            print(f"  Document Text (first 200 chars):")
            print(f"    {note['document_text'][:200]}...")
            return True
        else:
            print(f"❌ Error: Note {note_id} not found")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_note_authors():
    """Test get_note_authors function"""
    print("\n" + "=" * 70)
    print("TEST: get_note_authors(ICN100001)")
    print("=" * 70)

    try:
        authors = get_note_authors("ICN100001")
        print(f"✅ Success: Retrieved {len(authors)} unique authors")
        print(f"  Authors:")
        for author in authors[:5]:  # Show first 5
            print(f"    - {author}")
        if len(authors) > 5:
            print(f"    ... and {len(authors) - 5} more")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("CLINICAL NOTES DATABASE QUERY TESTS")
    print("=" * 70)

    tests = [
        ("Recent Notes", test_recent_notes),
        ("Notes Summary", test_notes_summary),
        ("All Notes (No Filters)", test_all_notes),
        ("All Notes (With Filters)", test_all_notes_filtered),
        ("Note Detail", test_note_detail),
        ("Note Authors", test_note_authors),
    ]

    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
