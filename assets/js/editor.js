// assets/js/editor.js
import { apiFetch } from './api.js';
import { showToast } from './ui-utils.js';

let currentSongId = localStorage.getItem('lyricai_current_song_id');
let allSongs = [];

export async function initEditor(elements) {
    // Session check and profile
    const user = await fetchProfileData(elements);
    if (user) {
        document.getElementById('user-name').textContent = `${user.first_name} ${user.last_name}`;
    }

    // Event Listeners
    elements.songTitle.oninput = (e) => {
        localStorage.setItem("lyricai_title", e.target.value);
    };

    elements.saveBtn.onclick = () => saveSong(elements);
    
    document.getElementById('logout-btn').onclick = () => { 
        localStorage.removeItem('lyricai_token'); 
        window.location.reload(); 
    };

    elements.analyzeBtn.onclick = () => analyzeLyrics(elements);
    
    elements.copyLyricsBtn.onclick = () => copyLyrics(elements);
    
    elements.reportBtn.onclick = () => generatePDF(elements);

    document.getElementById('new-song-sidebar-btn').onclick = () => { 
        resetEditor(elements); 
        toggleLibrary(elements, false); 
    };

    document.getElementById('toggle-library-btn').onclick = () => toggleLibrary(elements, true);
    document.getElementById('close-library-btn').onclick = () => toggleLibrary(elements, false);
    document.getElementById('library-overlay').onclick = () => toggleLibrary(elements, false);

    document.getElementById('library-search-input').oninput = (e) => {
        const query = e.target.value.toLowerCase();
        renderSongList(elements, allSongs.filter(s => s.title.toLowerCase().includes(query)));
    };

    // Load initial state
    if (currentSongId && currentSongId !== 'null' && currentSongId !== 'undefined') {
        console.log("[Editor] Found existing song ID:", currentSongId);
    }
    
    // Enable Agent link if we already have a translation
    if (localStorage.getItem("lyricai_translation")) {
        elements.navAgent.classList.remove("opacity-50", "pointer-events-none");
    }
}

async function fetchProfileData(elements) {
    const response = await apiFetch('/me');
    if (response && response.ok) {
        const user = await response.json();
        document.getElementById('profile-first-name').value = user.first_name;
        document.getElementById('profile-last-name').value = user.last_name;
        document.getElementById('modal-user-email').textContent = user.email;
        document.getElementById('stat-total-songs').textContent = user.stats.total_songs;
        document.getElementById('modal-user-avatar').src = user.avatar_url || `https://ui-avatars.com/api/?name=${user.first_name}+${user.last_name}&background=B5EAD7`;
        
        const statusEl = document.getElementById('user-status-display');
        if (statusEl) {
            statusEl.textContent = user.contribution_level === 'Free' ? 'Standard Author' : `${user.contribution_level} Author`;
            statusEl.className = `text-xs font-black uppercase ${user.contribution_level === 'Free' ? 'text-slate-400' : 'text-primary'}`;
        }
        return user;
    }
    return null;
}

