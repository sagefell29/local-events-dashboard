# Local Events Dashboard

A local event discovery dashboard for Delft and Rijswijk, built with Python and Streamlit.

The dashboard collects events from several local websites, filters them by location, date, and price, and supports Dutch and English display through offline translation with Argos Translate.

## Features

* Collect events from configured local event websites.
* Filter by location: Delft and Rijswijk.
* Choose a time period: 7, 14, 30, or 90 days, or all upcoming events.
* Filter for free events or set a maximum price.
* Switch between Dutch and English event titles and descriptions.
* Cache collected events and translations to reduce repeated work.
* Refresh event data manually.

## Requirements

* Windows 10 or 11
* Python 3.11 or another version supported by the project's dependencies
* Internet access to collect events from the configured websites
* An installed Dutch-to-English language package for Argos Translate

## Setup

Open PowerShell and navigate to the project directory:

```powershell
cd C:\Projects\local-events-dashboard
```

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of its execution policy, you can use the virtual environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Alternatively, activate the environment from Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install dependencies

With the virtual environment activated:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Ensure `requirements.txt` includes all required packages, including `argostranslate`.

### 4. Verify the translation package

The application uses Argos Translate for local Dutch-to-English translation.

If the Dutch-to-English language package has already been installed, no additional setup is necessary. Installing the Python package alone does not necessarily install the translation model.

If setting up on a new machine, install the Dutch-to-English model through Argos Translate's package-management interface or installation API. The model must be installed before using English mode.

## Running the dashboard

From the project root, with the virtual environment activated:

```powershell
python -m streamlit run app.py
```

Streamlit will display a local URL in the terminal, typically:

```text
http://localhost:8501
```

Open that address in your browser.

To stop the application, press `Ctrl+C` in the terminal running Streamlit.

## Refreshing events

The dashboard caches collected event data to avoid scraping the websites on every interaction.

Click **Refresh events** in the dashboard to clear the event collection cache and fetch fresh data.

Translations are cached separately. Repeated translations of identical text can reuse cached results.

## Running tests

Run the tests from the project root, with the virtual environment activated:

```powershell
python -m tests.test
python -m tests.test_collectors
```

These test the existing date-parsing and collector functionality.

## Stopping the application and virtual environment

When you're finished working on the dashboard:

### 1. Stop the Streamlit app

In the terminal running Streamlit, press:

```text
Ctrl+C
```

This stops the local web server. If you have multiple terminals running the app, stop each one separately.

### 2. Deactivate the virtual environment

In the terminal where the virtual environment is activated, run:

```powershell
deactivate
```

Your terminal prompt should no longer show `(.venv)`.

This only deactivates the environment for the current terminal session. It does **not** delete the virtual environment or uninstall any packages.

### 3. Close the terminal

You can now close PowerShell or VS Code's terminal. Your project files, installed packages, and cached application data remain on disk.

### Starting again next time

Open a new terminal and run:

```powershell
cd C:\Projects\local-events-dashboard
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

**Remember:** You don't need to recreate `.venv` or reinstall dependencies every time. Do that only when setting up the project for the first time or when you intentionally rebuild the environment.

## Project structure

```text
local-events-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── models.py
│   ├── translation.py
│   └── sources/
│       ├── __init__.py
│       ├── common.py
│       ├── indelft.py
│       ├── uitrijswijk.py
│       ├── broodfabriek.py
│       └── collector.py
└── tests/
    ├── test.py
    └── test_collectors.py
```

The exact test filenames may differ if the test suite is reorganised later.

## How the application works

1. **Collection:** source-specific modules fetch and parse events from their respective websites.
2. **Normalisation:** the collector combines the results and attempts to remove duplicate events.
3. **Caching:** Streamlit caches the collected events to reduce unnecessary requests.
4. **Filtering:** the dashboard filters events by location, date, and price.
5. **Translation:** Argos Translate converts event titles and descriptions into English when English is selected.
6. **Display:** matching events are rendered as cards with dates, venues, prices, descriptions, and links to the original event pages.

The original event text remains unchanged in the underlying event data.

## Adding another event source

1. Create a new module in `src/sources/`.
2. Reuse common helpers from `common.py` where appropriate.
3. Implement a collector that returns `Event` objects defined in `src/models.py`.
4. Register the collector in `collector.py`.
5. Test the new collector and verify the results in the dashboard.

Keep website-specific scraping logic inside its own module so that changes to one website do not unnecessarily affect the others.

## Current limitations

* Event coverage depends on the websites currently configured.
* Duplicate detection is basic and may miss events listed under different titles or venues.
* Scraped prices, descriptions, venue names, and dates may be incomplete or inconsistent.
* English translations are generated locally and may not always preserve proper nouns or event-specific wording perfectly.
* The dashboard currently requires Streamlit to be running; it is not yet a packaged desktop application.

## Development notes

Activate the virtual environment before installing dependencies, running the app, or executing tests.

After adding dependencies, update `requirements.txt` so the project can be reproduced on another machine:

```powershell
python -m pip freeze > requirements.txt
```

For a more controlled dependency list, edit `requirements.txt` to include only the packages the application actually needs rather than every package installed in the environment.
