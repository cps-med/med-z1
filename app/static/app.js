// Custom JavaScript

console.log("Custom JS loaded successfully.");

document.addEventListener("DOMContentLoaded", () => {
    const layout = document.querySelector(".layout");
    const toggleBtn = document.querySelector("[data-toggle-sidebar]");

    if (!layout) return;

    function toggleSidebar() {
        layout.classList.toggle("layout--sidebar-collapsed");
    }

    // Click on the hamburger button
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            toggleSidebar();
        });
    }

    // Keyboard shortcut: Cmd+B (macOS) or Ctrl+B (Win/Linux)
    document.addEventListener("keydown", (event) => {
        // Don’t hijack the shortcut when user is typing in a form field
        const tag = event.target.tagName.toLowerCase();
        if (
            tag === "input" ||
            tag === "textarea" ||
            event.target.isContentEditable
        ) {
            return;
        }

        const isBKey = event.key && event.key.toLowerCase() === "b";
        const hasModifier = event.metaKey || event.ctrlKey; // meta = Cmd on macOS, ctrl = Ctrl on Win/Linux

        if (isBKey && hasModifier && !event.altKey && !event.shiftKey) {
            event.preventDefault(); // avoid any browser default behavior
            toggleSidebar();
        }
    });
});

/* ============================================
   Modal Handling
   ============================================ */

// Open modal
document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-modal-open]');
    if (trigger) {
        const modalId = trigger.getAttribute('data-modal-open');
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent background scroll

            // Focus first input if exists
            const firstInput = modal.querySelector('input, button');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }
});

// Close modal
document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-modal-close]');
    if (trigger) {
        const modalId = trigger.getAttribute('data-modal-close');
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // Restore scroll
        }
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal[style*="display: flex"]');
        modals.forEach(modal => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        });
    }
});

/* ============================================
   HTMX Event Listeners for Modal Integration
   ============================================ */

// Close modal after successful patient selection
document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.detail.target.id === 'patient-header-container') {
        // Close patient search modal if open
        const searchModal = document.getElementById('patient-search-modal');
        if (searchModal && searchModal.style.display === 'flex') {
            searchModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
});

// Clear search input when modal closes
document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-modal-close="patient-search-modal"]');
    if (trigger) {
        const searchInput = document.getElementById('search-query');
        if (searchInput) {
            searchInput.value = '';
        }
        const resultsDiv = document.getElementById('search-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = '<p class="text-muted">Enter search criteria above</p>';
        }
    }
});

/* ============================================
   Search Result Keyboard Navigation
   ============================================ */

document.addEventListener('keydown', (e) => {
    // Handle Enter key on search result items
    if (e.key === 'Enter' && e.target.classList.contains('search-result-item')) {
        e.target.click();
    }
});

/* ============================================
   Debug Helpers (Development Only)
   ============================================ */

// Log HTMX requests in console (helpful for debugging)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    document.body.addEventListener('htmx:beforeRequest', (e) => {
        console.log('HTMX Request:', e.detail.requestConfig.verb, e.detail.requestConfig.path);
    });

    document.body.addEventListener('htmx:afterSwap', (e) => {
        console.log('HTMX Swap complete:', e.detail.target.id);
    });

    document.body.addEventListener('htmx:responseError', (e) => {
        console.error('HTMX Error:', e.detail);
    });
}
