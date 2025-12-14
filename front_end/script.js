// API Configuration
// Use relative URL since frontend is now served by FastAPI
const API_BASE_URL = '';
const STORAGE_KEY = 'lughati_openai_key';

// DOM Elements (will be initialized after DOM loads)
let inputText, outputText, modeSelect, generateBtn, clearInputBtn, clearOutputBtn;
let copyBtn, statusDiv, apiKeyInput, saveKeyBtn, clearKeyBtn;

// State
let isProcessing = false;

// Initialize - wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeDOM();
    loadApiKey();
    setupEventListeners();
});

function initializeDOM() {
    // Get all DOM elements with null checks
    inputText = document.getElementById('inputText');
    outputText = document.getElementById('outputText');
    modeSelect = document.getElementById('mode');
    generateBtn = document.getElementById('generateBtn');
    clearInputBtn = document.getElementById('clearInputBtn');
    clearOutputBtn = document.getElementById('clearOutputBtn');
    copyBtn = document.getElementById('copyBtn');
    statusDiv = document.getElementById('status');
    apiKeyInput = document.getElementById('apiKey');
    saveKeyBtn = document.getElementById('saveKeyBtn');
    clearKeyBtn = document.getElementById('clearKeyBtn');
    
    // Verify all required elements exist
    const requiredElements = {
        'inputText': inputText,
        'outputText': outputText,
        'mode': modeSelect,
        'generateBtn': generateBtn,
        'clearInputBtn': clearInputBtn,
        'clearOutputBtn': clearOutputBtn,
        'copyBtn': copyBtn,
        'status': statusDiv,
        'apiKey': apiKeyInput,
        'saveKeyBtn': saveKeyBtn,
        'clearKeyBtn': clearKeyBtn
    };
    
    const missing = Object.entries(requiredElements)
        .filter(([name, element]) => !element)
        .map(([name]) => name);
    
    if (missing.length > 0) {
        console.error('Missing DOM elements:', missing);
        showError('Page initialization error. Please refresh the page.');
        return false;
    }
    
    return true;
}

function showError(message) {
    // Try to show error even if statusDiv is missing
    if (statusDiv) {
        showStatus(message, 'error');
    } else {
        alert(message);
    }
}

function loadApiKey() {
    // Load API key from localStorage on page load
    if (!apiKeyInput) return;
    
    const savedKey = localStorage.getItem(STORAGE_KEY);
    if (savedKey) {
        apiKeyInput.value = savedKey;
    }
}

function saveApiKey() {
    if (!apiKeyInput) {
        showError('API key input field not found.');
        return;
    }
    
    const key = apiKeyInput.value.trim();
    if (key) {
        localStorage.setItem(STORAGE_KEY, key);
        showStatus('API key saved locally.', 'success');
        setTimeout(hideStatus, 2000);
    } else {
        // Clear if empty
        localStorage.removeItem(STORAGE_KEY);
        showStatus('API key cleared.', 'success');
        setTimeout(hideStatus, 2000);
    }
}

function getApiKey() {
    // Get API key from input field first (most recent), then localStorage
    // This ensures we always use the latest value
    let key = null;
    
    // Check input field first (user may have typed but not saved)
    if (apiKeyInput) {
        const inputKey = apiKeyInput.value.trim();
        if (inputKey) {
            key = inputKey;
        }
    }
    
    // Fall back to localStorage if input is empty
    if (!key) {
        key = localStorage.getItem(STORAGE_KEY);
        if (key) {
            key = key.trim();
            // If we got key from storage, also update the input field
            if (apiKeyInput && !apiKeyInput.value.trim()) {
                apiKeyInput.value = key;
            }
        }
    }
    
    return key || null;
}

function clearSavedKey() {
    localStorage.removeItem(STORAGE_KEY);
    if (apiKeyInput) {
        apiKeyInput.value = '';
    }
    showStatus('Saved API key cleared.', 'success');
    setTimeout(hideStatus, 2000);
}

function setupEventListeners() {
    // Add event listeners only if elements exist
    if (generateBtn) {
        generateBtn.addEventListener('click', handleGenerate);
    }
    if (clearInputBtn) {
        clearInputBtn.addEventListener('click', clearInput);
    }
    if (clearOutputBtn) {
        clearOutputBtn.addEventListener('click', clearOutput);
    }
    if (copyBtn) {
        copyBtn.addEventListener('click', copyOutput);
    }
    if (saveKeyBtn) {
        saveKeyBtn.addEventListener('click', saveApiKey);
    }
    if (clearKeyBtn) {
        clearKeyBtn.addEventListener('click', clearSavedKey);
    }
    
    // Allow Enter+Ctrl/Cmd to generate (with double-submit protection)
    if (inputText) {
        inputText.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                // handleGenerate() already has isProcessing check, so safe to call
                handleGenerate();
            }
        });
    }
    
    // Allow Enter to save API key
    if (apiKeyInput) {
        apiKeyInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveApiKey();
            }
        });
    }
}

