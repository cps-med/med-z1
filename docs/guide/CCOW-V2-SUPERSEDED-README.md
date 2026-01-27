# CCOW v2.0 Testing Guide - SUPERSEDED

**Date Superseded:** 2026-01-27
**Superseded By:** `ccow-v2.1-testing-guide.md`

---

## Notice

This document (`ccow-v2-testing-guide.md`) has been **SUPERSEDED** by the newer `ccow-v2.1-testing-guide.md`.

**Reason for Supersession:**
CCOW Context Vault was upgraded from v2.0 to v2.1 on 2026-01-27, adding support for cross-application authentication via the `X-Session-ID` header.

---

## What Changed in v2.1

### New Authentication Methods

**v2.0 (This Document):**
- Only supported `session_id` cookie authentication

**v2.1 (New Document):**
- Supports **both** `session_id` cookie AND `X-Session-ID` header
- Header authentication enables med-z4 and other external apps to integrate
- Cookie authentication maintained for backward compatibility with med-z1

### Documentation Updates

The new v2.1 testing guide includes:
- ✅ All v2.0 content (cookie-based testing)
- ✅ New header-based authentication tests
- ✅ Priority testing (header > cookie)
- ✅ CORS workarounds (from v2.0)
- ✅ Insomnia testing guide (from v2.0)
- ✅ Enhanced troubleshooting
- ✅ Quick test suite script

---

## Migration Guide

### If You're Using Cookie-Based Auth (med-z1)

**No changes needed!** All cookie-based tests from v2.0 continue to work in v2.1.

```bash
# v2.0 command (still works in v2.1)
curl -X GET http://localhost:8001/ccow/active-patient \
  -b "session_id=<your-session-id>"
```

### If You're Building External Integration (med-z4)

**Use the new header-based auth:**

```bash
# v2.1 new capability
curl -X GET http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: <your-session-id>"
```

---

## Where to Find Current Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| **Testing Guide (v2.1)** | `docs/guide/ccow-v2.1-testing-guide.md` | API testing with curl/Insomnia |
| **Design Spec (v2.1)** | `docs/spec/ccow-multi-user-enhancement.md` (Section 14) | Cross-app auth design |
| **Implementation Summary** | `docs/spec/CCOW-V2.1-IMPLEMENTATION-SUMMARY.md` | What changed in v2.1 |

---

## Old File Location

The superseded v2.0 testing guide has been renamed:
- **Old Name:** `ccow-v2-testing-guide.md`
- **New Name:** `ccow-v2-testing-guide.md.SUPERSEDED`
- **Location:** `docs/guide/`

**Preserved for:**
- Historical reference
- Understanding the evolution from v2.0 to v2.1
- CORS workaround documentation (incorporated into v2.1)

---

## Questions?

If you have questions about:
- **v2.1 Testing:** See `ccow-v2.1-testing-guide.md`
- **v2.1 Design:** See `ccow-multi-user-enhancement.md` (Section 14)
- **Migration:** See `CCOW-V2.1-IMPLEMENTATION-SUMMARY.md`

---

**Recommendation:** Delete this README and the `.SUPERSEDED` file after 30 days if no longer needed.

---

**End of Document**
