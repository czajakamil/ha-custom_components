# Cookidoo Today (Home Assistant integration)

Integracja do Home Assistant, która czyta dane z Twojego add-ona "Cookidoo Today" (FastAPI).

## Instalacja (HACS - Custom repository)
1. HACS → Integrations → ⋮ → Custom repositories
2. Dodaj URL tego repo jako typ: Integration
3. Zainstaluj i zrestartuj Home Assistant

## Instalacja ręczna
Skopiuj `custom_components/cookidoo_today` do:
`/config/custom_components/cookidoo_today`
i zrestartuj Home Assistant.

## Konfiguracja w HA
Settings → Devices & services → Add integration → "Cookidoo Today"

Wpisz `Base URL` do add-ona, np.:
- http://192.168.x.x:8099  (jeśli masz wystawiony port add-ona na hosta)

## Encje
- Sensory: dzisiaj (count + atrybuty), tydzień (count + atrybuty)
- Kamery: kolaż dnia i tygodnia (/api/today.jpg, /api/week.jpg)

## Serwis
`cookidoo_today.refresh_now` – wymusza odświeżenie.