// assets/js/agent-ui.js
import { apiFetch } from './api.js';
import { showToast } from './ui-utils.js';

export function initAgent(elements) {
    // Event Listeners
    elements.analyzeBtn.onclick = () => analyzeManuscript(elements);
    elements.deepBtn.onclick = () => polishByClaude(elements);
    elements.exportBtn.onclick = () => generatePDF(elements);
    elements.copyBtn.onclick = () => copyRefined(elements);
    
    document.getElementById('logout-btn').onclick = () => {
        localStorage.removeItem('lyricai_token');
        window.location.href = 'registration.html';
    };

    // Load initial data from localStorage
    loadInitialData(elements);
}

function loadInitialData(elements) {
    const title = localStorage.getItem("lyricai_title") || "Untitled";
    const original = localStorage.getItem("lyricai_original") || "";
    const translation = localStorage.getItem("lyricai_translation") || "";
    const refined = localStorage.getItem("lyricai_refined") || "";

    elements.songTitleDisplay.innerText = title;
    
    // The "Manuscript" in Agent is the Translation from Editor
    elements.originalBody.innerText = translation || "No translation found. Please analyze in Editor first.";
    
    // Populate the original reference for comparison if the element exists
    const originalContent = document.getElementById('original-content');
    if (originalContent) originalContent.innerText = original;

    if (refined) {
        elements.resultBody.innerHTML = refined.split('\n').map(l => `<p>${l}</p>`).join('');
        const lastMethod = localStorage.getItem("lyricai_last_refined_method") || "Claude";
        updateStatusBadge(lastMethod === "Claude" ? "Polished by Claude" : "Verified by Rocinante");
    }

    updateHarmonyDisplay();
}

function updateHarmonyDisplay() {
    const key = localStorage.getItem("lyricai_key");
    const bpm = localStorage.getItem("lyricai_bpm");
    const verse = localStorage.getItem("lyricai_chords_verse");
    const chorus = localStorage.getItem("lyricai_chords_chorus");

    document.getElementById('harmony-key').innerText = key || "Awaiting harmony...";
    document.getElementById('harmony-bpm').innerText = (bpm || "0") + " BPM";
    document.getElementById('chords-verse').innerText = verse || "---";
    document.getElementById('chords-chorus').innerText = chorus || "---";
}

function updateStatusBadge(text) {
    const statusCheck = document.getElementById('status-check');
    if (statusCheck) {
        statusCheck.classList.remove('hidden');
        statusCheck.style.display = 'flex';
        statusCheck.innerHTML = `<span class="material-symbols-outlined text-green-600 text-xs">verified</span> <span class="text-[10px] font-bold text-green-600 uppercase">${text}</span>`;
    }
}

function formatResultText(val) {
    if (!val) return "";
    let text = "";
    
    if (typeof val === 'string') {
        text = val;
    } else if (Array.isArray(val)) {
        text = val.map(item => (typeof item === 'object' ? JSON.stringify(item) : item)).join("\n");
    } else if (typeof val === 'object') {
        const commonKeys = ['poetDraft', 'editor_output', 'text', 'result', 'output', 'translation'];
        let found = false;
        for (let key of commonKeys) {
            if (val[key] && typeof val[key] === 'string') {
                text = val[key];
                found = true;
                break;
            }
        }
        if (!found) text = JSON.stringify(val, null, 2);
    } else {
        text = String(val);
    }

    // Convert to paragraphs for display
    return text.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0 || line === "")
        .map(line => `<p class="min-h-[1em]">${line}</p>`)
        .join('');
}

async function analyzeManuscript(elements) {
    const original = localStorage.getItem("lyricai_original");
    const translation = localStorage.getItem("lyricai_translation");
    const structure = localStorage.getItem("lyricai_structure") || "";
    const mood = localStorage.getItem("lyricai_mood") || "";
    const metaphors = localStorage.getItem("lyricai_metaphors") || "";
    
    if (!original) return showToast("No lyrics found! Analyze in Editor first.", "error");

    elements.analyzeBtn.disabled = true;
    const originalHtml = elements.analyzeBtn.innerHTML;
    elements.analyzeBtn.innerHTML = `<span class="material-symbols-outlined animate-spin text-sm">sync</span> ANALYZING...`;
    
    // Clear previous results and show loading state in the box
    elements.resultBody.innerHTML = `<div class="flex items-center justify-center h-full text-slate-400 animate-pulse">Generative processing...</div>`;

    try {
        // 1. Get Harmony (Euryale-70b)
        const harmonyPromise = apiFetch('/webhook/analyze-harmony', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lyrics: original })
        });

        // 2. Get Poet Draft (Rocinante-12b)
        const poetPromise = apiFetch('/webhook/poet-agent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                originalLyrics: original,
                analysis: `${structure}\n${mood}`,
                metaphors: metaphors,
                bridge: "", 
                targetLanguage: localStorage.getItem("lyricai_targetLang") || "English",
                literalTranslation: translation || ""
            })
        });

        const [hRes, pRes] = await Promise.all([harmonyPromise, poetPromise]);

        if (hRes.ok) {
            const hData = await hRes.json();
            localStorage.setItem("lyricai_key", hData.key || "");
            localStorage.setItem("lyricai_bpm", hData.bpm || "0");
            localStorage.setItem("lyricai_chords_verse", hData.chords_verse || "");
            localStorage.setItem("lyricai_chords_chorus", hData.chords_chorus || "");
            updateHarmonyDisplay();
        }

        if (pRes.ok) {
            const pData = await pRes.json();
            const draft = pData.poetDraft || pData.result || pData.output || "";
            
            elements.resultBody.innerHTML = formatResultText(draft);
            localStorage.setItem("lyricai_refined", typeof draft === 'string' ? draft : JSON.stringify(draft));
            localStorage.setItem("lyricai_last_refined_method", "Rocinante");
            updateStatusBadge("Verified by Rocinante");
            showToast("Manuscript analyzed by Rocinante & Euryale", "success");
        } else {
            const err = await pRes.json().catch(() => ({}));
            throw new Error(err.detail || "Rocinante agent failed to respond.");
        }

    } catch (err) {
        showToast(err.message, "error");
        elements.resultBody.innerHTML = `<p class="text-red-500 italic">Error: ${err.message}</p>`;
    } finally {
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.innerHTML = originalHtml;
    }
}

