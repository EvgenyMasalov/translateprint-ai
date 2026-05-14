// assets/js/agent-ui.js
import { apiFetch } from './api.js';
import { showToast } from './ui-utils.js';

export function initAgent(elements) {
    // Event Listeners
    elements.analyzeBtn.onclick = () => analyzeManuscript(elements);
    elements.deepBtn.onclick = () => deepAnalyze(elements);
    elements.exportBtn.onclick = () => generatePDF(elements);
    
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
    elements.originalBody.innerText = original;
    
    if (refined) {
        elements.resultBody.innerHTML = refined.split('\n').map(l => `<p>${l}</p>`).join('');
        const statusCheck = document.getElementById('status-check');
        statusCheck.classList.remove('hidden');
        statusCheck.style.display = 'flex';
        statusCheck.innerHTML = `<span class="material-symbols-outlined text-green-600 text-xs">verified</span> <span id="status-text" class="text-[10px] font-bold text-green-600 uppercase">Polished by Claude</span>`;
    }
 else if (translation) {
        elements.resultBody.innerHTML = translation.split('\n').map(l => `<p>${l}</p>`).join('');
    }

    updateHarmonyDisplay();
}

function updateHarmonyDisplay() {
    document.getElementById('harmony-key').innerText = localStorage.getItem("lyricai_key") || "Awaiting harmony...";
    document.getElementById('harmony-bpm').innerText = (localStorage.getItem("lyricai_bpm") || "0") + " BPM";
    document.getElementById('chords-verse').innerText = localStorage.getItem("lyricai_chords_verse") || "---";
    document.getElementById('chords-chorus').innerText = localStorage.getItem("lyricai_chords_chorus") || "---";
}

async function analyzeManuscript(elements) {
    const original = localStorage.getItem("lyricai_original");
    if (!original) return showToast("No lyrics found to analyze!", "error");

    elements.analyzeBtn.disabled = true;
    elements.analyzeBtn.innerHTML = `<span class="material-symbols-outlined animate-spin text-sm">sync</span> ANALYZING...`;

    try {
        const response = await apiFetch('/webhook/analyze-harmony', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lyrics: original })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("lyricai_key", data.key);
            localStorage.setItem("lyricai_bpm", data.bpm);
            localStorage.setItem("lyricai_chords_verse", data.chords_verse);
            localStorage.setItem("lyricai_chords_chorus", data.chords_chorus);
            updateHarmonyDisplay();
            
            const statusCheck = document.getElementById('status-check');
            statusCheck.classList.remove('hidden');
            statusCheck.style.display = 'flex';
        } else {
            throw new Error("Harmony analysis failed");
        }
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.innerHTML = `<span class="material-symbols-outlined text-sm">psychology</span> ANALYZE HARMONY`;
    }
}

async function deepAnalyze(elements) {
    const translation = localStorage.getItem("lyricai_translation");
    if (!translation) return showToast("Analyze lyrics in the editor first!", "error");

    elements.deepBtn.disabled = true;
    elements.deepBtn.innerHTML = `<span class="material-symbols-outlined animate-spin text-sm">sync</span> POLISHING...`;

    try {
        const response = await apiFetch('/webhook/literary-editor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                poetDraft: translation,
                structure: localStorage.getItem("lyricai_structure") || "",
                mood: localStorage.getItem("lyricai_mood") || "",
                targetLanguage: localStorage.getItem("lyricai_targetLang") || "English"
            })
        });

        if (response.ok) {
            const data = await response.json();
            elements.resultBody.innerHTML = data.editor_output.split('\n').map(l => `<p>${l}</p>`).join('');
            localStorage.setItem("lyricai_refined", data.editor_output);
            
            const statusCheck = document.getElementById('status-check');
            statusCheck.classList.remove('hidden');
            statusCheck.style.display = 'flex';
            statusCheck.innerHTML = `<span class="material-symbols-outlined text-green-600 text-xs">verified</span> <span class="text-[10px] font-bold text-green-600 uppercase">Polished by Claude</span>`;
        } else {
            throw new Error("Deep analysis failed");
        }
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        elements.deepBtn.disabled = false;
        elements.deepBtn.innerHTML = `<span class="material-symbols-outlined text-sm">auto_fix_high</span> DEEP POLISH`;
    }
}

async function generatePDF(elements) {
    const songTitle = localStorage.getItem("lyricai_title") || "Untitled Song";
    const originalHtml = elements.exportBtn.innerHTML;
    elements.exportBtn.disabled = true;
    elements.exportBtn.innerHTML = `<span class="material-symbols-outlined text-xl animate-spin">sync</span> <span>Wait...</span>`;

    // Fill PDF template (needs to be in DOM)
    document.getElementById('pdf-song-title').textContent = songTitle;
    document.getElementById('pdf-date').textContent = new Date().toLocaleDateString();
    document.getElementById('pdf-original-lyrics').textContent = localStorage.getItem("lyricai_original");
    document.getElementById('pdf-translation').textContent = elements.resultBody.innerText;
    document.getElementById('pdf-mood').textContent = localStorage.getItem("lyricai_mood") || "---";
    document.getElementById('pdf-structure').textContent = localStorage.getItem("lyricai_structure") || "---";
    document.getElementById('pdf-metaphors').textContent = localStorage.getItem("lyricai_metaphors") || "---";
    
    document.getElementById('pdf-key').textContent = localStorage.getItem("lyricai_key") || "---";
    document.getElementById('pdf-bpm').textContent = (localStorage.getItem("lyricai_bpm") || "0") + " BPM";
    document.getElementById('pdf-chords-verse').textContent = localStorage.getItem("lyricai_chords_verse") || "---";
    document.getElementById('pdf-chords-chorus').textContent = localStorage.getItem("lyricai_chords_chorus") || "---";
    
    const opt = {
        margin: 10,
        filename: `${songTitle.replace(/\s+/g, '_')}_Masterpiece.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try {
        await html2pdf().from(document.getElementById('pdf-template').innerHTML).set(opt).save();
    } catch (err) {
        showToast('PDF export failed.', "error");
    } finally {
        elements.exportBtn.innerHTML = originalHtml;
        elements.exportBtn.disabled = false;
    }
}
