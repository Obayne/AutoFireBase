# QA Checklist for GUI, Menu, Settings, and Autofire Content Updates

## Separate Windows Architecture
- [ ] Open Model Space window from Window menu
- [ ] Open Paperspace window from Window menu
- [ ] Both windows display independently
- [ ] Tools work in each window (e.g., draw in Model Space)
- [ ] AI Assistant dock visible in both windows

## Project Overview Hub
- [ ] Open Project Overview from Window menu
- [ ] Overview tab: Add/edit notes, milestones, set progress
- [ ] Calendar tab: Select dates, add notes
- [ ] AI Assistant tab: Query commands, see simulation responses
- [ ] Data persists across sessions (check prefs.json)

## Settings
- [ ] Settings dialog includes AI enable and Project Overview startup options
- [ ] Settings dialog includes CAD functionality options (units, drawing scale, line weight, color)
- [ ] Settings dialog includes menu and table options (device palette, properties dock, status bar)
- [ ] Settings dialog includes additional options (auto-save, OSNAP)
- [ ] Prefs save/load correctly (check prefs.json)
- [ ] Project Overview auto-opens if enabled

## Menus
- [ ] Menus consistent across windows
- [ ] OSNAP toggles in View menu
- [ ] Window menu shows all windows

## Content
- [ ] Help > User Guide shows updated guide with new features
- [ ] Help > About mentions new features
- [ ] Keyboard shortcuts accessible

## AI Integration
- [ ] AI responds to "place detector", "draw line", etc. with simulations
- [ ] No actual changes made to scene/database
- [ ] Commands logged in AI dock

## General
- [ ] App starts without errors
- [ ] No crashes when opening/closing windows
- [ ] Prefs persist correctly