async function polishByClaude(elements) {
    const refined = localStorage.getItem("lyricai_refined");
    const translation = localStorage.getItem("lyricai_translation");
    
    const textToPolish = refined || translation;
    
    if (!textToPolish) return showToast("No manuscript to polish! Run analysis first.", "error");

    elements.deepBtn.disabled = true;
    const originalHtml = elements.deepBtn.innerHTML;
    elements.deepBtn.innerHTML = `<span class="material-symbols-outlined animate-spin text-sm">sync</span> POLISHING...`;

    try {
        const response = await apiFetch('/webhook/literary-editor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                poetDraft: textToPolish,
                structure: localStorage.getItem("lyricai_structure") || "",
                mood: localStorage.getItem("lyricai_mood") || "",
                targetLanguage: localStorage.getItem("lyricai_targetLang") || "English"
            })
        });

        if (response.ok) {
            const data = await response.json();
            const output = data.editor_output || data.result || data.output || "";
            
            elements.resultBody.innerHTML = formatResultText(output);
            localStorage.setItem("lyricai_refined", typeof output === 'string' ? output : JSON.stringify(output));
            localStorage.setItem("lyricai_last_refined_method", "Claude");
            updateStatusBadge("Polished by Claude");
            showToast("Polished by Claude", "success");
        } else {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || "Claude polish failed.");
        }
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        elements.deepBtn.disabled = false;
        elements.deepBtn.innerHTML = originalHtml;
    }
}

function copyRefined(elements) {
    const text = elements.resultBody.innerText;
    if (!text || text.includes("Awaiting")) return showToast("Nothing to copy yet!", "info");
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = elements.copyBtn.innerText;
        elements.copyBtn.innerText = "COPIED!";
        setTimeout(() => elements.copyBtn.innerText = originalText, 2000);
    }).catch(err => {
        showToast("Copy failed: " + err.message, "error");
    });
}

async function generatePDF(elements) {
    const songTitle = localStorage.getItem("lyricai_title") || "Untitled Song";
    const originalHtml = elements.exportBtn.innerHTML;
    const currentRefined = elements.resultBody.innerText;

    if (!currentRefined || currentRefined.includes("Awaiting")) {
        return showToast("Analyze manuscript before exporting.", "info");
    }

    elements.exportBtn.disabled = true;
    elements.exportBtn.innerHTML = `<span class="material-symbols-outlined text-xl animate-spin">sync</span> <span>Wait...</span>`;

    // Fill PDF template
    const pdfSongTitle = document.getElementById('pdf-song-title');
    const pdfDate = document.getElementById('pdf-date');
    const pdfOriginal = document.getElementById('pdf-original-lyrics');
    const pdfRefined = document.getElementById('pdf-refined');
    const pdfTranslation = document.getElementById('pdf-translation');
    const pdfMood = document.getElementById('pdf-mood');
    const pdfStructure = document.getElementById('pdf-structure');
    const pdfMetaphors = document.getElementById('pdf-metaphors');
    
    if (pdfSongTitle) pdfSongTitle.textContent = songTitle;
    if (pdfDate) pdfDate.textContent = new Date().toLocaleDateString();
    if (pdfOriginal) pdfOriginal.textContent = localStorage.getItem("lyricai_original");
    if (pdfRefined) pdfRefined.textContent = currentRefined;
    if (pdfTranslation) pdfTranslation.textContent = localStorage.getItem("lyricai_translation");
    if (pdfMood) pdfMood.textContent = localStorage.getItem("lyricai_mood") || "---";
    if (pdfStructure) pdfStructure.textContent = localStorage.getItem("lyricai_structure") || "---";
    if (pdfMetaphors) pdfMetaphors.textContent = localStorage.getItem("lyricai_metaphors") || "---";
    
    const keyEl = document.getElementById('pdf-key');
    const bpmEl = document.getElementById('pdf-bpm');
    const verseEl = document.getElementById('pdf-chords-verse');
    const chorusEl = document.getElementById('pdf-chords-chorus');

    if (keyEl) keyEl.textContent = localStorage.getItem("lyricai_key") || "---";
    if (bpmEl) bpmEl.textContent = (localStorage.getItem("lyricai_bpm") || "0") + " BPM";
    if (verseEl) verseEl.textContent = localStorage.getItem("lyricai_chords_verse") || "---";
    if (chorusEl) chorusEl.textContent = localStorage.getItem("lyricai_chords_chorus") || "---";
    
    const opt = {
        margin: 10,
        filename: `${songTitle.replace(/\s+/g, '_')}_Masterpiece.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try {
        const template = document.getElementById('pdf-template');
        if (template) {
            await html2pdf().from(template.innerHTML).set(opt).save();
        } else {
            throw new Error("PDF template not found in page.");
        }
    } catch (err) {
        showToast('PDF export failed: ' + err.message, "error");
    } finally {
        elements.exportBtn.innerHTML = originalHtml;
        elements.exportBtn.disabled = false;
    }
}
