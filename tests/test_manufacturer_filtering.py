import pytest

from frontend.panels.enhanced_panel_dialog import EnhancedPanelSelectionDialog


@pytest.mark.usefixtures("qapp")
def test_enhanced_dialog_manufacturer_combo_and_filtering():
    dlg = EnhancedPanelSelectionDialog()

    # Manufacturer combo should include "All Manufacturers" plus normalized brands
    combo = dlg.manufacturer_combo
    items = [combo.itemText(i) for i in range(combo.count())]

    # Expect 'All Manufacturers' and at least one normalized brand present from DB
    assert "All Manufacturers" in items
    brands = [i for i in items if i != "All Manufacturers"]
    assert len(brands) >= 1, "Expected at least one manufacturer brand in combo"

    # Select NOTIFIER and ensure filtered list contains NOTIFIER models
    # Select the first available brand and ensure filtered list contains only that brand
    first_brand = brands[0]
    combo.setCurrentIndex(items.index(first_brand))
    models = [dlg.panel_list.item(i).text() for i in range(dlg.panel_list.count())]
    assert all(first_brand in m for m in models)

    # Select Fire-Lite and ensure filtered list contains Fire-Lite models
    # The normalized name might be "Fire-Lite Alarms" depending on normalization
    # Switch to 'All Manufacturers' shows a mix (or at least non-empty)
    combo.setCurrentIndex(items.index("All Manufacturers"))
    assert dlg.panel_list.count() >= 1
