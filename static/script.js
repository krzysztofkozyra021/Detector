document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('file-input');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    
    if (fileInput.files.length === 0) return;
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    resultDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        loadingDiv.style.display = 'none';
        
        if (!response.ok) {
            resultDiv.innerHTML = `<strong>Błąd:</strong> ${data.error}`;
            resultDiv.className = 'error';
        } else {
            let html = `<strong>Wykryto znaków:</strong> ${data.count}<br><br>`;
            
            if (data.count > 0) {
                html += "<ul>";
                data.predictions.forEach(p => {
                    html += `<li><strong>${p.class_name}</strong> (pewność: ${(p.confidence).toFixed(2)})</li>`;
                });
                html += "</ul>";
            } else {
                html += "Nie wykryto żadnych znaków.";
            }
            
            resultDiv.innerHTML = html;
            resultDiv.className = '';
        }
        
        resultDiv.style.display = 'block';
    } catch (err) {
        loadingDiv.style.display = 'none';
        resultDiv.innerHTML = `<strong>Wystąpił błąd:</strong> ${err.message}`;
        resultDiv.className = 'error';
        resultDiv.style.display = 'block';
    }
});
