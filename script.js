document.addEventListener('DOMContentLoaded', () => {

    // --- 1. DOM & CONFIGURATION ---
    const GAME_VERSION = "1.5.1"; // Final UI Streamlining
    const BUILD_DATE = "2025-07-25";
    // UPDATED: Removed skipBtn and clearCacheBtn
    const gameWrapper = document.getElementById('game-wrapper'),
        gameTitleEl = document.getElementById('game-title'),
        optionsToggle = document.getElementById('options-toggle'),
        optionsDrawer = document.getElementById('options-drawer'),
        gridContainer = document.getElementById('puzzle-grid'),
        wordListUl = document.getElementById('words-to-find'),
        scoreEl = document.getElementById('score'),
        levelEl = document.getElementById('level'),
        timerEl = document.getElementById('timer'),
        newGameBtn = document.getElementById('new-game-btn'),
        newGameBtnText = document.getElementById('new-game-btn-text'),
        soundBtn = document.getElementById('sound-btn'),
        soundIconEl = document.getElementById('sound-icon'),
        langEnBtn = document.getElementById('lang-en'),
        langRoBtn = document.getElementById('lang-ro'),
        bibleModeCheckbox = document.getElementById('bible-mode-checkbox'),
        gridSizeSlider = document.getElementById('grid-size-slider'),
        gridSizeValue = document.getElementById('grid-size-value'),
        completionMessageEl = document.getElementById('completion-message'),
        completionDetailsEl = document.getElementById('completion-details'),
        verseDisplayEl = document.getElementById('verse-display'),
        definitionDisplayEl = document.getElementById('definition-display'),
        definitionWordEl = document.getElementById('definition-word'),
        definitionTextEl = document.getElementById('definition-text'),
        historyBtn = document.getElementById('history-btn'),
        historyModal = document.getElementById('history-modal'),
        closeHistoryBtn = document.getElementById('close-history-btn'),
        historyLogEl = document.getElementById('history-log'),
        versionInfoEl = document.getElementById('version-info');

    // --- 2. GAME STATE & OTHER VARIABLES ---
    let gameState = {}, puzzleTimer, bibleData = {}, standardDictionaries = {};
    let hasGridSizeChanged = false;
    const colorPalette = ['--found-color-1', '--found-color-2', '--found-color-3', '--found-color-4', '--found-color-5', '--found-color-6', '--found-color-7', '--found-color-8', '--found-color-9', '--found-color-10'];
    let wordColorMap = {};
    const alphabet = { english: "ABCDEFGHIJKLMNOPQRSTUVWXYZ", romanian: "AĂÂBCDEFGHIÎJKLMNOPRSȘTȚUVWXYZ" };

    // --- SOUND ENGINE (Unchanged) ---
    const sound = { isMuted: true, audioContext: null, buffers: {}, isUnlocked: false, init: function() { this.isMuted = localStorage.getItem('soundMuted') === 'true'; soundIconEl.src = this.isMuted ? 'mute.png' : 'volume.png'; soundBtn.classList.toggle('muted', this.isMuted); }, unlock: function() { if (this.isUnlocked) return; try { this.audioContext = new (window.AudioContext || window.webkitAudioContext)(); this._loadSounds(); this.isUnlocked = true; console.log("Audio Context unlocked."); const unlockOverlay = document.getElementById('sound-unlock-overlay'); if (unlockOverlay) unlockOverlay.style.display = 'none'; gameWrapper.style.display = 'block'; } catch (e) { console.error("Web Audio API not supported.", e); gameWrapper.style.display = 'block'; } }, _loadSound: async function(name, url) { if (!this.audioContext) return; try { const response = await fetch(url); const arrayBuffer = await response.arrayBuffer(); this.buffers[name] = await this.audioContext.decodeAudioData(arrayBuffer); } catch (error) { console.error(`Failed to load sound: ${name}`, error); } }, _loadSounds: function() { this._loadSound('correct', 'correct.mp3'); this._loadSound('error', 'error.mp3'); this._loadSound('complete', 'complete.mp3'); this._loadSound('hint', 'hint.mp3'); }, play: function(name) { if (this.isMuted || !this.buffers[name] || !this.audioContext) return; if (this.audioContext.state === 'suspended') { this.audioContext.resume(); } const source = this.audioContext.createBufferSource(); source.buffer = this.buffers[name]; source.connect(this.audioContext.destination); source.start(0); }, toggleMute: function() { if (!this.isUnlocked) { this.unlock(); } this.isMuted = !this.isMuted; localStorage.setItem('soundMuted', this.isMuted); soundIconEl.src = this.isMuted ? 'mute.png' : 'volume.png'; soundBtn.classList.toggle('muted', this.isMuted); } };

    // --- 3. CORE INITIALIZATION (Unchanged) ---
    async function initializeGame() { versionInfoEl.textContent = `v${GAME_VERSION} (${BUILD_DATE})`; sound.init(); const unlockOverlay = document.getElementById('sound-unlock-overlay'); unlockOverlay.addEventListener('click', () => { sound.unlock(); initializeData(); }, { once: true }); }
    async function initializeData() {
        try {
            const [bibleRes, dictEngRes, dictRomRes] = await Promise.all([ fetch('bible_data.json'), fetch('english_dictionary.json'), fetch('romanian_dictionary.json'), ]);
            if (!bibleRes.ok) throw new Error(`Bible data fetch failed`); if (!dictEngRes.ok) throw new Error(`English dictionary fetch failed`); if (!dictRomRes.ok) throw new Error(`Romanian dictionary fetch failed`);
            bibleData = await bibleRes.json(); standardDictionaries.english = await dictEngRes.json(); standardDictionaries.romanian = await dictRomRes.json();
            console.log("All 3 required game data files successfully loaded.");
            initGameSession();
        } catch (error) { console.error("CRITICAL ERROR: Could not load game data files.", error); const unlockOverlay = document.getElementById('sound-unlock-overlay'); unlockOverlay.innerHTML = `<div id="sound-unlock-content"><h1>Error</h1><p>Could not load game data. Please ensure JSON files are correct and refresh the page.</p></div>`; }
    }

    // --- 4. GAME SESSION & STATE LOGIC (Unchanged) ---
    function initGameSession() { const savedGridSize = localStorage.getItem('wordSearchGridSize') || 13; gridSizeSlider.value = savedGridSize; gridSizeValue.textContent = `${savedGridSize} x ${savedGridSize}`; const savedState = loadState(); if (savedState) { console.log("Found saved state. Resuming game."); gameState = savedState; bibleModeCheckbox.checked = gameState.bibleMode; langEnBtn.classList.toggle('active', gameState.currentLanguage === 'english'); langRoBtn.classList.toggle('active', gameState.currentLanguage === 'romanian'); renderGame(); if (gameState.foundWords.length === gameState.words.length) { completionMessageEl.classList.remove('hidden'); newGameBtnText.textContent = "Next Level"; } else { startTimer(); } } else { console.log("No saved state found. Starting new game with defaults."); createNewGame('romanian', true, 0); } }
    function saveState() { if (gameState) { localStorage.setItem('wordSearchGameState', JSON.stringify(gameState)); } }
    function loadState() { const savedStateJSON = localStorage.getItem('wordSearchGameState'); if (savedStateJSON) { try { return JSON.parse(savedStateJSON); } catch (e) { console.error("Failed to parse saved state, starting fresh.", e); localStorage.removeItem('wordSearchGameState'); return null; } } return null; }
    function saveHistory(levelData) { if (!levelData) return; let history = JSON.parse(localStorage.getItem('wordSearchHistory')) || []; history.push(levelData); localStorage.setItem('wordSearchHistory', JSON.stringify(history)); }
    function displayHistory() { let history = JSON.parse(localStorage.getItem('wordSearchHistory')) || []; historyLogEl.innerHTML = ''; if (history.length === 0) { historyLogEl.innerHTML = '<p>No games completed yet!</p>'; return; } history.slice().reverse().forEach(entry => { const entryDiv = document.createElement('div'); entryDiv.className = 'history-entry'; const date = new Date(entry.timestamp).toLocaleString(); const status = entry.completed ? '' : `<span class="entry-skipped">(Incomplete)</span>`; entryDiv.innerHTML = `<div class="entry-header"><strong>Level ${entry.level} ${status}</strong><span class="entry-date">${date}</span></div><p class="entry-details"><strong>Mode:</strong> ${entry.mode}</p><p class="entry-details"><strong>Time:</strong> ${entry.time}s | <strong>Hints Used:</strong> ${entry.hintsUsed} | <strong>Words Found:</strong> ${entry.wordsFound}/${entry.totalWords} | <strong>Points Earned:</strong> ${entry.pointsEarned}</p>`; historyLogEl.appendChild(entryDiv); }); historyModal.classList.remove('hidden'); }

    // --- 5. PUZZLE GENERATION & TIMER (Unchanged) ---
    function startTimer() { stopTimer(); let seconds = gameState.currentLevelData.time || 0; timerEl.textContent = `${seconds}s`; puzzleTimer = setInterval(() => { seconds++; timerEl.textContent = `${seconds}s`; if (gameState.currentLevelData) gameState.currentLevelData.time = seconds; }, 1000); }
    function stopTimer() { clearInterval(puzzleTimer); }
    function generatePuzzle() { const wordsToPlace = [...gameState.words].sort((a, b) => b.length - a.length); const directions = { horizontal: [{ x: 1, y: 0 }, { x: -1, y: 0 }], vertical: [{ x: 0, y: 1 }, { x: 0, y: -1 }], diagonal: [{ x: 1, y: 1 }, { x: -1, y: -1 }, { x: 1, y: -1 }, { x: -1, y: 1 }] }; const requiredPlacements = { horizontal: 2, vertical: 2, diagonal: 2 }; const remainingWords = 10 - Object.values(requiredPlacements).reduce((a, b) => a + b); for (let attempt = 0; attempt < 50; attempt++) { let grid = Array.from({ length: gameState.gridSize }, () => Array(gameState.gridSize).fill(null)); gameState.wordLocations = {}; let availableWords = [...wordsToPlace]; let success = true; for (const type in requiredPlacements) { for (let i = 0; i < requiredPlacements[type]; i++) { if (availableWords.length === 0) break; let word = availableWords.shift(); if (!placeWordInGrid(grid, word, directions[type])) { success = false; break; } } if (!success) break; } if (!success) continue; const allDirections = [...directions.horizontal, ...directions.vertical, ...directions.diagonal]; for (let i = 0; i < remainingWords; i++) { if (availableWords.length === 0) break; let word = availableWords.shift(); if (!placeWordInGrid(grid, word, allDirections)) { success = false; break; } } if (!success) continue; fillEmptyCells(grid); return grid; } console.error("Failed to generate puzzle after all attempts."); return null; }
    function placeWordInGrid(grid, word, directionSet) { const shuffledDirections = directionSet.sort(() => 0.5 - Math.random()); for (let i = 0; i < 100; i++) { const dir = shuffledDirections[i % shuffledDirections.length]; const row = Math.floor(Math.random() * gameState.gridSize); const col = Math.floor(Math.random() * gameState.gridSize); if (canPlaceWord(grid, word, row, col, dir)) { for (let j = 0; j < word.length; j++) { grid[row + j * dir.y][col + j * dir.x] = word[j]; } gameState.wordLocations[word] = { r: row, c: col }; return true; } } return false; }
    function canPlaceWord(grid, word, row, col, dir) { for (let i = 0; i < word.length; i++) { let r = row + i * dir.y, c = col + i * dir.x; if (r < 0 || r >= gameState.gridSize || c < 0 || c >= gameState.gridSize) return false; if (grid[r][c] !== null && grid[r][c] !== word[i]) return false; } return true; }
    function fillEmptyCells(grid) { const letters = alphabet[gameState.currentLanguage]; for (let r = 0; r < gameState.gridSize; r++) { for (let c = 0; c < gameState.gridSize; c++) { if (grid[r][c] === null) grid[r][c] = letters[Math.floor(Math.random() * letters.length)]; } } }
    function getWordsForPuzzle(count) { const dictionary = standardDictionaries[gameState.currentLanguage]; if (!dictionary) return []; const allWords = Object.keys(dictionary); const validWords = allWords.filter(word => word.length <= gameState.gridSize); let shuffled = validWords.sort(() => 0.5 - Math.random()); return shuffled.slice(0, count); }
    
    // --- 6. RENDERING (Unchanged) ---
    function renderGame() { renderGrid(); renderWordList(); updateStats(); langEnBtn.classList.toggle('active', gameState.currentLanguage === 'english'); langRoBtn.classList.toggle('active', gameState.currentLanguage === 'romanian'); }
    function renderGrid() { gridContainer.style.setProperty('--grid-size', gameState.gridSize); gridContainer.innerHTML = ''; gridContainer.classList.add('loaded'); gridContainer.style.gridTemplateColumns = `repeat(${gameState.gridSize}, 1fr)`; for (let r = 0; r < gameState.gridSize; r++) { for (let c = 0; c < gameState.gridSize; c++) { const cell = document.createElement('div'); cell.classList.add('grid-cell'); cell.textContent = gameState.grid[r][c]; cell.dataset.row = r; cell.dataset.col = c; gridContainer.appendChild(cell); } } addSelectionListeners(); }
    function renderWordList() { wordListUl.innerHTML = ''; const sortedWords = [...gameState.words].sort(); wordColorMap = {}; let shuffledPalette = [...colorPalette].sort(() => 0.5 - Math.random()); sortedWords.forEach((word, index) => { wordColorMap[word] = shuffledPalette[index % shuffledPalette.length]; }); sortedWords.forEach(word => { const li = document.createElement('li'); li.textContent = word; li.id = `word-${word}`; if (gameState.foundWords.includes(word)) { li.classList.add('found'); li.style.backgroundColor = `var(${wordColorMap[word]})`; } li.addEventListener('click', handleHintRequest); wordListUl.appendChild(li); }); }
    function updateStats() { scoreEl.textContent = gameState.score; levelEl.textContent = gameState.level; }

    // --- 7. WORD SELECTION & PROCESSING (Unchanged) ---
    let isSelecting = false, selectionStartCell = null, selectedCells = [];
    function addSelectionListeners() { gridContainer.addEventListener('mousedown', handleSelectionStart); gridContainer.addEventListener('mousemove', handleSelectionMove); window.addEventListener('mouseup', handleSelectionEnd); gridContainer.addEventListener('touchstart', handleSelectionStart, { passive: false }); gridContainer.addEventListener('touchmove', handleSelectionMove, { passive: false }); window.addEventListener('touchend', handleSelectionEnd); }
    function getCellFromEvent(e) { if (e.touches && e.touches.length > 0) { const touch = e.touches[0]; return document.elementFromPoint(touch.clientX, touch.clientY); } return e.target; }
    function handleSelectionStart(e) { e.preventDefault(); const targetCell = getCellFromEvent(e); if (targetCell && targetCell.classList.contains('grid-cell')) { isSelecting = true; selectionStartCell = targetCell; highlightLine(selectionStartCell, selectionStartCell); } }
    function handleSelectionMove(e) { if (!isSelecting) return; e.preventDefault(); const targetCell = getCellFromEvent(e); if (targetCell && targetCell.classList.contains('grid-cell')) { highlightLine(selectionStartCell, targetCell); } }
    function handleSelectionEnd() { if (!isSelecting) return; isSelecting = false; const selectedWord = selectedCells.map(cell => cell.textContent).join(''); const reversedWord = selectedCells.map(cell => cell.textContent).reverse().join(''); if (gameState.words.includes(selectedWord) && !gameState.foundWords.includes(selectedWord)) { processFoundWord(selectedWord); } else if (gameState.words.includes(reversedWord) && !gameState.foundWords.includes(reversedWord)) { processFoundWord(reversedWord); } else { if (selectedCells.length > 1) sound.play('error'); selectedCells.forEach(cell => cell.classList.remove('selected')); } selectionStartCell = null; }
    function highlightLine(startCell, endCell) { document.querySelectorAll('.grid-cell.selected').forEach(c => c.classList.remove('selected')); selectedCells = []; const start = { r: parseInt(startCell.dataset.row), c: parseInt(startCell.dataset.col) }; const end = { r: parseInt(endCell.dataset.row), c: parseInt(endCell.dataset.col) }; const dR = end.r - start.r, dC = end.c - start.c; if (start.r === end.r || start.c === end.c || Math.abs(dR) === Math.abs(dC)) { const steps = Math.max(Math.abs(dR), Math.abs(dC)); const stepR = Math.sign(dR), stepC = Math.sign(dC); for (let i = 0; i <= steps; i++) { const cell = document.querySelector(`[data-row='${start.r + i * stepR}'][data-col='${start.c + i * stepC}']`); if (cell) { cell.classList.add('selected'); selectedCells.push(cell); } } } }
    function processFoundWord(word) { if (gameState.foundWords.includes(word)) return; sound.play('correct'); const points = word.length * 10; gameState.foundWords.push(word); gameState.score += points; gameState.currentLevelData.pointsEarned += points; gameState.currentLevelData.wordsFound = gameState.foundWords.length; verseDisplayEl.classList.add('hidden'); definitionDisplayEl.classList.add('hidden'); if (gameState.bibleMode && gameState.currentLevelData.verseMap[word]) { const verseInfo = gameState.currentLevelData.verseMap[word]; const verseText = bibleData[gameState.currentLanguage][verseInfo.book][verseInfo.chapter][verseInfo.verse]; verseDisplayEl.innerHTML = `${verseInfo.book} ${verseInfo.chapter}:${verseInfo.verse} - ${verseText.replace(new RegExp(word, 'i'), `<strong>$&</strong>`)}`; verseDisplayEl.classList.remove('hidden'); } else if (!gameState.bibleMode) { const definition = standardDictionaries[gameState.currentLanguage][word]; if (definition) { definitionWordEl.textContent = word; definitionTextEl.textContent = definition; definitionDisplayEl.classList.remove('hidden'); } } const wordColorVar = wordColorMap[word]; selectedCells.forEach(cell => { cell.classList.remove('selected'); cell.classList.add('found'); cell.style.backgroundColor = `var(${wordColorVar})`; }); const wordLi = document.getElementById(`word-${word}`); wordLi.classList.add('found'); wordLi.style.backgroundColor = `var(${wordColorVar})`; updateStats(); if (gameState.foundWords.length === gameState.words.length) { sound.play('complete'); stopTimer(); gameState.currentLevelData.completed = true; completionDetailsEl.textContent = `You earned ${gameState.currentLevelData.pointsEarned} points!`; completionMessageEl.classList.remove('hidden'); saveHistory(gameState.currentLevelData); newGameBtnText.textContent = "Next Level"; } saveState(); }
    
    // --- 8. HINT SYSTEM (Unchanged) ---
    function handleHintRequest(e) { const word = e.target.textContent; const hintCost = 75; if (gameState.foundWords.includes(word)) return; if (gameState.score < hintCost) { alert(`Not enough points! A hint costs ${hintCost} points.`); return; } sound.play('hint'); gameState.score -= hintCost; gameState.currentLevelData.pointsEarned -= hintCost; if (gameState.currentLevelData) gameState.currentLevelData.hintsUsed++; updateStats(); saveState(); const location = gameState.wordLocations[word]; if (location) { const hintCell = document.querySelector(`[data-row='${location.r}'][data-col='${location.c}']`); if (hintCell) { hintCell.classList.add('hint'); setTimeout(() => { hintCell.classList.remove('hint'); }, 1500); } } }

    // --- 9. GAME INITIALIZATION & CONTROLS (UPDATED) ---
    function createNewGame(language, isBibleMode, score = 0) {
        langEnBtn.classList.toggle('active', language === 'english');
        langRoBtn.classList.toggle('active', language === 'romanian');
        bibleModeCheckbox.checked = isBibleMode;
        gameState = { level: 1, score: score, currentLanguage: language, bibleMode: isBibleMode, words: [], wordLocations: {}, grid: [], foundWords: [], currentLevelData: null, bibleChapterPlaylist: [] };
        startLevel();
    }
    
    function startLevel() {
        gridContainer.classList.remove('loaded');
        gridContainer.innerHTML = '<div id="loader"></div>';
        completionMessageEl.classList.add('hidden'); verseDisplayEl.classList.add('hidden'); definitionDisplayEl.classList.add('hidden');
        newGameBtnText.textContent = "New Puzzle / Skip";
        gameState.gridSize = parseInt(gridSizeSlider.value);
        gridContainer.style.setProperty('--grid-size', gameState.gridSize);
        hasGridSizeChanged = false;
        gameState.currentLevelData = { level: gameState.level, mode: `${gameState.bibleMode ? 'Bible' : 'Standard'} (${gameState.currentLanguage})`, time: 0, hintsUsed: 0, pointsEarned: 0, wordsFound: 0, totalWords: 10, completed: false, verseMap: {}, timestamp: new Date().toISOString() };
        
        // UPDATED: Set title to Bible Word Search always
        gameTitleEl.textContent = "Bible Word Search";
        
        if (gameState.bibleMode) {
            const langBibleData = bibleData[gameState.currentLanguage];
            if (!langBibleData || Object.keys(langBibleData).length === 0) { alert(`Bible data not available for '${gameState.currentLanguage}'. Switching to Standard Mode.`); bibleModeCheckbox.checked = false; switchMode(); return; }
            if (gameState.level === 1 || !gameState.bibleChapterPlaylist || gameState.bibleChapterPlaylist.length === 0) { const allChapters = []; for (const book in langBibleData) { for (const chapterNum in langBibleData[book]) { allChapters.push({ book, chapterNum }); } } gameState.bibleChapterPlaylist = allChapters.sort(() => 0.5 - Math.random()); }
            if (gameState.bibleChapterPlaylist.length === 0) { alert(`No chapters found. Switching to Standard Mode.`); bibleModeCheckbox.checked = false; switchMode(); return; }
            const chapterInfo = gameState.bibleChapterPlaylist[(gameState.level - 1) % gameState.bibleChapterPlaylist.length];
            // ... (rest of Bible word selection is unchanged)
            const { book, chapterNum } = chapterInfo;
            let wordsWithVerses = [];
            const chapterData = langBibleData[book][chapterNum];
            for (const verseNum in chapterData) { const verseText = chapterData[verseNum]; const wordsInVerse = verseText.toUpperCase().match(/[A-ZĂÂÎȘȚ]+/g) || []; wordsInVerse.forEach(word => { if (word.length > 3 && word.length <= gameState.gridSize) { wordsWithVerses.push({ word, book, chapter: chapterNum, verse: verseNum }); } }); }
            const uniqueWords = [...new Map(wordsWithVerses.map(item => [item.word, item])).values()];
            const shuffledWords = uniqueWords.sort(() => 0.5 - Math.random());
            const selectedWords = shuffledWords.slice(0, 10);
            gameState.words = selectedWords.map(w => w.word);
            selectedWords.forEach(w => { gameState.currentLevelData.verseMap[w.word] = { book: w.book, chapter: w.chapter, verse: w.verse }; });
        } else {
            gameState.words = getWordsForPuzzle(10);
        }
        
        if (gameState.words.length < 10) { alert("Not enough unique words for this level. Trying another level."); gameState.level++; startLevel(); return; }
        
        setTimeout(() => {
            gameState.grid = generatePuzzle();
            if (gameState.grid) { renderGame(); startTimer(); saveState(); } else { alert("The puzzle generator failed. Let's try creating a new puzzle for this level."); startLevel(); }
        }, 50);
    }
    
    function switchLanguage(lang) { if (gameState.currentLevelData && gameState.currentLevelData.completed === false) { saveHistory(gameState.currentLevelData); } if (gameState.foundWords && gameState.foundWords.length === gameState.words.length) { gameState.level++; } const currentScore = gameState.score || 0; const isBible = bibleModeCheckbox.checked; createNewGame(lang, isBible, currentScore); }
    function switchMode() { if (gameState.currentLevelData && gameState.currentLevelData.completed === false) { saveHistory(gameState.currentLevelData); } const currentScore = gameState.score || 0; const currentLang = gameState.currentLanguage; const isBible = bibleModeCheckbox.checked; createNewGame(currentLang, isBible, currentScore); }
    
    // --- EVENT LISTENERS ---
    soundBtn.addEventListener('click', () => sound.toggleMute());
    historyBtn.addEventListener('click', displayHistory);
    closeHistoryBtn.addEventListener('click', () => historyModal.classList.add('hidden'));
    bibleModeCheckbox.addEventListener('change', switchMode);
    
    // UPDATED: Combined New/Skip/Regenerate logic
    newGameBtn.addEventListener('click', () => {
        const isComplete = gameState.foundWords.length === gameState.words.length;
        if (isComplete) {
            gameState.level++;
            gameState.foundWords = [];
            startLevel();
        } else if (hasGridSizeChanged) {
            if (confirm("Change grid size and start a new puzzle for this level? (Your progress on this level will be lost)")) {
                saveHistory(gameState.currentLevelData);
                gameState.foundWords = [];
                startLevel();
            }
        } else {
            const skipCost = 100;
            if (gameState.score < skipCost) { alert(`You need at least ${skipCost} points to skip a puzzle!`); return; }
            if (confirm(`Are you sure you want to skip this puzzle? It will cost ${skipCost} points.`)) {
                saveHistory(gameState.currentLevelData);
                gameState.score -= skipCost;
                gameState.level++;
                gameState.foundWords = [];
                startLevel();
            }
        }
    });

    // UPDATED: Removed clear cache button listener, added options toggle
    optionsToggle.addEventListener('click', () => {
        optionsDrawer.classList.toggle('expanded');
    });
    
    langEnBtn.addEventListener('click', () => { if (gameState.currentLanguage !== 'english') switchLanguage('english'); });
    langRoBtn.addEventListener('click', () => { if (gameState.currentLanguage !== 'romanian') switchLanguage('romanian'); });
    
    gridSizeSlider.addEventListener('input', (e) => {
        const size = e.target.value;
        gridSizeValue.textContent = `${size} x ${size}`;
        localStorage.setItem('wordSearchGridSize', size);
        hasGridSizeChanged = true;
    });

    // KICK OFF THE ENTIRE PROCESS
    initializeGame();
});