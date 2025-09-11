
# app/main_startup_safety.py
# This companion module is imported by app/main.py near startup in your last patch.
# If you want to avoid editing main.py directly, this pattern is easy to ship:
def ensure_startup_proto(win):
    try:
        # If nothing selected, pick Generic so placement always works.
        if not getattr(win.view, "current_proto", None):
            win.set_generic_proto()
    except Exception:
        pass
