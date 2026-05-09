const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadContent = document.getElementById('upload-content');
const previewContainer = document.getElementById('preview-container');
const imagePreview = document.getElementById('image-preview');
const imageWrapper = document.getElementById('image-wrapper');
const selectionBox = document.getElementById('selection-box');
const selectionHint = document.getElementById('selection-hint');
const removeBtn = document.getElementById('remove-image');
const submitBtn = document.getElementById('submit-btn');
const uploadForm = document.getElementById('upload-form');
const resultDiv = document.getElementById('result');
const loadingDiv = document.getElementById('loading');

let isSelecting = false;
let startX, startY;
let selection = { x: 0, y: 0, w: 0, h: 0 };

// Stan ostatniego submitu - potrzebny zeby przeliczyc bboxy z cropa
// na pelny obraz przy rysowaniu
let lastSubmissionWasCropped = false;
let lastSubmissionCropSelection = null;

dropZone.addEventListener('click', (e) => {
    if (previewContainer.style.display === 'none') {
        fileInput.click();
    }
});

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        if (previewContainer.style.display === 'none') {
            dropZone.classList.add('dragover');
        }
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', (e) => {
    if (previewContainer.style.display === 'none') {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                uploadContent.style.display = 'none';
                previewContainer.style.display = 'block';
                selectionHint.style.display = 'block';
                submitBtn.disabled = false;
                resultDiv.style.display = 'none';
                resetSelection();
                clearDetectionBoxes();
            };
            reader.readAsDataURL(file);

            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
        } else {
            alert('Proszę wybrać plik graficzny (PNG, JPG, WebP).');
        }
    }
}

imageWrapper.addEventListener('mousedown', (e) => {
    if (e.target !== imagePreview && e.target !== selectionBox && e.target !== imageWrapper) return;

    // Nowe zaznaczenie - usuwamy stare boxy detekcji
    clearDetectionBoxes();

    isSelecting = true;
    const rect = imageWrapper.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;

    selectionBox.style.left = `${startX}px`;
    selectionBox.style.top = `${startY}px`;
    selectionBox.style.width = '0px';
    selectionBox.style.height = '0px';
    selectionBox.style.display = 'block';
});

window.addEventListener('mousemove', (e) => {
    if (!isSelecting) return;

    const rect = imageWrapper.getBoundingClientRect();
    let currentX = e.clientX - rect.left;
    let currentY = e.clientY - rect.top;

    currentX = Math.max(0, Math.min(currentX, rect.width));
    currentY = Math.max(0, Math.min(currentY, rect.height));

    const x = Math.min(startX, currentX);
    const y = Math.min(startY, currentY);
    const w = Math.abs(startX - currentX);
    const h = Math.abs(startY - currentY);

    selection = { x, y, w, h };

    selectionBox.style.left = `${x}px`;
    selectionBox.style.top = `${y}px`;
    selectionBox.style.width = `${w}px`;
    selectionBox.style.height = `${h}px`;
});

window.addEventListener('mouseup', () => {
    if (!isSelecting) return;
    isSelecting = false;

    if (selection.w < 10 || selection.h < 10) {
        resetSelection();
    }
});

function resetSelection() {
    selection = { x: 0, y: 0, w: 0, h: 0 };
    selectionBox.style.display = 'none';
}

removeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetUpload();
});

function resetUpload() {
    fileInput.value = '';
    imagePreview.src = '';
    uploadContent.style.display = 'block';
    previewContainer.style.display = 'none';
    selectionHint.style.display = 'none';
    submitBtn.disabled = true;
    resultDiv.style.display = 'none';
    resetSelection();
    clearDetectionBoxes();
}

async function getCroppedBlob() {
    if (selectionBox.style.display === 'none') return null;

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    const scaleX = imagePreview.naturalWidth / imagePreview.clientWidth;
    const scaleY = imagePreview.naturalHeight / imagePreview.clientHeight;

    canvas.width = selection.w * scaleX;
    canvas.height = selection.h * scaleY;

    ctx.drawImage(
        imagePreview,
        selection.x * scaleX, selection.y * scaleY, selection.w * scaleX, selection.h * scaleY,
        0, 0, canvas.width, canvas.height
    );

    return new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.95));
}

