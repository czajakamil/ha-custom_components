# HA Custom Components

Repozytorium z niestandardowymi integracjami do Home Assistant.

---

## CatPrint

Integracja do drukowania na termicznej drukarce BLE (GOTOOGO C15 / MXW01) przez serwer CatPrint.

### Wymagania
Serwer CatPrint musi działać i być dostępny z Home Assistant.
Sklonuj i uruchom: `python app.py` (domyślnie port 5123).

### Instalacja ręczna
Skopiuj `custom_components/catprint` do `/config/custom_components/catprint`
i zrestartuj Home Assistant.

### Konfiguracja
Settings → Devices & services → Add integration → **CatPrint**

Wpisz URL serwera, np. `http://192.168.1.X:5123`

### Encje
- `sensor.catprint_status` – status drukarki (idle / printing / disconnected / error)
- `sensor.catprint_pending_jobs` – liczba zadań czekających w kolejce

### Serwisy
| Serwis | Opis |
|---|---|
| `catprint.print_text` | Drukuje tekst (`text`, `font_size`) |
| `catprint.print_shopping_list` | Lista zakupów z checkboxami (`items`, `title`) |
| `catprint.print_notification` | Karta powiadomienia (`title`, `message`, `source`) |
| `catprint.print_qr` | Kod QR (`data`, `caption`) |
| `catprint.scan` | Skanuje BLE i łączy z drukarką |
| `catprint.flush_queue` | Drukuje wszystkie oczekujące zadania |

### Notify
Dostępna platforma `notify.catprint` – możesz używać w automatyzacjach:
```yaml
service: notify.catprint
data:
  message: "Drzwi wejściowe otwarte!"
  data:
    font_size: 28
```

---

## Cookidoo Today

Integracja do Home Assistant, która czyta dane z Twojego add-ona "Cookidoo Today" (FastAPI).

### Instalacja ręczna
Skopiuj `custom_components/cookidoo_today` do:
`/config/custom_components/cookidoo_today`
i zrestartuj Home Assistant.

### Konfiguracja
Settings → Devices & services → Add integration → "Cookidoo Today"

Wpisz `Base URL` do add-ona, np.:
- http://192.168.x.x:8099

### Encje
- Sensory: dzisiaj (count + atrybuty), tydzień (count + atrybuty)
- Kamery: kolaż dnia i tygodnia (/api/today.jpg, /api/week.jpg)

### Serwis
`cookidoo_today.refresh_now` – wymusza odświeżenie.