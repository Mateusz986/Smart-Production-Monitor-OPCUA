# Smart-Production-Monitor-OPCUA

Symulowane stanowisko produkcyjne zliczające wyprodukowane sztuki, napisane w języku Structured Text (ST) w środowisku CODESYS. Dane produkcyjne (licznik sztuk, wydajność, status linii) są udostępniane na zewnątrz przez OPC UA, a następnie odczytywane w czasie rzeczywistym przez dedykowany, asynchroniczny klient napisanym w Pythonie, tak jakby zewnętrzny system nadrzędny (np. MES) monitorował postęp produkcji.


<img width="1232" height="997" alt="image" src="https://github.com/user-attachments/assets/d001356f-2aa0-470c-bed0-4b252ff420b3" />

## Co robi projekt

Automat stanów steruje symulowaną linią produkcyjną. W stanie pracy licznik sztuk rośnie co sekundę, zależnie od zadanego tempa produkcji, a wydajność jest przeliczana na bieżąco jako ekstrapolacja na godzinę względem zadanego celu. Świadome zatrzymanie linii (przycisk stop) zeruje liczniki, traktując to jako koniec zmiany produkcyjnej, natomiast awaria w trakcie pracy nie zeruje niczego, tylko wstrzymuje proces do czasu naprawy, odzwierciedlając ciągłą pracę linii na kilka zmian.

## Stany

| Stan | Opis | Aktywne wyjścia |
|---|---|---|
| `Waiting` | Oczekiwanie na włączenie linii | - |
| `Working` | Linia pracuje, licznik i wydajność aktualizowane co sekundę | - |
| `Fault` | Stan awaryjny, linia zatrzymana | - |

## Wejścia / wyjścia (I/O)

| Zmienna | Typ | Opis |
|---|---|---|
| `xRunSwitch` | BOOL | Włącznik linii |
| `xStopBtn` | BOOL | Zatrzymanie linii, zerowanie liczników (koniec zmiany) |
| `xLineFault` | BOOL | Sygnał awarii |
| `xResetBtn` | BOOL | Kasowanie awarii, działa tylko gdy `xLineFault` = FALSE |
| `iItemCounter` | DINT | Licznik wyprodukowanych sztuk |
| `iSecondElapsed` | DINT | Czas pracy linii w sekundach |
| `rLineSpeed` | REAL | Mnożnik tempa produkcji |
| `iTargetPerHour` | INT | Cel produkcyjny na godzinę |
| `rEfficiency` | REAL | Wydajność w procentach względem celu, liczona jako ekstrapolacja bieżącego tempa na pełną godzinę |

## Dlaczego licznik i czas są typu DINT, nie INT

Zwykły `INT` w CODESYS to liczba 16-bitowa, z maksymalną wartością 32767. Przy zliczaniu sekund pracy ciągłej linii (założenie: praca na kilka zmian, bez zerowania między nimi), ten zakres wyczerpałby się po niecałych 9 godzinach, znacznie mniej niż jedna zmiana robocza. Zmiana typu na `DINT` (32-bitowy) eliminuje ten problem, pozwalając na tygodnie ciągłego działania bez przepełnienia licznika.

## Komunikacja OPC UA

Sterownik udostępnia przez OPC UA kluczowe zmienne produkcyjne (`iItemCounter`, `rEfficiency`, `xRunSwitch`, `xLineFault`), skonfigurowane przez Communication Manager i mapowanie na serwerze OPC UA wbudowanym w CODESYS. Połączenie przetestowane end-to-end klientem UAExpert, z odczytem wartości na żywo, zmieniających się zgodnie z działaniem symulacji.

<img width="1908" height="1015" alt="Zrzut ekranu 2026-09-14 162842" src="https://github.com/user-attachments/assets/60e8e87c-de19-4d79-9b61-873b234b6b7d" />

Konfiguracja połączenia z zewnętrznym klientem wymagała kilku prób i weryfikacji ustawień po stronie serwera (port, mapowanie symboli, poziom bezpieczeństwa autoryzacji), zanim udało się uzyskać stabilne połączenie potwierdzone zrzutem ekranu powyżej.

### Klient Python (IIoT / Asynchroniczny)
Poza weryfikacją w UAExpert, do odczytu danych w czasie rzeczywistym został napisy autorski asynchroniczny klient w **Pythonie** (z użyciem biblioteki `asyncua`). Obsługuje on uwierzytelnianie oparte na certyfikatach (zgodnie z wymogami bezpieczeństwa serwera OPC UA w CODESYS) oraz stabilny polling zmiennych produkcyjnych.

<img width="728" height="282" alt="image" src="https://github.com/user-attachments/assets/0ff4aa52-e074-4d2c-ab51-0bc820c30edb" />


## Środowisko

- CODESYS Development System V3
- Runtime: CODESYS Control Win V3 x64
- Język: Structured Text (ST)
- Komunikacja: OPC UA (serwer wbudowany w CODESYS), testowane klientem UAExpert
- Skrypty / Integracja IT: Python (asyncua, obsługa certyfikatów bezpieczeństwa)

## Autor

Bąk Mateusz
