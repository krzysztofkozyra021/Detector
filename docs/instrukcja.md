# Dokumentacja Techniczna i Instrukcja Obsługi: Traffic Sign Detector

## 1. Wprowadzenie
System Traffic Sign Detector jest zaawansowanym narzędziem do analizy obrazów drogowych. Niniejszy dokument opisuje strukturę projektu, wymagania oraz procedurę uruchomienia i eksploatacji systemu.

## 2. Struktura Projektu
Kluczowe pliki i foldery:
- `app.py`: Główny skrypt aplikacji Flask, obsługujący routing i interfejs webowy.
- `detector.py`: Logika detekcji obiektów, przetwarzanie obrazu (OpenCV) i integracja z modelem.
- `model.py`: Definicje architektur sieci neuronowych (TensorFlow/PyTorch).
- `sign_mapping.py`: Słownik mapujący identyfikatory klas na nazwy znaków w języku polskim.
- `train.py`: Skrypt do trenowania modelu na nowych danych.
- `test_performance.py`: Narzędzie do walidacji czasu odpowiedzi i stabilności systemu.
- `requirements.txt`: Lista wszystkich bibliotek niezbędnych do działania projektu.
- `static/` i `templates/`: Pliki frontendowe (CSS, JavaScript, HTML).

## 3. Wymagania Techniczne
- **Interpreter Python**: Wersja 3.8, 3.9 lub 3.10.
- **Biblioteki**: TensorFlow 2.x, PyTorch 1.x+, OpenCV-Python, Flask, NumPy, Pillow.
- **Zasoby**: Minimum 4GB RAM oraz wsparcie dla instrukcji AVX (procesor).

## 4. Procedura Instalacji

### Krok 1: Przygotowanie środowiska
Zaleca się użycie izolowanego środowiska wirtualnego:
```bash
# Utworzenie środowiska
python -m venv venv

# Aktywacja (Linux/macOS)
source venv/bin/activate

# Aktywacja (Windows)
venv\Scripts\activate
```

### Krok 2: Instalacja zależności
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Krok 3: Konfiguracja wag modelu
Upewnij się, że w głównym katalogu znajduje się plik:
- `polskie_znaki_model_92.pth` (dla pełnego zestawu klas)
- lub `model.h5` (dla modelu Keras).

## 5. Instrukcja Obsługi

### Uruchomienie aplikacji
Aby uruchomić serwer deweloperski, wykonaj polecenie:
```bash
python app.py
```
Po wyświetleniu komunikatu `Running on http://127.0.0.1:5000`, otwórz przeglądarkę pod tym adresem.

### Proces analizy obrazu
1. Na stronie głównej wybierz przycisk przesłania pliku.
2. Wskaż obraz w formacie JPG lub PNG.
3. Kliknij przycisk analizy.
4. System przetworzy obraz i wyświetli:
   - Oryginalne zdjęcie z nałożonymi ramkami detekcji.
   - Nazwę rozpoznanego znaku (zgodnie z kodeksem drogowym).
   - Współczynnik pewności modelu (od 0 do 1).

## 6. Diagnostyka i Rozwiązywanie Problemów

- **Błąd: ModuleNotFoundError**: Oznacza brak biblioteki. Wykonaj ponownie `pip install -r requirements.txt`.
- **Błąd: Model failed to load**: Sprawdź, czy nazwa pliku modelu w `app.py` zgadza się z plikiem na dysku.
- **Błąd: Port 5000 is already in use**: Inna aplikacja korzysta z portu Flask. Możesz zmienić port w `app.py` zmieniając `app.run(port=5001)`.
- **Niska precyzja**: Upewnij się, że zdjęcia nie są rozmazane (Motion Blur) oraz że znak zajmuje co najmniej 30x30 pikseli na oryginalnym zdjęciu.

## 7. Informacje o Zbiorze Danych
System został wytrenowany na zbiorze „Polish Traffic Signs Dataset”. Każda klasa odpowiada konkretnemu kodowi znaku (np. B-33 dla ograniczenia prędkości). Pełna lista dostępna jest w pliku `sign_mapping.py`.
