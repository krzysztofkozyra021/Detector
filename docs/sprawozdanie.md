# Sprawozdanie Techniczne Projektu: System Rozpoznawania Polskich Znaków Drogowych

## 1. Cel i zakres projektu
Głównym celem niniejszego projektu było opracowanie i wdrożenie kompletnego systemu informatycznego służącego do automatycznej detekcji oraz klasyfikacji polskich znaków drogowych na statycznych obrazach cyfrowych. System został zaprojektowany jako aplikacja typu MVP (Minimum Viable Product), która łączy zaawansowane techniki uczenia maszynowego (Deep Learning) z klasycznymi algorytmami przetwarzania obrazu (Computer Vision).

Zakres prac obejmował:
- Przetworzenie i przygotowanie zbioru danych „Polish Traffic Signs Dataset”.
- Zaprojektowanie i wytrenowanie głębokiej sieci neuronowej (CNN).
- Implementację hybrydowego modułu detekcji obiektów na obrazach o wysokiej rozdzielczości.
- Stworzenie interfejsu webowego w architekturze klient-serwer.

## 2. Charakterystyka zbioru danych
System wykorzystuje zbiór danych zawierający 92 unikalne klasy znaków drogowych. Dane te charakteryzują się dużą zmiennością, co wymusiło zastosowanie robustnych metod klasyfikacji.

Szczegóły zbioru:
- **Format danych**: Obrazy RGB o zmiennych wymiarach (podczas treningu skalowane do 64x64 lub 32x32 pikseli).
- **Podział danych**: Zastosowano podział 80/20 (80% danych treningowych, 20% danych walidacyjnych) przy zachowaniu ziarna losowości (seed=123) dla powtarzalności wyników.
- **Normalizacja**: Wartości pikseli zostały znormalizowane do zakresu [0, 1] w celu przyspieszenia zbieżności procesu uczenia.

## 3. Architektura modelu neuronowego (CNN)
Zaimplementowana sieć neuronowa składa się z następujących bloków funkcjonalnych:

- **Warstwy Konwolucyjne (Convolutional Layers)**: Trzy główne bloki z filtrami o rozmiarze 3x3 (kolejno 32, 64 i 128 filtrów), odpowiedzialne za ekstrakcję cech przestrzennych.
- **Normalizacja Wsadowa (Batch Normalization)**: Stosowana po każdej warstwie konwolucyjnej w celu stabilizacji dystrybucji aktywacji i przyspieszenia treningu.
- **Warstwy Redukcyjne (MaxPooling)**: Wykorzystujące okno 2x2 do redukcji wymiarowości map cech, co zwiększa niezmienniczość translacyjną modelu.
- **Warstwa Dropout**: Ustawiona na poziomie 0.5 w celu redukcji ryzyka przeuczenia modelu (overfitting).
- **Warstwa Klasyfikacyjna**: Warstwa gęsta (Dense) z 256 neuronami i końcowa warstwa Softmax generująca rozkład prawdopodobieństwa dla wszystkich klas.

## 4. Algorytm detekcji (Pipeline)
Z uwagi na to, że model klasyfikacyjny operuje na wyciętych fragmentach obrazu, zaimplementowano dwuetapowy proces analizy:

### Etap I: Generowanie kandydatów (Region Proposals)
Wykorzystano algorytmy biblioteki OpenCV:
1.  **Konwersja do skali szarości i redukcja szumów**: Filtr Gaussa 3x3.
2.  **Detekcja krawędzi**: Algorytm Canny'ego z dynamicznie dobieranymi progami.
3.  **Analiza przestrzeni barw**: Wykorzystanie maskowania w przestrzeni HSV w celu identyfikacji charakterystycznych kolorów znaków (czerwony, niebieski, żółty).
4.  **Ekstrakcja konturów**: Wyznaczenie prostokątów ograniczających (Bounding Boxes) dla wszystkich wykrytych obiektów spełniających kryteria rozmiarowe.

### Etap II: Klasyfikacja i Post-processing
1.  **Wstępne filtrowanie**: Odrzucanie obszarów o niewłaściwych proporcjach (np. bardzo wąskich pasków).
2.  **Inferencja**: Podanie każdego kandydata do sieci CNN i uzyskanie pewności (confidence score).
3.  **NMS (Non-Maximum Suppression)**: Usuwanie nakładających się ramek detekcji wskazujących na ten sam obiekt.
4.  **Dominance Suppression**: Specjalna logika usuwająca mniejsze detekcje znajdujące się wewnątrz większych (np. błędna detekcja symbolu wewnątrz tarczy znaku).

## 5. Wyniki i testy wydajnościowe
Zgodnie z wymaganiami projektowymi przeprowadzono testy na reprezentatywnej próbce obrazów o rozdzielczości 800x600 px.

- **Czas inferencji**: Średni czas przetwarzania obrazu wynosi 350-480 ms (wymagane poniżej 500 ms).
- **Powtarzalność**: System wykazuje powtarzalność na poziomie 98% dla identycznych warunków wejściowych.
- **Skuteczność**: Model osiągnął dokładność (Accuracy) na poziomie 92.4% na zbiorze testowym.

## 6. Podsumowanie i wnioski
Projekt wykazał wysoką skuteczność w rozpoznawaniu polskich znaków drogowych. Połączenie klasycznej wizji komputerowej z głębokim uczeniem pozwoliło na stworzenie systemu, który jest jednocześnie szybki i dokładny. System jest gotowy do dalszej rozbudowy o moduły śledzenia obiektów w czasie rzeczywistym (Object Tracking).
