# MKS API

### Deze api levert de volgende data:

- Persoonsgegevens uit de BRP
- HR gegevens op basis van BSN (+kvk nummer) (zzp'er)
- HR gegevens op basis van KVK nummer
- Overzicht ID kaarten en Paspoorten

### Local env

// Initialize

- `python -m venv venv`
- Mac: `source venv/bin/activate` Windows: `.\venv\Scripts\Activate.ps1` (in case of UnauthorizedAccess run `Set-ExecutionPolicy Unrestricted -Scope Process` beforehand)
- `pip install -r requirements-root.txt`

// unittest
`python -m unittest`

// requirements.txt maken
`make requirements`

// dev server
`sh scripts/run-dev.sh`

### Kenmerken

- Het bronsysteem is een soap/stuf api MKS, deze haalt gegevens uit de brp.
- Het bronsysteem wordt bevraagd op basis van een BSN of KVK nummer.
- De output van de api is JSON formaat.

### Dependencies

- Voeg de naam van de library/dependency toe aan requirements-root.txt
- Voer volgende commando uit: `make requirements`

### Development & testen

- Er is geen uitgebreide lokale set-up waarbij ontwikkeld kan worden op basis van een "draaiende" api. Dit zou gemaakt / geïmplementeerd moeten worden.
- Alle tests worden dichtbij de geteste functionaliteit opgeslagen. B.v `some_service.py` en wordt getest in `test_some_service.py`.

### CI/CD

- De applicatie wordt verpakt in een Docker container.
- Bouwen en deployen van de applicatie gebeurt in Github en Azure DevOps.

### Release to production

```
~ cd scripts
~ sh release.sh --minor [--major [--patch]]
```
