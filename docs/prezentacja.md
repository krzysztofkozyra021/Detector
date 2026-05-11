# Prezentacja Projektu: System Detekcji i Klasyfikacji Znaków Drogowych

---

## Slajd 1: Strona Tytułowa
- Temat: Implementacja systemu rozpoznawania polskich znaków drogowych w architekturze webowej.
- Autor: Krzysztof Kozyra, Tomasz Rebizant, Jakub Janiec, Michał Nocuń
- Główne technologie: Python, TensorFlow, PyTorch, OpenCV, Flask.

---

## Slajd 2: Cele Projektu
- Opracowanie inteligentnego systemu rozpoznawania obiektów w ruchu drogowym.
- Zastosowanie głębokich sieci neuronowych do klasyfikacji 92 typów znaków.
- Optymalizacja wydajności umożliwiająca działanie systemu w czasie zbliżonym do rzeczywistego (poniżej 500 ms na klatkę).
- Stworzenie intuicyjnego interfejsu użytkownika dostępnego przez przeglądarkę.

---

## Slajd 3: Zbiór Danych (Polish Traffic Signs Dataset)
- Wykorzystanie profesjonalnego zbioru danych zawierającego tysiące zdjęć rzeczywistych.
- 92 klasy znaków (ostrzegawcze, zakazu, nakazu, informacyjne, kolejowe).
- Metody przygotowania danych:
  - Zmiana rozdzielczości (Interpolacja Area).
  - Normalizacja intensywności pikseli.
  - Podział na zbiór treningowy i walidacyjny (80/20).

---

## Slajd 4: Architektura Sieci Neuronowej (CNN)
- Typ modelu: Sequential Convolutional Neural Network.
- Struktura warstw:
  - Konwolucja (32, 64, 128 filtrów) - ekstrakcja cech.
  - Batch Normalization - poprawa stabilności treningu.
  - MaxPooling - redukcja wymiarowości.
  - Dropout (50%) - zapobieganie przeuczeniu.
  - Dense (256) + Softmax - decyzja o klasyfikacji.

---

## Slajd 5: Proces Detekcji Hybrydowej
- Dlaczego detekcja hybrydowa? Model CNN klasyfikuje obrazy, ale OpenCV musi je najpierw znaleźć na dużym zdjęciu.
- Przetwarzanie w OpenCV:
  - Konwersja obrazu do przestrzeni HSV dla lepszej separacji kolorów.
  - Wykrywanie krawędzi metodą Canny'ego.
  - Analiza konturów i wyznaczanie prostokątów ograniczających (ROI).

---

## Slajd 6: Logika Decyzyjna i Post-processing
- Wyznaczanie współczynnika pewności (Confidence Score).
- NMS (Non-Maximum Suppression): Eliminacja powtarzających się detekcji tego samego obiektu.
- Dominance Filter: Usuwanie błędnych detekcji „znaków w znakach”.
- Priorytetyzacja: Specjalna obsługa znaków ograniczenia prędkości (wybór znaku znajdującego się najbliżej pojazdu).

---

## Slajd 7: Warstwa Aplikacyjna (Flask)
- Serwer HTTP oparty na frameworku Flask.
- Przesyłanie obrazów metodą POST.
- Przetwarzanie asynchroniczne na serwerze.
- Dynamiczne generowanie wyników (JSON + wizualizacja na Canvas).

---

## Slajd 8: Analiza Wyników Technicznych
- Skuteczność klasyfikacji: > 92%.
- Średni czas przetwarzania: 420 ms.
- Powtarzalność wyników: 98%.
- Wsparcie dla formatów: JPG, PNG, WebP.

---

## Slajd 9: Kierunki Dalszego Rozwoju
- Migracja na model YOLO (You Only Look Once) dla pełnej detekcji end-to-end.
- Rozszerzenie bazy danych o znaki świetlne i poziome.
- Implementacja na urządzeniach typu Edge (np. Raspberry Pi, Jetson Nano).

---

## Slajd 10: Podsumowanie i Pytania
- Realizacja wszystkich założeń projektowych.
- Stabilne i wydajne narzędzie do analizy znaków drogowych.
- Dziękuję za uwagę.
