# Toggle Conduit Fill Labels (no UI required)

You can flip the wirepath label behavior between full labels with fill percent and bundle-only labels using a tiny CLI.

- Show all preferences

```powershell
python -m backend.preferences_cli --list
```

- Read current setting

```powershell
python -m backend.preferences_cli --get hide_conduit_fill
```

- Hide fill (bundle only)

```powershell
python -m backend.preferences_cli --set hide_conduit_fill=true
```

- Show fill again

```powershell
python -m backend.preferences_cli --set hide_conduit_fill=false
```

Notes

- Preferences are saved to a JSON file under your user folder (~/.autofire/preferences.json). Override with AUTOFIRE_PREF_FILE.
- The frontend reads this flag via `frontend.labels_manager`. UI wiring for a visible toggle will be added later.
