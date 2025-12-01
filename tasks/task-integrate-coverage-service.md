### Task: Integrate Coverage Service into UI

**Objective:**

Connect the frontend coverage visualization and dialogs to the `backend.coverage_service` to automatically calculate and display NFPA-compliant strobe coverage.

**Key Steps:**

1.  **Expose Service Logic:**
    *   In a suitable UI-to-backend bridge (e.g., within `app/main.py` or a dedicated controller module), create a function that takes room dimensions (room size, ceiling height) as input.
    *   This function will call the appropriate method from `backend.coverage_service` (`get_required_wall_strobe_candela` or `get_required_ceiling_strobe_candela`).

2.  **Update Coverage Dialog:**
    *   Modify the 'Coverage...' dialog (referenced in `v0.6.2` changelog) to include a button or checkbox, like "Calculate from Room Size".
    *   When used, this will prompt the user for room dimensions.
    *   The dialog will then call the new bridge function to get the required candela and update the UI fields.

3.  **Refactor `app/coverage.py`:**
    *   The `rebuild_overlay` function may need to be updated to accept candela or a specific coverage shape/size derived from the service's output.
    *   The goal is to draw the coverage overlay based on the calculated values, not just manual input.

**Acceptance Criteria:**

*   A user can open the coverage dialog for a strobe, enter room dimensions, and see the calculated candela value appear.
*   The visual coverage overlay on the main canvas updates to reflect the calculated coverage area.
*   If the service returns `None` (i.e., out of bounds), the UI should inform the user gracefully.