export async function saveSong(elements, auto = false) {
    const originalHtml = elements.saveBtn.innerHTML;
    if (!auto) {
        elements.saveBtn.disabled = true;
        elements.saveBtn.innerHTML = `<span class="material-symbols-outlined animate-spin">sync</span> Saving...`;
    }

    // Ensure id is truly null if it's 'null' string
    const songId = (currentSongId === 'null' || currentSongId === 'undefined') ? null : currentSongId;

    const data = {
        id: songId,
        title: elements.songTitle.value.trim() || 'Untitled',
        lyrics: elements.lyricsInput.value,
        structure: elements.analysis.innerText,
        metaphors: elements.metaphors.innerText,
        mood: elements.mood.innerText,
        translation: elements.poet.innerText,
        refined_lyrics: localStorage.getItem('lyricai_refined') || "",
        target_language: elements.targetLang.value,
        musical_key: localStorage.getItem("lyricai_key"),
        bpm: localStorage.getItem("lyricai_bpm"),
        chords_verse: localStorage.getItem("lyricai_chords_verse"),
        chords_chorus: localStorage.getItem("lyricai_chords_chorus")
    };
    
    console.log("[Editor] Attempting to save song...", { id: songId, title: data.title });
    
    try {
        const response = await apiFetch('/songs', { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify(data) 
        });
        
        if (response && response.ok) {
            const saved = await response.json();
            currentSongId = saved.id;
            localStorage.setItem('lyricai_current_song_id', saved.id);
            console.log("[Editor] Song saved successfully, ID:", saved.id);
            
            if (!auto) {
                elements.saveBtn.innerHTML = `<span class="material-symbols-outlined text-green-500">check_circle</span> Saved`;
                setTimeout(() => { 
                    elements.saveBtn.disabled = false; 
                    elements.saveBtn.innerHTML = originalHtml; 
                }, 2000);
            }
        } else {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || "Save failed");
        }
    } catch (err) {
        console.error("[Editor] Save Error:", err);
        if (!auto) {
            elements.saveBtn.disabled = false;
            elements.saveBtn.innerHTML = originalHtml;
            showToast(err.message, "error");
        }
    }
}

function formatAIOutput(val, isHtml = true) {
    if (!val) return "";
    
    let result = "";
    if (typeof val === 'string') {
        result = val;
    } else if (Array.isArray(val)) {
        result = val.map(item => (typeof item === 'object' ? JSON.stringify(item) : item)).join("\n");
    } else if (typeof val === 'object') {
        const commonKeys = ['text', 'content', 'output', 'lyrics', 'translation', 'result'];
        let found = false;
        for (let key of commonKeys) {
            if (val[key] && typeof val[key] === 'string') {
                result = val[key];
                found = true;
                break;
            }
        }
        if (!found) {
            result = Object.entries(val).map(([k, v]) => {
                const displayV = typeof v === 'object' ? JSON.stringify(v) : v;
                return isHtml ? `<b>${k}:</b> ${displayV}` : `${k}: ${displayV}`;
            }).join("\n");
        }
    } else {
        result = String(val);
    }

    return isHtml ? result.replace(/\n/g, "<br>") : result;
}

async function analyzeLyrics(elements) {
    const text = elements.lyricsInput.value.trim();
    if (!text) return showToast("Enter lyrics!", "error");
    elements.analyzeBtn.disabled = true;
    elements.status.innerHTML = `<span class="flex h-2 w-2 rounded-full bg-blue-500 animate-pulse"></span> <span class="text-[10px] font-bold text-blue-500 uppercase">Processing</span>`;
    
    try {
        const response = await apiFetch('/webhook/analyze-lyrics', { 
            method: "POST", 
            headers: { "Content-Type": "application/json" }, 
            body: JSON.stringify({ chatInput: text, targetLanguage: elements.targetLang.value }) 
        });
        
        if (!response.ok) { throw new Error(`Analysis service error: ${response.status}`); }
        
        const data = await response.json();
        
        // Display formatted HTML
        elements.analysis.innerHTML = formatAIOutput(data.structure_output, true);
        elements.mood.innerHTML = formatAIOutput(data.mood_output, true);
        elements.metaphors.innerHTML = formatAIOutput(data.metaphors_output, true);
        elements.poet.innerHTML = formatAIOutput(data.poet_output, true);
        
        const music = data.musical_data || {};
        localStorage.setItem("lyricai_original", text);
        // Save clean strings to localStorage
        localStorage.setItem("lyricai_translation", formatAIOutput(data.poet_output, false));
        localStorage.setItem("lyricai_targetLang", elements.targetLang.value);
        localStorage.setItem("lyricai_structure", formatAIOutput(data.structure_output, false));
        localStorage.setItem("lyricai_mood", formatAIOutput(data.mood_output, false));
        localStorage.setItem("lyricai_metaphors", formatAIOutput(data.metaphors_output, false));
        localStorage.setItem("lyricai_key", music.key || "");
        localStorage.setItem("lyricai_bpm", music.bpm || "");
        localStorage.setItem("lyricai_chords_verse", music.chords_verse || "");
        localStorage.setItem("lyricai_chords_chorus", music.chords_chorus || "");

        elements.navAgent.classList.remove("opacity-50", "pointer-events-none");
        saveSong(elements, true);
    } catch (err) { showToast(err.message, "error"); } 
    finally { 
        elements.analyzeBtn.disabled = false; 
        elements.status.innerHTML = `<span class="flex h-2 w-2 rounded-full bg-green-500"></span> <span class="text-[10px] font-bold text-green-500 uppercase">Complete</span>`; 
    }
}

