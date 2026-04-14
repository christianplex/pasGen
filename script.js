const passwordDisplay = document.getElementById('password-display');
const lengthSlider = document.getElementById('length-slider');
const lengthValue = document.getElementById('length-value');
const generateBtn = document.getElementById('generate-btn');
const strengthBar = document.getElementById('strength-bar');
const toastContainer = document.getElementById('toast-container');

const API_URL = "https://us-central1-plexarian-pass.cloudfunctions.net/generate-passphrase";

// Update length display
lengthSlider.addEventListener('input', () => {
    const val = lengthSlider.value;
    lengthValue.textContent = val;
    // Show placeholders matching length
    passwordDisplay.textContent = '•'.repeat(val);
    strengthBar.style.width = '0%';
});

// Generate Memorable Password (API - Rate Limited)
async function generateMemorablePassword() {
    const length = lengthSlider.value;
    showToast('Consultando base de seguridad...');
    
    try {
        const response = await fetch(`${API_URL}?length=${length}`);
        const data = await response.json();

        if (response.status === 429) {
            showToast(data.error || 'Límite excedido');
            return null;
        }

        if (!response.ok) {
            throw new Error(data.error || 'Error en el servidor');
        }

        return data.password;
    } catch (err) {
        showToast('Error de conexión');
        console.error(err);
        return null;
    }
}

// Update strength bar (Simple visual feedback)
function updateStrength(password) {
    let strength = (password.length / 16) * 100;
    strengthBar.style.width = strength + '%';
    
    if (strength < 40) strengthBar.style.background = '#ff4d4d';
    else if (strength < 70) strengthBar.style.background = '#ffa500';
    else strengthBar.style.background = '#FF3364';
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('¡Copiada al portapapeles!');
    } catch (err) {
        console.error('Error al copiar: ', err);
    }
}

function showToast(message) {
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Main Action
generateBtn.addEventListener('click', async () => {
    const originalBtnText = generateBtn.innerHTML;
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="btn-text">GENERANDO...</span>';
    
    passwordDisplay.textContent = 'Solicitando...';
    passwordDisplay.style.color = 'var(--text-muted)';

    const password = await generateMemorablePassword();
    generateBtn.disabled = false;
    generateBtn.innerHTML = originalBtnText;
    
    if (password) {
        displayPassword(password);
        copyToClipboard(password);
    } else {
        passwordDisplay.textContent = 'REINTENTAR';
        passwordDisplay.style.color = 'rgba(255,255,255,0.3)';
    }
});

function displayPassword(password) {
    passwordDisplay.innerText = password;
    passwordDisplay.style.color = 'white';
    updateStrength(password);
    
    passwordDisplay.style.transform = 'scale(1.05)';
    setTimeout(() => {
        passwordDisplay.style.transform = 'scale(1)';
    }, 200);
}