async function handleGenerate() {
    // Validate required elements exist
    if (!inputText || !modeSelect || !generateBtn || !outputText) {
        showError('Required form elements not found. Please refresh the page.');
        return;
    }
    
    // Prevent double-submit: check if already processing
    if (isProcessing) {
        return;
    }
    
    // Prevent double-submit: disable button immediately
    if (generateBtn.disabled) {
        return;
    }
    
    const text = inputText.value.trim();
    const mode = modeSelect.value;

    if (!text) {
        showStatus('Please enter some text to process.', 'error');
        return;
    }

    // Set processing state and disable button BEFORE any async operations
    isProcessing = true;
    generateBtn.disabled = true;
    generateBtn.textContent = 'Processing...';
    showStatus('Processing your request...', 'loading');
    outputText.value = '';

    try {
        // Get API key and prepare headers
        const apiKey = getApiKey();
        const headers = {
            'Content-Type': 'application/json',
        };
        
        // Add API key header if available
        if (apiKey) {
            headers['X-OPENAI-KEY'] = apiKey;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                text: text,
                mode: mode
            })
        });

        if (!response.ok) {
            // Try to parse error response as JSON
            let errorMessage = '';
            try {
                const data = await response.json();
                
                // Priority 1: Check for data.error
                if (data.error) {
                    if (typeof data.error === 'string') {
                        errorMessage = data.error;
                    } else {
                        // If error is not a string, stringify it to avoid [object Object]
                        errorMessage = JSON.stringify(data.error);
                    }
                }
                // Priority 2: Check for data.detail
                else if (data.detail) {
                    if (typeof data.detail === 'string') {
                        errorMessage = data.detail;
                    } else if (data.detail.error && typeof data.detail.error === 'string') {
                        errorMessage = data.detail.error;
                    } else {
                        // If detail is not a string and has no error property, stringify it
                        errorMessage = JSON.stringify(data.detail);
                    }
                }
                // Priority 3: Generic fallback - stringify entire response to avoid [object Object]
                else {
                    errorMessage = JSON.stringify(data);
                }
            } catch (parseError) {
                // If JSON parsing fails, use status info as generic fallback
                errorMessage = `Request failed with status ${response.status}: ${response.statusText || 'Unknown error'}`;
            }
            
            // Add friendly upsell for daily limit
            if (errorMessage.includes('Daily free limit') || errorMessage.includes('daily free limit')) {
                errorMessage = 'Daily free limit reached. Add your own OpenAI key for unlimited usage (your billing) or subscribe to unlock more.';
            }
            
            // Improve rate limit error UX
            if (response.status === 429 || errorMessage.toLowerCase().includes('rate limit') || errorMessage.toLowerCase().includes('too many requests')) {
                errorMessage = 'Too many requests. Please wait a moment and try again.';
            }
            
            throw new Error(errorMessage);
        }

        const data = await response.json();
        outputText.value = data.result || '';
        
        showStatus('Text processed successfully!', 'success');
        
        // Auto-hide success message after 3 seconds
        setTimeout(() => {
            hideStatus();
        }, 3000);

    } catch (error) {
        console.error('Error:', error);
        // Display user-friendly error message
        showStatus(`Error: ${error.message}`, 'error');
        outputText.value = '';
    } finally {
        // Always re-enable button and reset state, even on error
        isProcessing = false;
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Fix / Rewrite';
        }
    }
}

function clearInput() {
    if (!inputText) return;
    inputText.value = '';
    inputText.focus();
    hideStatus();
}

function clearOutput() {
    if (!outputText) return;
    outputText.value = '';
    hideStatus();
}

async function copyOutput() {
    if (!outputText || !copyBtn) {
        showError('Copy functionality not available.');
        return;
    }
    
    const text = outputText.value;
    
    if (!text) {
        showStatus('No text to copy.', 'error');
        setTimeout(hideStatus, 2000);
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        copyBtn.style.background = 'var(--success-color)';
        
        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.background = '';
        }, 2000);
    } catch (err) {
        // Fallback for older browsers
        outputText.select();
        document.execCommand('copy');
        showStatus('Text copied to clipboard!', 'success');
        setTimeout(hideStatus, 2000);
    }
}

function showStatus(message, type) {
    if (!statusDiv) {
        console.warn('Status div not found, cannot show message:', message);
        return;
    }
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.classList.remove('hidden');
}

function hideStatus() {
    if (!statusDiv) return;
    statusDiv.classList.add('hidden');
}


