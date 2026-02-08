// Custom JavaScript

console.log("Custom JS loaded successfully.");

document.addEventListener("DOMContentLoaded", () => {
    const layout = document.querySelector(".layout");
    const toggleBtn = document.querySelector("[data-toggle-sidebar]");

    if (!layout) {
        console.error("Layout element not found!");
        return;
    }

    // Sidebar state management with localStorage
    const SIDEBAR_STATE_KEY = 'med-z1-sidebar-collapsed';

    function toggleSidebar() {
        layout.classList.toggle("layout--sidebar-collapsed");

        // Save state to localStorage
        const isCollapsed = layout.classList.contains("layout--sidebar-collapsed");
        localStorage.setItem(SIDEBAR_STATE_KEY, isCollapsed ? 'true' : 'false');
    }

    // Restore saved sidebar state on page load
    function restoreSidebarState() {
        const savedState = localStorage.getItem(SIDEBAR_STATE_KEY);

        if (savedState === 'true') {
            layout.classList.add("layout--sidebar-collapsed");
        }

        // Remove temporary init class from html element (used to prevent FOUC)
        document.documentElement.classList.remove('sidebar-init-collapsed');

        // If savedState is null (first visit) or 'false', sidebar stays expanded (default)
    }

    // Apply saved state immediately on page load
    restoreSidebarState();

    // Click on the hamburger button
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            toggleSidebar();
        });
    }

    // Keyboard shortcut: Cmd+B (macOS) or Ctrl+B (Win/Linux)
    document.addEventListener("keydown", (event) => {
        // Don't hijack the shortcut when user is typing in a form field
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

            // If opening patient flags modal, trigger HTMX content load
            if (modalId === 'patient-flags-modal') {
                document.body.dispatchEvent(new CustomEvent('loadFlagsContent'));
            }

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

// Close modal after successful patient selection and update flags button
document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.detail.target.id === 'patient-header-container') {
        // Close patient search modal if open
        const searchModal = document.getElementById('patient-search-modal');
        if (searchModal && searchModal.style.display === 'flex') {
            searchModal.style.display = 'none';
            document.body.style.overflow = '';
        }

        // Check if a patient is now selected
        const patientHeader = e.detail.target.querySelector('.patient-header--active');
        const flagsBtn = document.getElementById('btn-patient-flags');

        if (patientHeader && flagsBtn) {
            // Patient is selected - enable flags button
            flagsBtn.disabled = false;

            // Fetch flag count and update badge
            updateFlagBadge();

            // Refresh dashboard widgets if on dashboard page
            refreshDashboardWidgets();
        } else if (flagsBtn) {
            // No patient selected - disable flags button and hide badge
            flagsBtn.disabled = true;
            const badge = document.getElementById('flags-badge');
            if (badge) {
                badge.style.display = 'none';
            }

            // Reload dashboard page if on dashboard (to show empty state)
            const dashboardWidgets = document.getElementById('dashboard-widgets');
            if (dashboardWidgets) {
                window.location.reload();
            }
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
   Patient Flags Badge Management
   ============================================ */

/**
 * Extract current patient ICN from the patient header
 * @returns {string|null} Patient ICN or null if no patient selected
 */
function getCurrentPatientICN() {
    const patientHeader = document.querySelector('.patient-header--active');
    if (!patientHeader) return null;

    // Check the element itself for data attribute
    if (patientHeader.hasAttribute('data-patient-icn')) {
        return patientHeader.getAttribute('data-patient-icn');
    }

    // Fallback: extract from text content (e.g., "ICN: ICN100001")
    const textContent = patientHeader.textContent;
    const icnMatch = textContent.match(/ICN:\s*(ICN\d+)/);
    if (icnMatch) {
        return icnMatch[1];
    }

    return null;
}

/**
 * Fetch flag count from API and update the badge display
 */
function updateFlagBadge() {
    const icn = getCurrentPatientICN();
    if (!icn) {
        console.warn('Cannot update flag badge: no patient ICN found');
        return;
    }

    fetch(`/api/patient/${icn}/flags`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`API returned ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            const badge = document.getElementById('flags-badge');
            if (!badge) return;

            if (data.active_flags > 0) {
                // Show badge with count
                badge.textContent = data.active_flags;
                badge.style.display = 'inline';

                // Set badge color: red for overdue, yellow otherwise
                if (data.overdue_count > 0) {
                    badge.classList.add('badge--danger');
                    badge.classList.remove('badge--warning');
                } else {
                    badge.classList.add('badge--warning');
                    badge.classList.remove('badge--danger');
                }
            } else {
                // Hide badge if no flags
                badge.style.display = 'none';
            }
        })
        .catch(err => {
            console.error('Failed to fetch flag count:', err);
            // Hide badge on error
            const badge = document.getElementById('flags-badge');
            if (badge) {
                badge.style.display = 'none';
            }
        });
}

/* ============================================
   Dashboard Widget Refresh
   ============================================ */

/**
 * Refresh all dashboard widgets when patient context changes
 * Only runs if we're currently on the dashboard page
 */
function refreshDashboardWidgets() {
    // Check if we're on the dashboard page
    const dashboardContainer = document.querySelector('.dashboard');
    if (!dashboardContainer) {
        // Not on dashboard page, nothing to refresh
        return;
    }

    const dashboardWidgets = document.getElementById('dashboard-widgets');

    // If on dashboard but showing empty state, reload entire page to show widgets
    if (!dashboardWidgets) {
        console.log('Dashboard in empty state - reloading page to show widgets');
        window.location.reload();
        return;
    }

    // Dashboard is showing widgets - refresh them with new patient data
    const icn = getCurrentPatientICN();
    if (!icn) {
        console.warn('Cannot refresh dashboard: no patient ICN found');
        return;
    }

    // Update dashboard subtitle with new patient name
    const patientHeaderTitle = document.querySelector('.patient-header__title');
    const dashboardSubtitle = document.querySelector('.dashboard-header__subtitle');
    if (patientHeaderTitle && dashboardSubtitle) {
        const patientName = patientHeaderTitle.textContent.trim();
        dashboardSubtitle.textContent = `Clinical summary for ${patientName}`;
    }

    // Find all widgets with HTMX hx-get attributes (functional widgets)
    const widgets = dashboardWidgets.querySelectorAll('[hx-get]');

    widgets.forEach(widget => {
        const getUrl = widget.getAttribute('hx-get');

        // Update the URL with the new patient ICN
        const newUrl = getUrl.replace(/\/[^\/]+$/, `/${icn}`);
        widget.setAttribute('hx-get', newUrl);

        // Show loading spinner
        widget.innerHTML = '<div class="widget__body"><div class="widget__spinner"></div></div>';

        // Use fetch() to reload widget content (more reliable than htmx.ajax in HTMX 1.9)
        fetch(newUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(html => {
                widget.innerHTML = html;
                console.log(`Widget ${widget.id} refreshed successfully`);
            })
            .catch(err => {
                console.error(`Failed to refresh widget ${widget.id}:`, err);
                widget.innerHTML = `
                    <div class="widget__body">
                        <p class="text-danger">
                            <i class="fa-solid fa-triangle-exclamation"></i>
                            Failed to load widget
                        </p>
                    </div>
                `;
            });
    });

    console.log(`Dashboard refreshed for patient ${icn}: ${widgets.length} widgets reloaded`);
}

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

// ============================================
// Problem Detail Modal
// ============================================

function openProblemDetail(problemId, icn) {
    const modal = document.getElementById('problem-detail-modal');
    const content = document.getElementById('problem-detail-content');

    if (modal && content) {
        // Show modal
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Show loading spinner
        content.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p class="text-muted">Loading problem details...</p>
            </div>
        `;

        // Fetch problem detail content
        const url = `/api/patient/${icn}/problems/${problemId}/detail`;
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(html => {
                content.innerHTML = html;
                console.log(`Problem ${problemId} details loaded successfully`);
            })
            .catch(err => {
                console.error(`Failed to load problem ${problemId} details:`, err);
                content.innerHTML = `
                    <div class="alert alert--error">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        Failed to load problem details: ${err.message}
                    </div>
                `;
            });

        // Focus management
        setTimeout(() => {
            const firstInput = modal.querySelector('input, button');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}
