"""
Unit tests for multi-user CCOW Context Vault (v2.0)

Tests the core ContextVault class with multi-user context isolation,
ensuring each user maintains independent patient contexts.

Run with: pytest scripts/test_vault_multiuser.py -v
"""

import pytest
from datetime import datetime, timezone, timedelta
from ccow.vault import vault, ContextVault
from ccow.models import PatientContext, ContextHistoryEntry


class TestMultiUserContextVault:
    """Test suite for multi-user context vault operations."""

    def setup_method(self):
        """Reset vault state before each test."""
        # Create fresh vault instance for each test
        self.vault = ContextVault(max_history=100, cleanup_threshold_hours=24)

        # Test user identities
        self.user1_id = "user-uuid-1111"
        self.user1_email = "clinician.alpha@va.gov"

        self.user2_id = "user-uuid-2222"
        self.user2_email = "clinician.beta@va.gov"

        self.user3_id = "user-uuid-3333"
        self.user3_email = "clinician.gamma@va.gov"

        # Test patient ICNs
        self.patient1_icn = "1012853550V207686"
        self.patient2_icn = "1012853551V207687"
        self.patient3_icn = "1012853552V207688"

    def test_initial_state_empty(self):
        """Vault should start with no contexts."""
        assert self.vault.get_context_count() == 0
        assert self.vault.get_all_contexts() == []
        assert self.vault.get_context(self.user1_id) is None

    def test_set_context_single_user(self):
        """Setting context for one user should work."""
        context = self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        assert context.user_id == self.user1_id
        assert context.email == self.user1_email
        assert context.patient_id == self.patient1_icn
        assert context.set_by == "med-z1"
        assert isinstance(context.set_at, datetime)
        assert isinstance(context.last_accessed_at, datetime)
        assert self.vault.get_context_count() == 1

    def test_get_context_single_user(self):
        """Getting context for a user should return their context."""
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        retrieved = self.vault.get_context(self.user1_id)
        assert retrieved is not None
        assert retrieved.user_id == self.user1_id
        assert retrieved.patient_id == self.patient1_icn

    def test_context_isolation_between_users(self):
        """Each user should have independent context."""
        # User 1 sets patient A
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        # User 2 sets patient B
        self.vault.set_context(
            user_id=self.user2_id,
            patient_id=self.patient2_icn,
            set_by="med-z1",
            email=self.user2_email
        )

        # User 3 sets patient C
        self.vault.set_context(
            user_id=self.user3_id,
            patient_id=self.patient3_icn,
            set_by="med-z1",
            email=self.user3_email
        )

        # Each user should see their own context
        assert self.vault.get_context(self.user1_id).patient_id == self.patient1_icn
        assert self.vault.get_context(self.user2_id).patient_id == self.patient2_icn
        assert self.vault.get_context(self.user3_id).patient_id == self.patient3_icn

        # Total count should be 3
        assert self.vault.get_context_count() == 3

    def test_update_context_same_user(self):
        """User changing their patient should update their context."""
        # User 1 initially sets patient A
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        # User 1 changes to patient B
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient2_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        # Should have only one context (updated, not duplicate)
        assert self.vault.get_context_count() == 1
        assert self.vault.get_context(self.user1_id).patient_id == self.patient2_icn

    def test_clear_context_single_user(self):
        """Clearing context for one user should not affect others."""
        # Set contexts for two users
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )
        self.vault.set_context(
            user_id=self.user2_id,
            patient_id=self.patient2_icn,
            set_by="med-z1",
            email=self.user2_email
        )

        # Clear user 1's context
        cleared = self.vault.clear_context(
            user_id=self.user1_id,
            cleared_by="med-z1",
            email=self.user1_email
        )

        assert cleared is True
        assert self.vault.get_context(self.user1_id) is None
        assert self.vault.get_context(self.user2_id) is not None
        assert self.vault.get_context_count() == 1

    def test_clear_nonexistent_context(self):
        """Clearing a non-existent context should return False."""
        cleared = self.vault.clear_context(
            user_id="nonexistent-user",
            cleared_by="med-z1"
        )

        assert cleared is False

    def test_history_tracking_set_events(self):
        """Setting contexts should create history entries."""
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        history = self.vault.get_history(user_id=self.user1_id, scope="user")
        assert len(history) == 1
        assert history[0].action == "set"
        assert history[0].user_id == self.user1_id
        assert history[0].email == self.user1_email
        assert history[0].patient_id == self.patient1_icn
        assert history[0].actor == "med-z1"

    def test_history_tracking_clear_events(self):
        """Clearing contexts should create history entries."""
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        self.vault.clear_context(
            user_id=self.user1_id,
            cleared_by="med-z1",
            email=self.user1_email
        )

        history = self.vault.get_history(user_id=self.user1_id, scope="user")
        assert len(history) == 2
        assert history[0].action == "set"
        assert history[1].action == "clear"
        assert history[1].patient_id is None

    def test_history_user_scope(self):
        """User-scoped history should only show that user's events."""
        # User 1 sets context
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        # User 2 sets context
        self.vault.set_context(
            user_id=self.user2_id,
            patient_id=self.patient2_icn,
            set_by="med-z1",
            email=self.user2_email
        )

        # User 1's history should only show user 1 events
        user1_history = self.vault.get_history(user_id=self.user1_id, scope="user")
        assert len(user1_history) == 1
        assert all(entry.user_id == self.user1_id for entry in user1_history)

    def test_history_global_scope(self):
        """Global-scoped history should show all users' events."""
        # User 1 sets context
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        # User 2 sets context
        self.vault.set_context(
            user_id=self.user2_id,
            patient_id=self.patient2_icn,
            set_by="med-z1",
            email=self.user2_email
        )

        # Global history should show both users
        global_history = self.vault.get_history(user_id=None, scope="global")
        assert len(global_history) == 2
        user_ids = {entry.user_id for entry in global_history}
        assert user_ids == {self.user1_id, self.user2_id}

    def test_last_accessed_at_updates(self):
        """Getting context should update last_accessed_at timestamp."""
        # Set context
        context1 = self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        original_time = context1.last_accessed_at

        # Small delay to ensure time difference
        import time
        time.sleep(0.01)

        # Get context (should update last_accessed_at)
        context2 = self.vault.get_context(self.user1_id)

        assert context2.last_accessed_at > original_time

    def test_cleanup_stale_contexts(self):
        """Stale contexts should be removed by cleanup."""
        # Create a vault with 1-hour cleanup threshold for testing
        test_vault = ContextVault(max_history=100, cleanup_threshold_hours=1)

        # Set context for user 1
        test_vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        # Manually set last_accessed_at to 2 hours ago (stale)
        with test_vault._lock:
            if self.user1_id in test_vault._contexts:
                context = test_vault._contexts[self.user1_id]
                # Create new context with old timestamp
                from ccow.models import PatientContext
                stale_context = PatientContext(
                    user_id=context.user_id,
                    email=context.email,
                    patient_id=context.patient_id,
                    set_by=context.set_by,
                    set_at=context.set_at,
                    last_accessed_at=datetime.now(timezone.utc) - timedelta(hours=2)
                )
                test_vault._contexts[self.user1_id] = stale_context

        # Set fresh context for user 2
        test_vault.set_context(
            user_id=self.user2_id,
            patient_id=self.patient2_icn,
            set_by="med-z1",
            email=self.user2_email
        )

        # Run cleanup
        removed_count = test_vault.cleanup_stale_contexts()

        # User 1's stale context should be removed, user 2's should remain
        assert removed_count == 1
        assert test_vault.get_context(self.user1_id) is None
        assert test_vault.get_context(self.user2_id) is not None

    def test_get_all_contexts(self):
        """Getting all contexts should return list of all active contexts."""
        # Set contexts for multiple users
        self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )
        self.vault.set_context(
            user_id=self.user2_id,
            patient_id=self.patient2_icn,
            set_by="med-z1",
            email=self.user2_email
        )

        all_contexts = self.vault.get_all_contexts()
        assert len(all_contexts) == 2
        user_ids = {ctx.user_id for ctx in all_contexts}
        assert user_ids == {self.user1_id, self.user2_id}

    def test_context_persistence_across_updates(self):
        """Context should maintain set_at timestamp across updates."""
        # Set initial context
        context1 = self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        original_set_at = context1.set_at

        import time
        time.sleep(0.01)

        # Update to different patient
        context2 = self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient2_icn,
            set_by="med-z1",
            email=self.user1_email
        )

        # set_at should be updated (new context created)
        assert context2.set_at > original_set_at
        assert context2.patient_id == self.patient2_icn

    def test_thread_safety_concurrent_operations(self):
        """Vault should handle concurrent operations safely."""
        import threading

        def set_user_context(user_id, patient_id, email):
            for _ in range(10):
                self.vault.set_context(
                    user_id=user_id,
                    patient_id=patient_id,
                    set_by="med-z1",
                    email=email
                )

        # Create threads for 3 users
        threads = [
            threading.Thread(
                target=set_user_context,
                args=(self.user1_id, self.patient1_icn, self.user1_email)
            ),
            threading.Thread(
                target=set_user_context,
                args=(self.user2_id, self.patient2_icn, self.user2_email)
            ),
            threading.Thread(
                target=set_user_context,
                args=(self.user3_id, self.patient3_icn, self.user3_email)
            ),
        ]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Should have exactly 3 contexts (one per user)
        assert self.vault.get_context_count() == 3
        assert self.vault.get_context(self.user1_id).patient_id == self.patient1_icn
        assert self.vault.get_context(self.user2_id).patient_id == self.patient2_icn
        assert self.vault.get_context(self.user3_id).patient_id == self.patient3_icn

    def test_history_max_length_enforcement(self):
        """History should respect max_history limit."""
        # Create vault with small history limit
        small_vault = ContextVault(max_history=5, cleanup_threshold_hours=24)

        # Create 10 events
        for i in range(10):
            small_vault.set_context(
                user_id=self.user1_id,
                patient_id=f"patient-{i}",
                set_by="med-z1",
                email=self.user1_email
            )

        # Should only have 5 most recent events
        history = small_vault.get_history(user_id=None, scope="global")
        assert len(history) <= 5

    def test_email_optional(self):
        """Email should be optional in context operations."""
        # Set context without email
        context = self.vault.set_context(
            user_id=self.user1_id,
            patient_id=self.patient1_icn,
            set_by="med-z1",
            email=None
        )

        assert context.email is None
        assert context.user_id == self.user1_id

        # Clear context without email
        cleared = self.vault.clear_context(
            user_id=self.user1_id,
            cleared_by="med-z1",
            email=None
        )

        assert cleared is True
