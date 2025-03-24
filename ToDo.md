# Bazowy PoC: EEG GUI + Neurofeedback

## 1. GUI

### 1.0 – Wybór biblioteki GUI

- [ ] Zastanowić się nad wyborem biblioteki:
  - PyQt6 + pyqtgraph <- wybrana 
  - DearPyGui

---

### 1.1 – Lista urządzeń EEG

- [ ] Przycisk: `Scan available devices`
- [ ] Wyświetlenie listy dostępnych urządzeń do wyboru

---

### 1.2 – Informacje o wybranym urządzeniu

- [ ] Po wyborze urządzenia:
  - [ ] Autodetekcja nazwy urządzenia
  - [ ] Wykrycie typu czepka
  - [ ] Wyświetlenie szczegółów na ekranie
  - [ ] Wątek (publisher–subscriber):
    - [ ] Sprawdza stan baterii co minutę

---

### 1.2.1 – Kalibracja

- [ ] Opcja kalibracji sygnału z elektrod

---

### 1.3 – Data acquisition

- [ ] Opcja rozpoczęcia zbierania danych:
  - [ ] Zapis danych do pliku
  - [ ] Wizualizacja na żywo na ekranie

---

## 2. Edytor danych

- [ ] Możliwość zaznaczania eventów w danych
- [ ] Zaznaczenie punktów czasowych do późniejszego wycięcia

---

## 3. Sesja diagnostyczna neurofeedback

### 3.1 – Układ elektrod

- [ ] Dodanie możliwości wyboru układu elektrod
- [ ] Weryfikacja:
  - [ ] Czy diagnostyka jest możliwa z wybranego układu
  - [ ] Czy wszystkie wymagane elektrody są obecne

---

### 3.2 – Przebieg sesji

- [ ] Obsługa różnych trybów sesji:
  - [ ] `Dry run` – tylko zbieranie i wizualizacja danych
  - [ ] Zaznaczanie eventów podczas sesji
  - [ ] Ręczna edycja danych po zakończeniu
  - [ ] Dane dostępne w wersji:
    - surowej
    - przetworzonej

- [ ] Wizualizacja wyników sesji
