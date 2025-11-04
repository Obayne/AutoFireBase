"""
LVCAD - Low Voltage CAD Professional Interface
=============================================

Professional UI for Low Voltage CAD Intelligence Engine
- Menu organization
- Window functionality
- Professional layout
- Project management
- Analysis tools
"""

import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

# Import core engines
try:
    from autofire_layer_intelligence import CADLayerIntelligence

    from fire_pilot import AiHJ

    HAS_ENGINES = True
except ImportError as e:
    print(f"Warning: Could not import engines - {e}")
    HAS_ENGINES = False

try:
    import ezdxf

    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False


class LVCADMainWindow:
    """
    LVCAD - Low Voltage CAD Professional Interface

    Professional-grade user interface for low voltage CAD analysis
    with integrated menu system, project management, and analysis tools.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LVCAD - Low Voltage CAD Intelligence")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Initialize engines
        self.lvcad_engine = None
        self.aihj_engine = None
        if HAS_ENGINES:
            self.lvcad_engine = CADLayerIntelligence()
            self.aihj_engine = AiHJ()

        # Project state
        self.current_project = None
        self.project_folder = None
        self.analysis_results = {}

        self.setup_ui()
        self.setup_menus()
        self.setup_status_bar()

    def setup_menus(self):
        """Create professional menu system."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="New Project...", command=self.new_project, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="Open Project...", command=self.open_project, accelerator="Ctrl+O"
        )
        file_menu.add_separator()
        file_menu.add_command(label="Import CAD File...", command=self.import_cad_file)
        file_menu.add_command(label="Import Documents...", command=self.import_documents)
        file_menu.add_separator()
        file_menu.add_command(label="Export Analysis...", command=self.export_analysis)
        file_menu.add_command(label="Export Report...", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Analysis Menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Analyze CAD Layers", command=self.analyze_cad_layers)
        analysis_menu.add_command(label="Analyze Documents", command=self.analyze_documents)
        analysis_menu.add_separator()
        analysis_menu.add_command(
            label="Generate Cost Estimate", command=self.generate_cost_estimate
        )
        analysis_menu.add_command(label="Compliance Check", command=self.compliance_check)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Full Project Analysis", command=self.full_analysis)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Layer Pattern Manager", command=self.layer_pattern_manager)
        tools_menu.add_command(label="Device Library", command=self.device_library)
        tools_menu.add_command(label="Cost Database", command=self.cost_database)
        tools_menu.add_separator()
        tools_menu.add_command(label="Preferences...", command=self.preferences)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Project Explorer", command=self.toggle_project_explorer)
        view_menu.add_command(label="Analysis Results", command=self.toggle_analysis_results)
        view_menu.add_command(label="Output Log", command=self.toggle_output_log)
        view_menu.add_separator()
        view_menu.add_command(label="Refresh", command=self.refresh_all, accelerator="F5")

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Getting Started", command=self.show_getting_started)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_separator()
        help_menu.add_command(label="About LVCAD", command=self.show_about)

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.new_project())
        self.root.bind("<Control-o>", lambda e: self.open_project())
        self.root.bind("<F5>", lambda e: self.refresh_all())

    def setup_ui(self):
        """Create main UI layout."""
        # Main container with panedwindow for resizable sections
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Left panel - Project Explorer
        self.left_frame = ttk.Frame(main_paned, width=250)
        main_paned.add(self.left_frame, weight=1)

        # Project Explorer
        ttk.Label(self.left_frame, text="Project Explorer", font=("Arial", 10, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        self.project_tree = ttk.Treeview(self.left_frame, height=15)
        project_scroll = ttk.Scrollbar(
            self.left_frame, orient="vertical", command=self.project_tree.yview
        )
        self.project_tree.configure(yscrollcommand=project_scroll.set)

        self.project_tree.pack(side="left", fill="both", expand=True)
        project_scroll.pack(side="right", fill="y")

        # Center panel - Main work area
        center_paned = ttk.PanedWindow(main_paned, orient="vertical")
        main_paned.add(center_paned, weight=3)

        # Top center - Analysis area
        self.analysis_frame = ttk.LabelFrame(center_paned, text="Analysis Workspace", padding=10)
        center_paned.add(self.analysis_frame, weight=2)

        # Analysis controls
        control_frame = ttk.Frame(self.analysis_frame)
        control_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(control_frame, text="Analyze CAD", command=self.analyze_cad_layers).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(control_frame, text="Analyze Docs", command=self.analyze_documents).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(control_frame, text="Full Analysis", command=self.full_analysis).pack(
            side="left", padx=(0, 5)
        )

        # Analysis results area
        self.analysis_notebook = ttk.Notebook(self.analysis_frame)
        self.analysis_notebook.pack(fill="both", expand=True)

        # CAD Analysis tab
        self.cad_tab = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.cad_tab, text="CAD Analysis")

        self.cad_results = scrolledtext.ScrolledText(self.cad_tab, height=15, font=("Consolas", 9))
        self.cad_results.pack(fill="both", expand=True, padx=5, pady=5)

        # Document Analysis tab
        self.doc_tab = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.doc_tab, text="Document Analysis")

        self.doc_results = scrolledtext.ScrolledText(self.doc_tab, height=15, font=("Consolas", 9))
        self.doc_results.pack(fill="both", expand=True, padx=5, pady=5)

        # Combined Results tab
        self.combined_tab = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.combined_tab, text="Combined Results")

        self.combined_results = scrolledtext.ScrolledText(
            self.combined_tab, height=15, font=("Consolas", 9)
        )
        self.combined_results.pack(fill="both", expand=True, padx=5, pady=5)

        # Bottom center - Output log
        self.log_frame = ttk.LabelFrame(center_paned, text="Output Log", padding=5)
        center_paned.add(self.log_frame, weight=1)

        self.output_log = scrolledtext.ScrolledText(self.log_frame, height=8, font=("Consolas", 8))
        self.output_log.pack(fill="both", expand=True)

        # Right panel - Results summary
        self.right_frame = ttk.Frame(main_paned, width=200)
        main_paned.add(self.right_frame, weight=1)

        # Results summary
        ttk.Label(self.right_frame, text="Results Summary", font=("Arial", 10, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        self.summary_tree = ttk.Treeview(self.right_frame, height=10)
        summary_scroll = ttk.Scrollbar(
            self.right_frame, orient="vertical", command=self.summary_tree.yview
        )
        self.summary_tree.configure(yscrollcommand=summary_scroll.set)

        self.summary_tree.pack(side="left", fill="both", expand=True)
        summary_scroll.pack(side="right", fill="y")

        # Setup treeview columns
        self.summary_tree["columns"] = ("Value",)
        self.summary_tree.column("#0", width=120)
        self.summary_tree.column("Value", width=80)
        self.summary_tree.heading("#0", text="Metric")
        self.summary_tree.heading("Value", text="Value")

    def setup_status_bar(self):
        """Create status bar."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")

        self.status_label = ttk.Label(self.status_frame, text="Ready - LVCAD Professional")
        self.status_label.pack(side="left", padx=5)

        self.progress_bar = ttk.Progressbar(self.status_frame, length=200)
        self.progress_bar.pack(side="right", padx=5)

    def log_message(self, message: str, level: str = "INFO"):
        """Add message to output log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"

        self.output_log.insert("end", log_entry)
        self.output_log.see("end")
        self.root.update_idletasks()

    def update_status(self, message: str):
        """Update status bar."""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    # Menu command implementations
    def new_project(self):
        """Create new LVCAD project."""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.project_folder = folder
            self.current_project = Path(folder).name
            self.update_status(f"Project: {self.current_project}")
            self.log_message(f"New project created: {self.current_project}")
            self.refresh_project_explorer()

    def open_project(self):
        """Open existing LVCAD project."""
        folder = filedialog.askdirectory(title="Open Project Folder")
        if folder:
            self.project_folder = folder
            self.current_project = Path(folder).name
            self.update_status(f"Project: {self.current_project}")
            self.log_message(f"Project opened: {self.current_project}")
            self.refresh_project_explorer()

    def import_cad_file(self):
        """Import CAD file to project."""
        if not self.project_folder:
            messagebox.showwarning("No Project", "Please create or open a project first.")
            return

        file_path = filedialog.askopenfilename(
            title="Import CAD File", filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")]
        )
        if file_path:
            self.log_message(f"CAD file imported: {Path(file_path).name}")
            self.refresh_project_explorer()

    def import_documents(self):
        """Import documents to project."""
        if not self.project_folder:
            messagebox.showwarning("No Project", "Please create or open a project first.")
            return

        file_paths = filedialog.askopenfilenames(
            title="Import Documents", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_paths:
            self.log_message(f"Documents imported: {len(file_paths)} files")
            self.refresh_project_explorer()

    def analyze_cad_layers(self):
        """Analyze CAD layers in project."""
        if not self.project_folder or not HAS_ENGINES:
            messagebox.showwarning(
                "Cannot Analyze", "Project folder required and engines must be available."
            )
            return

        self.update_status("Analyzing CAD layers...")
        self.progress_bar.start()

        def analysis_thread():
            try:
                # Find DXF files
                dxf_files = list(Path(self.project_folder).glob("*.dxf"))
                if not dxf_files:
                    self.log_message("No DXF files found in project", "WARNING")
                    return

                results = []
                for dxf_file in dxf_files:
                    self.log_message(f"Analyzing: {dxf_file.name}")
                    # Perform actual analysis here
                    result = f"Analyzed {dxf_file.name} - Placeholder results\n"
                    results.append(result)

                # Update UI in main thread
                self.root.after(0, lambda: self.display_cad_results("".join(results)))

            except Exception:
                self.root.after(0, lambda: self.log_message(f"Analysis error: {e}", "ERROR"))
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
                self.root.after(0, lambda: self.update_status("CAD analysis complete"))

        threading.Thread(target=analysis_thread, daemon=True).start()

    def analyze_documents(self):
        """Analyze documents using AiHJ."""
        if not self.project_folder or not HAS_ENGINES:
            messagebox.showwarning(
                "Cannot Analyze", "Project folder required and engines must be available."
            )
            return

        self.update_status("Analyzing documents...")
        self.progress_bar.start()

        def analysis_thread():
            try:
                analysis = self.aihj_engine.analyze_pdf_documents(self.project_folder)
                result_text = f"""Document Analysis Results:
Total Documents: {analysis.get('total_documents', 0)}
Total Pages: {analysis.get('total_pages', 0)}
Total Words: {analysis.get('total_words', 0):,}

Fire Protection Terms:
"""
                for term, count in analysis.get("fire_term_counts", {}).items():
                    result_text += f"  {term}: {count}\n"

                self.root.after(0, lambda: self.display_doc_results(result_text))

            except Exception:
                self.root.after(
                    0, lambda: self.log_message(f"Document analysis error: {e}", "ERROR")
                )
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
                self.root.after(0, lambda: self.update_status("Document analysis complete"))

        threading.Thread(target=analysis_thread, daemon=True).start()

    def display_cad_results(self, results: str):
        """Display CAD analysis results."""
        self.cad_results.delete(1.0, "end")
        self.cad_results.insert(1.0, results)
        self.analysis_notebook.select(self.cad_tab)

    def display_doc_results(self, results: str):
        """Display document analysis results."""
        self.doc_results.delete(1.0, "end")
        self.doc_results.insert(1.0, results)
        self.analysis_notebook.select(self.doc_tab)

    def full_analysis(self):
        """Run complete project analysis."""
        self.log_message("Starting full project analysis...")
        self.analyze_cad_layers()
        self.analyze_documents()

    def refresh_project_explorer(self):
        """Refresh project explorer with current files."""
        if not self.project_folder:
            return

        self.project_tree.delete(*self.project_tree.get_children())

        # Add project root
        project_node = self.project_tree.insert("", "end", text=self.current_project, open=True)

        # Add CAD files
        dxf_files = list(Path(self.project_folder).glob("*.dxf"))
        if dxf_files:
            cad_node = self.project_tree.insert(project_node, "end", text="CAD Files", open=True)
            for dxf_file in dxf_files:
                self.project_tree.insert(cad_node, "end", text=dxf_file.name)

        # Add PDF files
        pdf_files = list(Path(self.project_folder).glob("*.pdf"))
        if pdf_files:
            doc_node = self.project_tree.insert(project_node, "end", text="Documents", open=True)
            for pdf_file in pdf_files:
                self.project_tree.insert(doc_node, "end", text=pdf_file.name)

    def refresh_all(self):
        """Refresh all UI elements."""
        self.refresh_project_explorer()
        self.log_message("Interface refreshed")

    # Placeholder menu implementations
    def generate_cost_estimate(self):
        self.log_message("Cost estimation feature - Coming soon")

    def compliance_check(self):
        self.log_message("Compliance checking feature - Coming soon")

    def export_analysis(self):
        self.log_message("Export analysis feature - Coming soon")

    def export_report(self):
        self.log_message("Export report feature - Coming soon")

    def layer_pattern_manager(self):
        self.log_message("Layer pattern manager - Coming soon")

    def device_library(self):
        self.log_message("Device library - Coming soon")

    def cost_database(self):
        self.log_message("Cost database manager - Coming soon")

    def preferences(self):
        self.log_message("Preferences dialog - Coming soon")

    def toggle_project_explorer(self):
        self.log_message("Toggle project explorer - Coming soon")

    def toggle_analysis_results(self):
        self.log_message("Toggle analysis results - Coming soon")

    def toggle_output_log(self):
        self.log_message("Toggle output log - Coming soon")

    def show_getting_started(self):
        messagebox.showinfo("Getting Started", "LVCAD Getting Started Guide - Coming soon")

    def show_user_guide(self):
        messagebox.showinfo("User Guide", "LVCAD User Guide - Coming soon")

    def show_about(self):
        about_text = """LVCAD - Low Voltage CAD Intelligence

Version 1.0.0
Professional low voltage system analysis

Features:
• CAD layer intelligence
• Document analysis
• Cost estimation
• Compliance checking
• Professional reporting

© 2025 LVCAD Systems"""
        messagebox.showinfo("About LVCAD", about_text)

    def run(self):
        """Start the LVCAD application."""
        if not HAS_ENGINES:
            self.log_message(
                "Warning: Core engines not available - limited functionality", "WARNING"
            )
        if not HAS_EZDXF:
            self.log_message("Warning: ezdxf not installed - CAD analysis disabled", "WARNING")

        self.log_message("LVCAD Professional Interface started")
        self.root.mainloop()


def main():
    """Launch LVCAD Professional Interface."""
    print("🏗️ Starting LVCAD - Low Voltage CAD Professional Interface...")

    app = LVCADMainWindow()
    app.run()


if __name__ == "__main__":
    main()
