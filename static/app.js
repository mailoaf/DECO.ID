document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const decoderInput = document.getElementById('decoder-input');
    const decoderOutput = document.getElementById('decoder-output');
    const successBanner = document.getElementById('success-banner');
    const successBannerText = document.getElementById('success-banner-text');
    const bubblesList = document.getElementById('decoder-bubbles-list');
    const notification = document.getElementById('notification');

    const btnPaste = document.getElementById('btn-paste');
    const btnClear = document.getElementById('btn-clear');
    const btnCopy = document.getElementById('btn-copy');

    // Debounce timer
    let debounceTimer;

    // Scrambling cipher text helper
    const cipherChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/";
    let scrambleInterval;

    function scrambleText(targetText) {
        if (scrambleInterval) clearInterval(scrambleInterval);
        
        if (!targetText) {
            decoderOutput.innerText = '';
            return;
        }

        const totalSteps = 22; // Smooth 1-second animation
        let step = 0;

        scrambleInterval = setInterval(() => {
            let currentVal = '';
            for (let j = 0; j < targetText.length; j++) {
                const targetChar = targetText[j];

                if (/\s/.test(targetChar)) {
                    currentVal += targetChar;
                    continue;
                }

                // Show correct character if locked, else show random cypher symbol
                const progressLimit = (step / totalSteps) * targetText.length;
                if (j < progressLimit) {
                    currentVal += targetChar;
                } else {
                    currentVal += cipherChars[Math.floor(Math.random() * cipherChars.length)];
                }
            }

            decoderOutput.innerText = currentVal;
            step++;

            if (step > totalSteps) {
                clearInterval(scrambleInterval);
                decoderOutput.innerText = targetText;
            }
        }, 50);
    }

    // Toast Notification helper
    function showNotification(message, isSuccess = true) {
        notification.textContent = message;
        notification.style.background = isSuccess ? 'var(--primary-red)' : 'rgba(239, 68, 68, 0.95)';
        notification.classList.add('show');
        setTimeout(() => {
            notification.classList.remove('show');
        }, 2200);
    }

    const defaultDecoders = [
        "Unicode Escape",
        "HTML Entities",
        "URL Encode",
        "Morse Code",
        "Binary",
        "Decimal",
        "Octal",
        "Base16 (Hex)",
        "Base32",
        "Base58",
        "Base64",
        "Base85",
        "ASCII85"
    ];

    // Reset interface to initial state
    function clearAll() {
        decoderInput.innerText = '';
        scrambleText('');
        
        successBanner.className = 'success-banner-box mismatch';
        successBannerText.textContent = 'NO SUCCESS DETECTED';
        
        // Render persistent list of decoders instead of placeholder row
        renderDecoderTable(defaultDecoders.map(name => ({
            name: name,
            status: 'MISMATCH'
        })));
    }

    // Decode execution
    async function runDecoding() {
        const text = decoderInput.innerText;
        if (!text.trim()) {
            clearAll();
            return;
        }

        try {
            const response = await fetch('/api/decode-all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await response.json();

            if (data.success && data.results) {
                // Find primary success decoder
                const firstSuccess = data.results.find(r => r.status === 'SUKSES');

                if (firstSuccess) {
                    // Trigger scrambling animation
                    scrambleText(firstSuccess.result);
                    
                    // Update Banner
                    successBanner.className = 'success-banner-box success';
                    successBannerText.textContent = `${firstSuccess.name.toUpperCase()} SUCCESS`;
                } else {
                    // No successes
                    scrambleText('');
                    
                    successBanner.className = 'success-banner-box mismatch';
                    successBannerText.textContent = 'NO SUCCESS DETECTED';
                }

                // Render dynamic table rows
                renderDecoderTable(data.results);
            } else {
                scrambleText('');
                successBanner.className = 'success-banner-box mismatch';
                successBannerText.textContent = 'NO SUCCESS DETECTED';
                
                // Show default decoders list on error
                renderDecoderTable(defaultDecoders.map(name => ({
                    name: name,
                    status: 'MISMATCH'
                })));
            }
        } catch (err) {
            console.error(err);
            showNotification('Failed to connect to server.', false);
        }
    }

    // Render status bubbles
    function renderDecoderTable(results) {
        bubblesList.innerHTML = '';

        results.forEach((item, index) => {
            const div = document.createElement('div');
            const isSuccess = item.status === 'SUKSES';
            
            div.className = 'decoder-bubble' + (isSuccess ? ' success' : '');
            div.style.animationDelay = `${index * 40}ms`;

            const name = item.name;
            const statusLabel = isSuccess ? 'FOUND' : 'NOT FOUND';
            const statusClass = isSuccess ? 'status-txt-success' : 'status-txt-mismatch';

            div.innerHTML = `
                <span class="bubble-name">${name}</span>
                <span class="bubble-status ${statusClass}">${statusLabel}</span>
            `;
            bubblesList.appendChild(div);
        });
    }

    // Event Listeners
    decoderInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(runDecoding, 300); // responsive debounce
    });

    btnPaste.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            decoderInput.innerText = text;
            runDecoding(); // Run immediately on paste
        } catch (err) {
            showNotification('Failed to read clipboard. Please grant permission.', false);
        }
    });

    btnClear.addEventListener('click', () => {
        clearAll();
        showNotification('Input cleared.');
    });

    btnCopy.addEventListener('click', async () => {
        if (!decoderOutput.innerText.trim()) {
            showNotification('No result to copy!', false);
            return;
        }
        try {
            await navigator.clipboard.writeText(decoderOutput.innerText);
            showNotification('Text copied to clipboard!');
        } catch (err) {
            showNotification('Failed to copy to clipboard.', false);
        }
    });

    // Initialize list of 13 decoders on startup
    clearAll();
});

