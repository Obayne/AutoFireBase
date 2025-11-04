"""
CAD Spaces System - Model Space and Paper Space for Professional CAD

This module provides the core model/paper space architecture that separates
design work (model space) from printing/layout work (paper space), following
AutoCAD standards.
"""

from .model_space import ModelSpace
from .paper_space import PageSize, PaperSpace
from .viewport import Viewport, ViewportScale

__all__ = ["ModelSpace", "PaperSpace", "PageSize", "Viewport", "ViewportScale"]
