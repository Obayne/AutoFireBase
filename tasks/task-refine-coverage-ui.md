### Task: Refine Coverage UI/UX

**Objective:**

Improve the user experience by making it clear when a coverage area is based on an automatic NFPA calculation versus a manual override.

**Key Steps:**

1.  **Visual Distinction for Overlays:**
    *   Modify the `rebuild_overlay` function in `app/coverage.py`.
    *   Use a different color or line style for the coverage overlay when it is generated from the `coverage_service` calculation. For example, automatically calculated overlays could be blue, while manual overrides are orange.

2.  **State Tracking on Device:**
    *   The `DeviceItem` class (or a related data model) should store whether its current coverage is `auto` or `manual`.
    *   This state will determine which color is used for the overlay.

3.  **Update Coverage Dialog:**
    *   The dialog should clearly display the source of the current coverage value (e.g., "Automatic: 75cd based on 40ft room" or "Manual: 100cd").
    *   If a user manually changes a value that was previously automatic, the state should be updated to `manual`.

**Acceptance Criteria:**

*   Coverage overlays for automatically calculated values have a distinct visual appearance from manually set ones.
*   The coverage dialog reflects the source of the values.
*   Switching from an automatic to a manual value is seamless and correctly changes the overlay's appearance.
