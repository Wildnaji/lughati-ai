# DOM Integrity Check - Required Element IDs

This document lists all DOM element IDs that must exist in `index.html` and where they are used in `script.js`.

## Required Element IDs

### 1. `apiKey` (Input Field)
- **Location in HTML**: Line 25 - `<input type="password" id="apiKey">`
- **Usage in script.js**:
  - Line 30: `apiKeyInput = document.getElementById('apiKey')`
  - Line 50: `loadApiKey()` - Sets value from localStorage
  - Line 37: `saveApiKey()` - Reads value to save
  - Line 52: `getApiKey()` - Reads value for API calls
  - Line 61: `clearSavedKey()` - Clears value
  - Line 83: Event listener for Enter key to save

### 2. `saveKeyBtn` (Button)
- **Location in HTML**: Line 29 - `<button id="saveKeyBtn">`
- **Usage in script.js**:
  - Line 31: `saveKeyBtn = document.getElementById('saveKeyBtn')`
  - Line 71: Event listener for click to save API key

### 3. `clearKeyBtn` (Button)
- **Location in HTML**: Line 30 - `<button id="clearKeyBtn">`
- **Usage in script.js**:
  - Line 32: `clearKeyBtn = document.getElementById('clearKeyBtn')`
  - Line 72: Event listener for click to clear saved key

### 4. `inputText` (Textarea)
- **Location in HTML**: Line 66 - `<textarea id="inputText">`
- **Usage in script.js**:
  - Line 22: `inputText = document.getElementById('inputText')`
  - Line 92: `handleGenerate()` - Reads value for processing
  - Line 75: Event listener for Ctrl/Cmd+Enter to generate
  - Line 160: `clearInput()` - Clears and focuses

### 5. `outputText` (Textarea)
- **Location in HTML**: Line 78 - `<textarea id="outputText">`
- **Usage in script.js**:
  - Line 23: `outputText = document.getElementById('outputText')`
  - Line 108: `handleGenerate()` - Clears before processing
  - Line 138: `handleGenerate()` - Sets result value
  - Line 151: `handleGenerate()` - Clears on error
  - Line 166: `clearOutput()` - Clears value
  - Line 171: `copyOutput()` - Reads value to copy
  - Line 191: `copyOutput()` - Selects for fallback copy

### 6. `mode` (Select Dropdown)
- **Location in HTML**: Line 44 - `<select id="mode">`
- **Usage in script.js**:
  - Line 24: `modeSelect = document.getElementById('mode')`
  - Line 93: `handleGenerate()` - Reads selected mode value

### 7. `generateBtn` (Button)
- **Location in HTML**: Line 56 - `<button id="generateBtn">`
- **Usage in script.js**:
  - Line 25: `generateBtn = document.getElementById('generateBtn')`
  - Line 67: Event listener for click to generate
  - Line 105: `handleGenerate()` - Disables during processing
  - Line 106: `handleGenerate()` - Changes text to "Processing..."
  - Line 154: `handleGenerate()` - Re-enables after processing
  - Line 155: `handleGenerate()` - Resets text to "Fix / Rewrite"

### 8. `clearInputBtn` (Button)
- **Location in HTML**: Line 57 - `<button id="clearInputBtn">`
- **Usage in script.js**:
  - Line 26: `clearInputBtn = document.getElementById('clearInputBtn')`
  - Line 68: Event listener for click to clear input

### 9. `clearOutputBtn` (Button)
- **Location in HTML**: Line 58 - `<button id="clearOutputBtn">`
- **Usage in script.js**:
  - Line 27: `clearOutputBtn = document.getElementById('clearOutputBtn')`
  - Line 69: Event listener for click to clear output

### 10. `copyBtn` (Button)
- **Location in HTML**: Line 75 - `<button id="copyBtn">`
- **Usage in script.js**:
  - Line 28: `copyBtn = document.getElementById('copyBtn')`
  - Line 70: Event listener for click to copy output
  - Line 181: `copyOutput()` - Changes text to "Copied!"
  - Line 186: `copyOutput()` - Resets text after timeout

### 11. `status` (Status Div)
- **Location in HTML**: Line 86 - `<div id="status">`
- **Usage in script.js**:
  - Line 29: `statusDiv = document.getElementById('status')`
  - Line 107: `handleGenerate()` - Shows loading status
  - Line 140: `handleGenerate()` - Shows success status
  - Line 150: `handleGenerate()` - Shows error status
  - Line 198: `showStatus()` - Sets message and type
  - Line 204: `hideStatus()` - Hides status div

## Verification

All 11 required elements are present in `index.html` and properly referenced in `script.js`.

## Security Notes

- **Server OPENAI_API_KEY**: Never exposed to frontend, only used server-side
- **BYO Key (X-OPENAI-KEY)**: Stored in browser localStorage, sent only in request header
- **No key logging**: API keys are never logged or exposed in error messages

