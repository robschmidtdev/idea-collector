# idea-collector

Lokale Idee-Collector-App (Django + CKEditor + Bootstrap 5, lokal eingebunden).

## Voraussetzungen

- Python 3.11 oder neuer
- Das Projekt liegt im Projektordner (z. B. `C:\MAMP\htdocs\idea-collector`)

## Schnellstart auf deinem Gerät

### Windows

1. Desktop-Shortcut anlegen (optional, erleichtert das Starten):

   ```bash
   python launcher.py install
   ```

2. App starten:

   ```bat
   start_ideacollector.bat
   ```

   oder per Doppelklick auf das Desktop-Shortcut **Idea Collector**.

3. Der Server läuft im Konsolenfenster (Titel `Idea Collector`), das Browser-Fenster öffnet sich danach automatisch.

4. **Stoppen:** Konsolenfenster schließen. Es gibt kein separates Beenden-Icon mehr.

### Linux

```bash
./start_ideacollector.sh
```

- Start per Desktop-Eintrag; das Terminal schließen beendet den Server.

### macOS

```bash
python launcher.py install
```

- Legt die App an, die ein Terminal-Fenster öffnet, in dem der Server startet.
- Terminal-Fenster schließen beendet den Server.

## Ein-Klick-Setup (bootstrap)

```bash
python launcher.py bootstrap --generate-data
```

Der Launcher legt bei Bedarf eine virtuelle Umgebung an, installiert die Abhängigkeiten, führt die Migrationen aus und erzeugt Testdaten (1 Item). Danach startet er den Server.

Mit `--no-data` wird das Generieren von Testdaten übersprungen.

## Ohne Launcher starten

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver --insecure
```

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver --insecure
```

Hinweis: Der Launcher ergänzt `--insecure` und bezieht Bootstrap, Favicon und CKEditor aus den lokalen Statik-Dateien.

## Testdaten

```bash
python manage.py generate_test_data --items 500 --tags 30
python manage.py generate_test_data --flush
```

## Launcher-Befehle

```bash
python launcher.py start
python launcher.py stop
python launcher.py restart
python launcher.py status
python launcher.py install
python launcher.py bootstrap --generate-data
```

Weitere Optionen: `--port <Port>` sowie Umgebungsvariablen `IDEA_COLLECTOR_PORT`, `IDEA_COLLECTOR_PIDFILE`, `IDEA_COLLECTOR_LOGFILE`.