function copyLyrics(elements) {
    const text = elements.poet.innerText;
    if (!text || text.includes("Awaiting")) return;
    navigator.clipboard.writeText(text);
    // Sync for agent
    localStorage.setItem("lyricai_title", elements.songTitle.value || "Untitled");
    localStorage.setItem("lyricai_original", elements.lyricsInput.value);
    localStorage.setItem("lyricai_translation", text);
    elements.navAgent.classList.remove("opacity-50", "pointer-events-none");
    
    const originalHtml = elements.copyLyricsBtn.innerHTML;
    elements.copyLyricsBtn.innerHTML = `<span class="material-symbols-outlined text-green-500 text-sm">check</span> COPIED!`;
    setTimeout(() => elements.copyLyricsBtn.innerHTML = originalHtml, 2000);
}

function toggleLibrary(elements, show) {
    elements.librarySidebar.classList.toggle('-translate-x-full', !show);
    elements.libraryOverlay.classList.toggle('hidden', !show);
    if (show) fetchSongs(elements);
}

async function fetchSongs(elements) {
    const response = await apiFetch('/songs');
    if (response && response.ok) {
        allSongs = await response.json();
        renderSongList(elements, allSongs);
    }
}

function renderSongList(elements, songs) {
    const container = document.getElementById('song-list-container');
    container.innerHTML = songs.map(s => `
        <div class="group p-4 rounded-2xl hover:bg-white dark:hover:bg-slate-800 transition-all cursor-pointer border border-transparent hover:border-slate-100 dark:hover:border-slate-700">
            <div class="flex justify-between items-start mb-1" onclick="window.loadSong('${s.id}')">
                <h4 class="font-bold text-slate-800 dark:text-slate-200 truncate pr-4">${s.title}</h4>
                <span class="text-[9px] font-black text-slate-400 uppercase">${new Date(s.updated_at).toLocaleDateString()}</span>
            </div>
            <div class="flex justify-between items-center">
                <p class="text-[10px] text-slate-400 truncate flex-1" onclick="window.loadSong('${s.id}')">${s.lyrics.substring(0, 60)}...</p>
                <button onclick="event.stopPropagation(); window.deleteSong('${s.id}')" class="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 transition-all">
                    <span class="material-symbols-outlined text-sm">delete</span>
                </button>
            </div>
        </div>
    `).join('');

    // Attach global handlers for the generated HTML
    window.loadSong = (id) => loadSong(elements, id);
    window.deleteSong = (id) => deleteSong(elements, id);
}

