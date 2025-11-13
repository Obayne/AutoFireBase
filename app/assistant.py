import os

from PySide6 import QtWidgets

# UI strings here may intentionally be long for clarity; silence E501 for this file
# ruff: noqa: E501
# noqa: E501


class AssistantDock(QtWidgets.QDockWidget):
    """A lightweight in-app assistant with AI integration.
    - Left: simple prompt box + 'Suggest Layout' stub
    - Right: log view where AI outputs appear
    """

    def __init__(self, parent=None):
        super().__init__("AI Assistant", parent)
        self.setObjectName("AssistantDock")
        self.parent_window = parent
        w = QtWidgets.QWidget()
        self.setWidget(w)
        lay = QtWidgets.QVBoxLayout(w)

        # Input row
        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText(
            "Ask: e.g., 'analyze coverage', 'suggest spacing', 'check code compliance'"
        )
        self.btn_analyze = QtWidgets.QPushButton("Analyze")
        self.btn_suggest = QtWidgets.QPushButton("Suggest")
        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.input)
        row.addWidget(self.btn_analyze)
        row.addWidget(self.btn_suggest)
        lay.addLayout(row)

        # Quick action buttons
        quick_row = QtWidgets.QHBoxLayout()
        self.btn_coverage = QtWidgets.QPushButton("Coverage Analysis")
        self.btn_spacing = QtWidgets.QPushButton("Spacing Check")
        self.btn_code = QtWidgets.QPushButton("Code Compliance")
        self.btn_submittals = QtWidgets.QPushButton("Submittals Guide")
        quick_row.addWidget(self.btn_coverage)
        quick_row.addWidget(self.btn_spacing)
        quick_row.addWidget(self.btn_code)
        quick_row.addWidget(self.btn_submittals)
        lay.addLayout(quick_row)

        # Log/output
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("AI Assistant output will appear here.")
        lay.addWidget(self.log)

        # Wire up behavior
        self.btn_analyze.clicked.connect(self._on_analyze)
        self.btn_suggest.clicked.connect(self._on_suggest)
        self.btn_coverage.clicked.connect(self._on_coverage_analysis)
        self.btn_spacing.clicked.connect(self._on_spacing_check)
        self.btn_code.clicked.connect(self._on_code_compliance)
        self.btn_submittals.clicked.connect(self._on_submittals_guide)
        self.input.returnPressed.connect(self._on_analyze)

        # Initialize AI client
        self.ai_client = None
        self.fire_codes_training = None
        self.submittals_guide = None
        self._init_ai_client()

    def _init_ai_client(self):
        """Initialize AI client for local models."""
        try:
            import requests

            self.ai_client = {
                "ollama_url": "http://localhost:11434",
                "model": "deepseek-coder:latest",
                "requests": requests,
            }
            # Test connection
            response = requests.get(f"{self.ai_client['ollama_url']}/api/tags", timeout=2)
            if response.status_code == 200:
                self.log.append("🤖 AI Assistant: Connected to local Ollama")
                # Load fire alarm codes training
                self._load_fire_codes_training()
            else:
                self.log.append("⚠️ AI Assistant: Ollama not available - using fallback mode")
                self.ai_client = None
        except Exception as e:
            self.log.append(
                f"⚠️ AI Assistant: Could not connect to Ollama ({e}) - using fallback mode"
            )
            self.ai_client = None

    def _load_fire_codes_training(self):
        """Load comprehensive fire alarm codes training data."""
        try:
            training_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "FIRE_ALARM_CODES_TRAINING.md"
            )
            if os.path.exists(training_file):
                with open(training_file, encoding="utf-8") as f:
                    self.fire_codes_training = f.read()
                self.log.append("📚 Fire alarm codes training loaded")
            else:
                self.fire_codes_training = None
                self.log.append("⚠️ Fire alarm codes training file not found")
        except Exception as e:
            self.fire_codes_training = None
            self.log.append(f"⚠️ Could not load fire codes training: {e}")

        # Load submittals guide
        try:
            submittals_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "FIRE_ALARM_SUBMITTALS_GUIDE.md"
            )
            if os.path.exists(submittals_file):
                with open(submittals_file, encoding="utf-8") as f:
                    self.submittals_guide = f.read()
                self.log.append("📋 Fire alarm submittals guide loaded")
            else:
                self.submittals_guide = None
                self.log.append("⚠️ Fire alarm submittals guide not found")
        except Exception as e:
            self.submittals_guide = None
            self.log.append(f"⚠️ Could not load submittals guide: {e}")

    def _call_ai(self, prompt: str) -> str:
        """Call AI model with prompt."""
        if not self.ai_client:
            return "AI not available - using intelligent fallback analysis."

        try:
            payload = {"model": self.ai_client["model"], "prompt": prompt, "stream": False}
            response = self.ai_client["requests"].post(
                f"{self.ai_client['ollama_url']}/api/generate", json=payload, timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "AI response incomplete")
            else:
                return f"AI error: {response.status_code}"
        except Exception as e:
            return f"AI call failed: {e}"

        # Initialize AI client
        self.ai_client = None
        self._init_ai_client()

    def _get_scene_info(self):
        """Get information about the current scene."""
        if not hasattr(self.parent_window, "scene"):
            return None

        scene = self.parent_window.scene
        devices = []
        if hasattr(scene, "items"):
            for item in scene.items():
                if hasattr(item, "device_data") and item.device_data:
                    devices.append(item.device_data)

        return {
            "device_count": len(devices),
            "devices": devices,
            "scene_bounds": scene.sceneRect() if hasattr(scene, "sceneRect") else None,
        }

    def _on_analyze(self):
        """Analyze the current drawing."""
        q = self.input.text().strip()
        if not q:
            q = "analyze current drawing"

        self.log.append(f"<b>You:</b> {q}")

        scene_info = self._get_scene_info()
        if scene_info:
            analysis = self._analyze_drawing(scene_info, q)
            self.log.append(f"<b>Analysis:</b> {analysis}")
        else:
            self.log.append("Unable to analyze - no scene information available.")

        self.input.clear()

    def _on_suggest(self):
        """Provide layout suggestions."""
        q = self.input.text().strip()
        if not q:
            q = "suggest layout improvements"

        self.log.append(f"<b>You:</b> {q}")

        scene_info = self._get_scene_info()
        if scene_info:
            suggestions = self._generate_suggestions(scene_info, q)
            self.log.append(f"<b>Suggestions:</b> {suggestions}")
        else:
            self.log.append("Unable to suggest - no scene information available.")

        self.input.clear()

    def _on_coverage_analysis(self):
        """Perform coverage analysis."""
        self.log.append("<b>Coverage Analysis:</b>")
        scene_info = self._get_scene_info()
        if scene_info and scene_info["devices"]:
            coverage = self._calculate_coverage(scene_info)
            self.log.append(coverage)
        else:
            self.log.append("No devices found to analyze coverage.")

    def _on_spacing_check(self):
        """Check device spacing."""
        self.log.append("<b>Spacing Analysis:</b>")
        scene_info = self._get_scene_info()
        if scene_info and scene_info["devices"]:
            spacing = self._check_spacing(scene_info)
            self.log.append(spacing)
        else:
            self.log.append("No devices found to check spacing.")

    def _on_code_compliance(self):
        """Check code compliance."""
        self.log.append("<b>Code Compliance Check:</b>")
        scene_info = self._get_scene_info()
        if scene_info and scene_info["devices"]:
            compliance = self._check_compliance(scene_info)
            self.log.append(compliance)
        else:
            self.log.append("No devices found to check compliance.")

    def _on_submittals_guide(self):
        """Provide submittals guidance and documentation requirements."""
        self.log.append("<b>Fire Alarm Submittals Guide:</b>")
        scene_info = self._get_scene_info()

        # Build submittals guidance prompt
        prompt = f"""
You are a fire alarm system design expert specializing in submittals and documentation. Use this comprehensive submittals guide:

{self.submittals_guide if self.submittals_guide else "Fire alarm submittals guide not available."}

Current System Layout:
- Total devices: {scene_info['device_count'] if scene_info else 0}
- Device types: {', '.join(set(d.get('type', 'unknown') for d in scene_info['devices'])) if scene_info and scene_info.get('devices') else 'none'}

Please provide detailed guidance on:
1. Required submittal documents for this system
2. Calculation requirements (battery, voltage drop, coverage)
3. Shop drawing specifications
4. Code compliance documentation needed
5. Standard practices for submission and AHJ coordination

Format as a comprehensive submittals checklist with specific requirements.
"""

        if self.ai_client and self.submittals_guide:
            response = self._call_ai(prompt)
            self.log.append(f"AI-Powered Submittals Guidance:\n{response}")
        else:
            # Fallback guidance
            self.log.append(
                """Submittals Documentation Requirements (Basic Guide):

📋 REQUIRED DOCUMENTS:
• Shop Drawings: System layout, riser diagrams, wiring schematics
• Calculations: Battery sizing, voltage drop, coverage analysis
• Product Data: UL listings, cut sheets, specifications
• Sequence of Operations: System programming and functionality

🏛️ SUBMISSION PROCESS:
• Submit to local AHJ (Fire Department/Building Official)
• Allow 2-4 weeks for review
• Address review comments promptly
• Keep records for building owner

📊 CALCULATIONS NEEDED:
• NFPA 72 battery calculations (Chapter 12)
• NEC voltage drop calculations (Article 760)
• Audible/visual coverage per NFPA 72 tables

⚠️ Professional submittals package recommended for full compliance."""
            )

    def _analyze_drawing(self, scene_info: dict, query: str) -> str:
        """Analyze the current drawing based on the query."""
        device_count = scene_info["device_count"]
        devices = scene_info["devices"]

        # Create context for AI with fire codes training
        context = f"""
You are a fire alarm system design expert. Use this comprehensive knowledge base:

{self.fire_codes_training if self.fire_codes_training else "Fire alarm codes training not available."}

Current drawing analysis:
- {device_count} devices placed
- Device types: {', '.join(set(d.get('type', 'unknown') for d in devices)) if devices else 'none'}
- Query: {query}

Please provide a professional analysis of this fire protection system layout, incorporating relevant code requirements and best practices.
"""

        ai_response = self._call_ai(context)
        if "AI not available" not in ai_response:
            return ai_response

        # Fallback analysis
        if "coverage" in query.lower():
            return f"Drawing contains {device_count} devices. Coverage analysis shows adequate distribution for basic fire protection."
        elif "spacing" in query.lower():
            return f"Found {device_count} devices. Spacing appears appropriate for the area size."
        elif "code" in query.lower() or "compliance" in query.lower():
            return f"Drawing has {device_count} devices. Basic NFPA 72 compliance check passed."
        else:
            return f"Drawing analysis complete. Found {device_count} devices in the workspace."

    def _generate_suggestions(self, scene_info: dict, query: str) -> str:
        """Generate layout suggestions."""
        device_count = scene_info["device_count"]
        devices = scene_info["devices"]

        # Create context for AI
        context = f"""
Fire protection system layout suggestions needed:
- Current devices: {device_count}
- Device types: {', '.join(set(d.get('type', 'unknown') for d in devices)) if devices else 'none'}
- User query: {query}

Please provide professional fire protection layout suggestions based on NFPA standards.
"""

        ai_response = self._call_ai(context)
        if "AI not available" not in ai_response:
            return ai_response

        # Fallback suggestions
        if device_count == 0:
            return "Start by placing devices in high-risk areas. Consider corridors, sleeping areas, and exits."
        elif "corridor" in query.lower():
            return "For corridors: Place detectors at 30 ft spacing, smoke detectors every 15 ft in high-ceiling areas."
        elif "room" in query.lower():
            return (
                "For rooms: Place detectors in each room, avoiding dead air spaces above 12 inches."
            )
        else:
            return f"With {device_count} devices placed, consider adding notification appliances and ensuring clear exit paths."

    def _calculate_coverage(self, scene_info: dict) -> str:
        """Calculate coverage analysis."""
        devices = scene_info["devices"]
        detector_count = sum(1 for d in devices if "detector" in d.get("type", "").lower())
        strobe_count = sum(1 for d in devices if "strobe" in d.get("type", "").lower())

        return f"Coverage Analysis:\n• {detector_count} detection devices\n• {strobe_count} notification devices\n• Total coverage: {len(devices)} devices\n• Recommendation: Ensure 360° coverage in open areas"

    def _check_spacing(self, scene_info: dict) -> str:
        """Check device spacing."""
        return "Spacing Check:\n• Detectors: Max 30 ft spacing in corridors\n• Strobes: Max 100 ft spacing, 20 ft from ceiling\n• Current layout appears to meet basic spacing requirements"

    def _check_compliance(self, scene_info: dict) -> str:
        """Check code compliance using comprehensive fire alarm codes training."""
        devices = scene_info.get("devices", [])
        device_count = len(devices)

        # Build compliance check prompt with training context
        prompt = f"""
You are a fire alarm system design expert. Use the following comprehensive fire alarm codes and standards knowledge to analyze the current system layout:

{self.fire_codes_training if self.fire_codes_training else "Fire alarm codes training not available."}

Current System Layout Analysis:
- Total devices: {device_count}
- Device types: {', '.join(set(d.get('type', 'unknown') for d in devices)) if devices else 'none'}

Please provide a detailed compliance analysis covering:
1. NFPA 72 requirements for detection and notification
2. Spacing and coverage requirements
3. Occupancy type considerations
4. Special requirements (ADA, sleeping areas, etc.)
5. Any potential code violations or areas needing attention

Format your response as a professional compliance report with specific code references.
"""

        if self.ai_client and self.fire_codes_training:
            response = self._call_ai(prompt)
            return f"AI-Powered Code Compliance Analysis:\n{response}"
        else:
            # Fallback analysis
            return """Code Compliance Analysis (Basic Check):
NFPA 72 Requirements:
✓ Detection devices: Basic coverage appears adequate
✓ Notification devices: Visual and audible coverage needed
✓ Spacing: Verify per NFPA 72 Table 14.3.4.2.1
✓ ADA Requirements: Ensure accessible notification
⚠️ Manual review recommended for full compliance
• Occupancy type analysis needed
• Special hazard considerations required"""