function clearDetectionBoxes() {
    document.querySelectorAll('.detection-box').forEach(el => el.remove());
}

function drawDetectionBox(prediction) {
    if (!prediction.bbox) return;

    const naturalW = imagePreview.naturalWidth;
    const naturalH = imagePreview.naturalHeight;
    if (!naturalW || !naturalH) return;

    let bx = prediction.bbox.x;
    let by = prediction.bbox.y;
    const bw = prediction.bbox.w;
    const bh = prediction.bbox.h;

    // Jezeli detekcja byla na cropie, bbox jest w przestrzeni cropa.
    // Przesuwamy o offset cropa (w naturalnych pikselach pelnego obrazu).
    if (lastSubmissionWasCropped && lastSubmissionCropSelection) {
        const scaleX = naturalW / imagePreview.clientWidth;
        const scaleY = naturalH / imagePreview.clientHeight;
        bx += lastSubmissionCropSelection.x * scaleX;
        by += lastSubmissionCropSelection.y * scaleY;
    }

    // Pozycje jako % wzgledem pelnego obrazu - skaluja sie automatycznie
    const leftPct = (bx / naturalW) * 100;
    const topPct = (by / naturalH) * 100;
    const widthPct = (bw / naturalW) * 100;
    const heightPct = (bh / naturalH) * 100;

    const box = document.createElement('div');
    box.className = 'detection-box';
    box.style.left = leftPct + '%';
    box.style.top = topPct + '%';
    box.style.width = widthPct + '%';
    box.style.height = heightPct + '%';

    const label = document.createElement('div');
    label.className = 'detection-label';
    label.textContent = `${prediction.class_name} ${(prediction.confidence * 100).toFixed(1)}%`;
    box.appendChild(label);

    imageWrapper.appendChild(box);
}

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (fileInput.files.length === 0) return;

    resultDiv.style.display = 'none';
    loadingDiv.style.display = 'flex';
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <svg class="spinner-small" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
        </svg>
        Analizowanie...
    `;
    clearDetectionBoxes();

    const formData = new FormData();
    const croppedBlob = await getCroppedBlob();

    if (croppedBlob) {
        formData.append('file', croppedBlob, 'crop.jpg');
        lastSubmissionWasCropped = true;
        lastSubmissionCropSelection = { ...selection };
    } else {
        formData.append('file', fileInput.files[0]);
        lastSubmissionWasCropped = false;
        lastSubmissionCropSelection = null;
    }

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        loadingDiv.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
            <svg class="btn-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            Analizuj zdjęcie
        `;

        if (!response.ok) {
            resultDiv.innerHTML = `<div class="error"><strong>Błąd:</strong> ${data.error}</div>`;
        } else {
            let html = `
                <h3>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    Wyniki analizy
                </h3>`;

            if (data.count > 0) {
                data.predictions.forEach(p => {
                    html += `
                        <div class="prediction-item" style="animation-delay: ${data.predictions.indexOf(p) * 0.1}s">
                            <span class="prediction-name">${p.class_name}</span>
                            <span class="prediction-confidence">${(p.confidence * 100).toFixed(1)}%</span>
                        </div>`;
                });

                // Rysuj boxy na obrazku
                data.predictions.forEach(p => drawDetectionBox(p));
            } else {
                html += `
                    <div class="no-results">
                        <p>Nie wykryto żadnych znaków na wybranym obszarze.</p>
                        <span class="hint">Spróbuj przesłać inne zdjęcie lub zaznaczyć obszar dokładniej.</span>
                    </div>`;
            }

            resultDiv.innerHTML = html;
        }

        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (err) {
        loadingDiv.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
            <svg class="btn-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            Analizuj zdjęcie
        `;
        resultDiv.innerHTML = `<div class="error"><strong>Wystąpił błąd:</strong> ${err.message}</div>`;
        resultDiv.style.display = 'block';
    }
});