async function loadSong(elements, id) {
    const response = await apiFetch(`/songs/${id}`);
    if (response && response.ok) {
        const song = await response.json();
        currentSongId = song.id;
        localStorage.setItem('lyricai_current_song_id', song.id);
        elements.songTitle.value = song.title;
        elements.lyricsInput.value = song.lyrics;
        elements.analysis.innerHTML = (song.structure || "Awaiting scan...").replace(/\n/g, "<br>");
        elements.mood.innerHTML = (song.mood || "Waiting...").replace(/\n/g, "<br>");
        elements.metaphors.innerHTML = (song.metaphors || "Awaiting...").replace(/\n/g, "<br>");
        elements.poet.innerHTML = (song.translation || "Awaiting...").replace(/\n/g, "<br>");
        elements.targetLang.value = song.target_language || "English";

        // LocalStorage sync
        localStorage.setItem("lyricai_title", song.title);
        localStorage.setItem("lyricai_original", song.lyrics);
        localStorage.setItem("lyricai_translation", song.translation || "");
        localStorage.setItem("lyricai_structure", song.structure || "");
        localStorage.setItem("lyricai_mood", song.mood || "");
        localStorage.setItem("lyricai_metaphors", song.metaphors || "");
        localStorage.setItem("lyricai_key", song.musical_key || "");
        localStorage.setItem("lyricai_bpm", song.bpm || "");
        localStorage.setItem("lyricai_chords_verse", song.chords_verse || "");
        localStorage.setItem("lyricai_chords_chorus", song.chords_chorus || "");

        toggleLibrary(elements, false);
        if (song.lyrics) elements.navAgent.classList.remove("opacity-50", "pointer-events-none");
    }
}

async function deleteSong(elements, id) {
    if (!confirm('Delete this song?')) return;
    const response = await apiFetch(`/songs/${id}`, { method: 'DELETE' });
    if (response && response.ok) { 
        if (currentSongId === id) resetEditor(elements); 
        fetchSongs(elements); 
    }
}

function resetEditor(elements) {
    currentSongId = null;
    localStorage.removeItem('lyricai_current_song_id');
    localStorage.removeItem('lyricai_refined');
    elements.songTitle.value = '';
    elements.lyricsInput.value = '';
    elements.analysis.innerHTML = 'Awaiting scan...';
    elements.mood.innerHTML = 'Waiting...';
    elements.metaphors.innerHTML = 'Awaiting AI creative...';
    elements.poet.innerHTML = 'Awaiting AI creative generation...';
    elements.navAgent.classList.add("opacity-50", "pointer-events-none");
}

async function generatePDF(elements) {
    const songTitle = elements.songTitle.value.trim() || "Untitled Song";
    const originalHtml = elements.reportBtn.innerHTML;
    elements.reportBtn.disabled = true;
    elements.reportBtn.innerHTML = `<span class="material-symbols-outlined text-xl animate-spin">sync</span> <span>Wait...</span>`;

    document.getElementById('pdf-song-title').textContent = songTitle;
    document.getElementById('pdf-date').textContent = new Date().toLocaleDateString();
    document.getElementById('pdf-original-lyrics').textContent = elements.lyricsInput.value;
    document.getElementById('pdf-translation').textContent = elements.poet.innerText;
    document.getElementById('pdf-mood').textContent = elements.mood.innerText;
    document.getElementById('pdf-structure').textContent = elements.analysis.innerText;
    document.getElementById('pdf-metaphors').textContent = elements.metaphors.innerText;
    
    document.getElementById('pdf-key').textContent = localStorage.getItem("lyricai_key") || "---";
    document.getElementById('pdf-bpm').textContent = (localStorage.getItem("lyricai_bpm") || "0") + " BPM";
    document.getElementById('pdf-chords-verse').textContent = localStorage.getItem("lyricai_chords_verse") || "---";
    document.getElementById('pdf-chords-chorus').textContent = localStorage.getItem("lyricai_chords_chorus") || "---";
    
    const opt = {
        margin: 10,
        filename: `${songTitle.replace(/\s+/g, '_')}_Report.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try { 
        await html2pdf().from(document.getElementById('pdf-template').innerHTML).set(opt).save(); 
    } catch (err) { 
        showToast('PDF export failed.', "error"); 
    }
    
    elements.reportBtn.innerHTML = originalHtml;
    elements.reportBtn.disabled = false;
}
