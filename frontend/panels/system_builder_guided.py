"""
Enhanced System Builder - Intuitive Guided Workflow

This wrapper provides the new guided system builder as the main SystemBuilderWidget,
maintaining compatibility while providing a much more intuitive user experience.
"""

# Import the guided system builder
from .guided_system_builder import GuidedSystemBuilderWidget


# Create alias for backward compatibility
class SystemBuilderWidget(GuidedSystemBuilderWidget):
    """
    Enhanced System Builder with guided workflow.

    Provides intuitive step-by-step guidance for building fire alarm systems:
    1. Building Assessment - Understanding requirements
    2. Panel Selection - Choosing the right control panel
    3. Device Planning - Selecting detection and notification devices
    4. Wire Planning - Specifying circuits and wiring
    5. System Review - Final review and deployment

    Works for any skill level - from beginners to experts.
    """

    pass


# Also export the guided version directly
__all__ = ["SystemBuilderWidget", "GuidedSystemBuilderWidget"]
