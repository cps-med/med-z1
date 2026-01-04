/**
 * Clinical Insights Transcript Download
 *
 * Client-side transcript generation for AI Clinical Insights conversations.
 * Generates plaintext and markdown formats with PHI warnings and metadata.
 *
 * Key Functions:
 * - downloadTranscript(format) - Main entry point, triggers download
 * - collectChatMessages() - Extracts conversation from DOM
 * - generatePlaintextTranscript() - Formats as .txt file
 * - generateMarkdownTranscript() - Formats as .md file
 *
 * File Naming: clinical_insights_ICN{patient_icn}_{timestamp}.{ext}
 * Example: clinical_insights_ICN100001_20260103_143205.txt
 */

/**
 * Collect all chat messages from the DOM
 * Returns array of message objects with type, text, timestamp, and tools
 */
function collectChatMessages() {
    const messages = [];
    const chatHistory = document.getElementById('chat-history');

    if (!chatHistory) {
        console.warn('Chat history container not found');
        return messages;
    }

    // Find all chat message elements
    const messageElements = chatHistory.querySelectorAll('.chat-message');

    messageElements.forEach(element => {
        const message = {};

        // Determine message type
        if (element.classList.contains('chat-message--user')) {
            message.type = 'user';
        } else if (element.classList.contains('chat-message--ai')) {
            message.type = 'ai';
        } else if (element.classList.contains('chat-message--system')) {
            message.type = 'system';
        } else {
            message.type = 'unknown';
        }

        // Extract message text
        const textElement = element.querySelector('.chat-message__text');
        if (textElement) {
            message.text = textElement.textContent.trim();
        } else {
            message.text = '';
        }

        // Extract timestamp if available
        const timestampElement = element.querySelector('.chat-message__timestamp');
        if (timestampElement) {
            message.timestamp = timestampElement.textContent.trim();
        }

        // Extract tools/sources for AI messages
        if (message.type === 'ai') {
            const metadataElement = element.querySelector('.chat-message__metadata');
            if (metadataElement) {
                const metadataText = metadataElement.textContent.trim();
                // Extract "Sources checked: tool1, tool2, tool3"
                const match = metadataText.match(/Sources checked:\s*(.+)/);
                if (match) {
                    message.tools = match[1].trim();
                }
            }
        }

        messages.push(message);
    });

    return messages;
}

/**
 * Generate metadata header (patient, clinician, timestamp)
 * Returns object with patient ICN, name, and current timestamp
 */
function generateMetadata() {
    const metadata = {};

    // Extract patient ICN from hidden input
    const icnInput = document.querySelector('input[name="icn"]');
    if (icnInput) {
        metadata.patientIcn = icnInput.value;
    } else {
        metadata.patientIcn = 'Unknown';
    }

    // Extract patient name from page title
    const pageTitle = document.title;
    const nameMatch = pageTitle.match(/AI Insights - (.+)/);
    if (nameMatch) {
        metadata.patientName = nameMatch[1];
    } else {
        metadata.patientName = 'Unknown Patient';
    }

    // Current timestamp
    const now = new Date();
    metadata.timestamp = now.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });

    // Timestamp for filename (YYYYMMDD_HHMMSS)
    metadata.filenameTimestamp = now.getFullYear().toString() +
        (now.getMonth() + 1).toString().padStart(2, '0') +
        now.getDate().toString().padStart(2, '0') + '_' +
        now.getHours().toString().padStart(2, '0') +
        now.getMinutes().toString().padStart(2, '0') +
        now.getSeconds().toString().padStart(2, '0');

    // Clinician email (from authenticated user session)
    const clinicianEmailInput = document.getElementById('clinician-email');
    if (clinicianEmailInput) {
        metadata.clinician = clinicianEmailInput.value;
    } else {
        metadata.clinician = 'unknown@va.gov';  // Fallback if not found
    }

    // Session ID (use browser-generated random ID)
    if (!sessionStorage.getItem('transcript_session_id')) {
        sessionStorage.setItem('transcript_session_id',
            'session_' + Math.random().toString(36).substring(2, 15));
    }
    metadata.sessionId = sessionStorage.getItem('transcript_session_id');

    return metadata;
}

/**
 * Generate PHI/HIPAA disclaimer footer
 */
function generateDisclaimer() {
    return `
========================================
IMPORTANT NOTICE
========================================

This transcript contains Protected Health Information (PHI) subject to
federal privacy regulations under HIPAA and VA policies.

SECURITY REQUIREMENTS:
- Store on encrypted, VA-approved devices only
- Do NOT share via unsecured channels (email, text, cloud storage)
- Delete when no longer clinically necessary
- Follow all VA and HIPAA data handling policies

CLINICAL DISCLAIMER:
This transcript is for clinical reference and documentation purposes only.
All AI-generated insights must be verified before making clinical decisions.

AI-generated content should be used for decision support, not as a
substitute for professional medical judgment.

Generated by: Med-Z1 AI Clinical Insights
Date: ${new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
})}
`.trim();
}

