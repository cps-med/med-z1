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
