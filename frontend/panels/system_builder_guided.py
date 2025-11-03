"""
System Builder - Direct CAD Launch

Professional approach: Go directly to CAD with AI initialization period.
AI learns about user's region, local codes, and project context in the background.
"""

# Import the direct CAD launcher
from frontend.panels.direct_cad_launcher import DirectCADLauncher


# Create alias for backward compatibility
class SystemBuilderWidget(DirectCADLauncher):
    """
    Direct CAD Launcher.

    Professional workflow:
    1. Launch immediately - no menus or wizards
    2. AI initialization period (3-4 seconds)
    3. AI learns: location, codes, manufacturers, compliance
    4. Launch CAD workspace with full context

    No hand-holding - just intelligent background assistance.
    """

    pass


# Also export directly
__all__ = ["SystemBuilderWidget", "DirectCADLauncher"]