/**
 * Generate plaintext transcript
 */
function generatePlaintextTranscript() {
    const metadata = generateMetadata();
    const messages = collectChatMessages();

    if (messages.length === 0) {
        alert('No messages to export. Start a conversation first.');
        return null;
    }

    // Build header
    let transcript = `========================================
AI CLINICAL INSIGHTS TRANSCRIPT
========================================

Generated: ${metadata.timestamp}
Patient: ${metadata.patientName} (ICN: ${metadata.patientIcn})
Clinician: ${metadata.clinician}
Session ID: ${metadata.sessionId}

========================================

`;

    // Add messages
    messages.forEach(msg => {
        const prefix = msg.type === 'user' ? 'USER:' :
                      msg.type === 'ai' ? 'AI:' :
                      msg.type === 'system' ? 'SYSTEM:' : 'MESSAGE:';

        // Add timestamp if available
        const timestampStr = msg.timestamp ? `[${msg.timestamp}] ` : '';

        transcript += `${timestampStr}${prefix}\n${msg.text}\n`;

        // Add tools/sources for AI messages
        if (msg.tools) {
            transcript += `\nSources Checked: ${msg.tools}\n`;
        }

        transcript += '\n';
    });

    // Add disclaimer footer
    transcript += '\n' + generateDisclaimer();

    return transcript;
}

/**
 * Generate markdown transcript
 */
function generateMarkdownTranscript() {
    const metadata = generateMetadata();
    const messages = collectChatMessages();

    if (messages.length === 0) {
        alert('No messages to export. Start a conversation first.');
        return null;
    }

    // Build header
    let transcript = `# AI Clinical Insights Transcript

---

**Generated:** ${metadata.timestamp}
**Patient:** ${metadata.patientName} (ICN: ${metadata.patientIcn})
**Clinician:** ${metadata.clinician}
**Session ID:** ${metadata.sessionId}

---

## Conversation

`;

    // Add messages
    messages.forEach((msg, index) => {
        // Determine header and icon
        let header, icon;
        if (msg.type === 'user') {
            header = '👤 User';
        } else if (msg.type === 'ai') {
            header = '🤖 AI Assistant';
        } else if (msg.type === 'system') {
            header = '⚙️ System';
        } else {
            header = '💬 Message';
        }

        // Add timestamp if available
        const timestampStr = msg.timestamp ? ` _(${msg.timestamp})_` : '';

        transcript += `### ${header}${timestampStr}\n\n`;
        transcript += `${msg.text}\n`;

        // Add tools/sources for AI messages
        if (msg.tools) {
            transcript += `\n**Sources Checked:** ${msg.tools}\n`;
        }

        transcript += '\n';
    });

    // Add disclaimer footer
    transcript += `---

## Important Notice

> ⚠️ **Protected Health Information (PHI)**
>
> This transcript contains PHI subject to federal privacy regulations under HIPAA and VA policies.

### Security Requirements

- Store on encrypted, VA-approved devices only
- Do NOT share via unsecured channels (email, text, cloud storage)
- Delete when no longer clinically necessary
- Follow all VA and HIPAA data handling policies

### Clinical Disclaimer

This transcript is for clinical reference and documentation purposes only.
**All AI-generated insights must be verified before making clinical decisions.**

AI-generated content should be used for decision support, not as a substitute for professional medical judgment.

---

*Generated by: Med-Z1 AI Clinical Insights*
*Date: ${new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
})}*
`;

    return transcript;
}

/**
 * Download file to user's computer
 *
 * @param {string} content - File content
 * @param {string} filename - Filename (without extension)
 * @param {string} mimeType - MIME type (text/plain or text/markdown)
 * @param {string} extension - File extension (.txt or .md)
 */
function downloadFile(content, filename, mimeType, extension) {
    // Create blob
    const blob = new Blob([content], { type: mimeType });

    // Create download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.${extension}`;

    // Trigger download
    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Main download function - triggered by modal buttons
 *
 * @param {string} format - 'text' or 'markdown'
 */
function downloadTranscript(format) {
    const metadata = generateMetadata();

    // Generate filename: clinical_insights_ICN{patient_icn}_{timestamp}
    const filename = `clinical_insights_${metadata.patientIcn}_${metadata.filenameTimestamp}`;

    let content, mimeType, extension;

    if (format === 'text') {
        content = generatePlaintextTranscript();
        mimeType = 'text/plain';
        extension = 'txt';
    } else if (format === 'markdown') {
        content = generateMarkdownTranscript();
        mimeType = 'text/markdown';
        extension = 'md';
    } else {
        console.error(`Unknown format: ${format}`);
        alert('Invalid download format');
        return;
    }

    // Check if content was generated successfully
    if (!content) {
        return; // Error already shown by generate functions
    }

    // Download file
    downloadFile(content, filename, mimeType, extension);

    // Close modal
    const modal = document.getElementById('transcript-download-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    console.log(`Downloaded ${format} transcript: ${filename}.${extension}`);
}
