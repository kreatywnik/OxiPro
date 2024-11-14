
# OxiPro - Aplikacja do Konwersji Artykułów na HTML z Integracją AI

## Opis projektu
OxiPro to aplikacja desktopowa napisana w Pythonie, która umożliwia konwersję plików tekstowych na format HTML z automatycznym generowaniem obrazów za pomocą API OpenAI. Aplikacja oferuje dwa tryby działania: generowanie surowego kodu HTML oraz tworzenie projektu z grafikami i stylami CSS.

## Funkcjonalności
- **Konwersja tekstu na HTML**: Przekształcanie plików tekstowych na strukturalny kod HTML.
- **Integracja z OpenAI**: Wykorzystanie API OpenAI do generowania obrazów na podstawie treści artykułu.
- **Podgląd i zapis**: Opcje podglądu wygenerowanego kodu HTML oraz zapisu do pliku.
- **Personalizacja**: Możliwość dostosowania rozdzielczości obrazów oraz szerokości tekstu.

## Technologie
Projekt został stworzony z wykorzystaniem następujących technologii:
- **Python 3.7 lub nowszy**
- **Tkinter**: Biblioteka do tworzenia interfejsu graficznego.
- **OpenAI API**
- **Pillow**: Biblioteka do przetwarzania obrazów.
- **Requests**: Do pobierania zasobów z sieci.
- **Pyperclip**: Do obsługi schowka systemowego.

## Wymagania
- Python 3.7 lub nowszy
- Plik `.env` z kluczem API OpenAI (`OPENAI_API_KEY`)
- Pakiety Python:
  - `openai`
  - `requests`
  - `python-dotenv`
  - `Pillow`
  - `pyperclip`

Możesz je zainstalować za pomocą polecenia:
```bash
pip install -r requirements.txt
```

## Instalacja
1. Sklonuj repozytorium:
```bash
git clone https://github.com/kreatywnik/oxipro.git
cd oxipro
```

2. Zainstaluj wymagane pakiety:
```bash
pip install -r requirements.txt
```

## Uruchamianie aplikacji
Aby uruchomić aplikację, użyj poniższego polecenia:
```bash
python oxipro.py
```

## Instrukcja obsługi
1. **Wybierz plik**: Użyj przycisku „Wybierz plik”, aby załadować plik tekstowy z artykułem.
2. **Przetwórz artykuł**: Wybierz „Surowy kod HTML” lub „Projekt z grafikami”, aby przetworzyć treść.
3. **Podgląd i zapis**: Kliknij „Zapisz”, „Zapisz podgląd” lub „Podgląd”, aby zapisać lub zobaczyć wynik.
4. **Opcje**: Dostosuj rozdzielczość obrazów oraz szerokość tekstu w ustawieniach.

## Struktura plików
- `oxipro.py`: Główny skrypt aplikacji.
- `README.txt`: Instrukcja obsługi i opis projektu.
- `requirements.txt`: Lista wymaganych pakietów Python.
- `podglad.html`: Szablon HTML z treścią artykułu oraz obrazami.

## Autor
Łukasz Fałdowski  
Kontakt: vdzik@interia.pl

## Od autora
Chociaż częściej zajmuję się grafiką niż programowaniem, tym razem mogłem liczyć na wsparcie AI. 
Zdaję sobie sprawę, że aplikacja wygląda dość surowo, ale celem było stworzenie jej funkcjonalnie poprawnej, a niekoniecznie atrakcyjnej wizualnie.

Muszę przyznać, że miałem na wykonanie tego projektu tylko kilkanaście godzin, ponieważ nie sprawdziłem wcześniej maila. 
Najwięcej trudności sprawiło mi zapewnienie bezpieczeństwa przy implementacji klucza API – mam nadzieję, że ostatecznie wszystko działa tak, jak powinno.

Dodałem kilka opcji, które pozwalają na dostosowanie szerokości tekstu i rozmiaru grafik. Oczywiście mam wiele pomysłów na dalszy rozwój, 
od poprawy interfejsu użytkownika po dodanie dodatkowych opcji do edycji. Jednak celem tego projektu było spełnienie wymagań w określonym czasie, 
więc brak czasu oraz doświadczenia ograniczyły moje możliwości.

Mam nadzieję, że aplikacja spełni oczekiwania. Bawcie się dobrze, trzymajcie ciepło i bądźcie kreatywni! Wszelki feedback jak zawsze mile widziany.
