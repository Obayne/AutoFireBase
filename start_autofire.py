#!/usr/bin/env python3
"""
AUTOFIRE LAUNCHER - Start AutoFire as visible application
"""

import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time

# Add AutoFire to path
sys.path.append('C:/Dev/Autofire')

class AutoFireApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 AutoFire AI - Live Application")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Status
        self.status_var = tk.StringVar(value="AutoFire AI - Ready")
        self.results_var = tk.StringVar(value="No analysis yet")
        
        self.create_widgets()
        self.load_autofire()
    
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="🔥 AutoFire AI - Construction Intelligence", 
                        font=("Arial", 16, "bold"), fg="orange", bg="#2b2b2b")
        title.pack(pady=10)
        
        # Status
        status_frame = tk.Frame(self.root, bg="#2b2b2b")
        status_frame.pack(pady=5)
        
        tk.Label(status_frame, text="Status:", fg="white", bg="#2b2b2b").pack(side=tk.LEFT)
        status_label = tk.Label(status_frame, textvariable=self.status_var, 
                               fg="lime", bg="#2b2b2b", font=("Arial", 10, "bold"))
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(pady=20)
        
        self.analyze_btn = tk.Button(btn_frame, text="Analyze PDF", 
                                    command=self.analyze_pdf,
                                    bg="orange", fg="black", font=("Arial", 12, "bold"),
                                    width=15, height=2)
        self.analyze_btn.pack(side=tk.LEFT, padx=10)
        
        self.test_btn = tk.Button(btn_frame, text="Test RFI Engine", 
                                 command=self.test_rfi,
                                 bg="lime", fg="black", font=("Arial", 12, "bold"),
                                 width=15, height=2)
        self.test_btn.pack(side=tk.LEFT, padx=10)
        
        # Results area
        results_frame = tk.LabelFrame(self.root, text="Analysis Results", 
                                     fg="white", bg="#2b2b2b", font=("Arial", 12, "bold"))
        results_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.results_text = tk.Text(results_frame, bg="#1e1e1e", fg="white", 
                                   font=("Consolas", 10), wrap=tk.WORD)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load sample PDF button
        sample_btn = tk.Button(self.root, text="Load Sample PDF", 
                              command=self.load_sample,
                              bg="cyan", fg="black", font=("Arial", 10, "bold"))
        sample_btn.pack(pady=10)
    
    def load_autofire(self):
        """Load AutoFire AI modules"""
        try:
            from cad_core.intelligence.pdf_analyzer import PDFConstructionAnalyzer
            from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine
            
            self.pdf_analyzer = PDFConstructionAnalyzer()
            self.rfi_engine = RFIIntelligenceEngine()
            
            self.status_var.set("AutoFire AI - Loaded Successfully")
            self.log("✅ AutoFire AI modules loaded successfully")
            self.log(f"✅ PDF Analyzer: {type(self.pdf_analyzer).__name__}")
            self.log(f"✅ RFI Engine: {type(self.rfi_engine).__name__}")
            
        except Exception as e:
            self.status_var.set("AutoFire AI - FAILED TO LOAD")
            self.log(f"❌ Error loading AutoFire: {e}")
    
    def log(self, message):
        """Add message to results"""
        timestamp = time.strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def analyze_pdf(self):
        """Analyze PDF file"""
        if not hasattr(self, 'pdf_analyzer'):
            messagebox.showerror("Error", "AutoFire AI not loaded!")
            return
        
        # Use sample PDF
        pdf_path = "C:/Dev/Autofire/Projects/floorplan-sample.pdf"
        
        try:
            self.status_var.set("Analyzing PDF...")
            self.log(f"🔄 Starting PDF analysis: {pdf_path}")
            
            result = self.pdf_analyzer.analyze_construction_set(pdf_path)
            
            self.log(f"✅ Analysis complete!")
            self.log(f"📋 Project: {result.project_name}")
            self.log(f"📄 Pages: {result.total_pages}")
            self.log(f"🏗️ Floor plans: {len(result.floor_plans)}")
            self.log(f"🔥 Fire alarm plans: {len(result.fire_alarm_plans)}")
            
            self.analysis_result = result
            self.status_var.set("PDF Analysis Complete")
            
        except Exception as e:
            self.log(f"❌ PDF Analysis failed: {e}")
            self.status_var.set("PDF Analysis Failed")
    
    def test_rfi(self):
        """Test RFI engine"""
        if not hasattr(self, 'rfi_engine'):
            messagebox.showerror("Error", "RFI Engine not loaded!")
            return
        
        if not hasattr(self, 'analysis_result'):
            messagebox.showwarning("Warning", "Analyze PDF first!")
            return
        
        try:
            self.status_var.set("Running RFI Analysis...")
            self.log("🔍 Testing RFI engine (the critical fix)...")
            
            rfi_result = self.rfi_engine.analyze_project_issues(self.analysis_result)
            
            self.log("✅ RFI Engine works - NO CRASH!")
            self.log(f"🔍 Issues identified: {len(rfi_result)}")
            self.log("🎉 Critical fix is working!")
            
            self.status_var.set("RFI Analysis Complete - NO CRASHES")
            
        except Exception as e:
            self.log(f"❌ RFI Engine failed: {e}")
            self.status_var.set("RFI Analysis Failed")
    
    def load_sample(self):
        """Load sample PDF path"""
        self.log("📁 Sample PDF: C:/Dev/Autofire/Projects/floorplan-sample.pdf")
        import os
        if os.path.exists("C:/Dev/Autofire/Projects/floorplan-sample.pdf"):
            size = os.path.getsize("C:/Dev/Autofire/Projects/floorplan-sample.pdf")
            self.log(f"✅ Sample PDF found ({size} bytes)")
        else:
            self.log("❌ Sample PDF not found")
    
    def run(self):
        """Start the application"""
        self.log("🚀 AutoFire AI Application Started")
        self.log("👤 USER: You can now see AutoFire running!")
        self.root.mainloop()

if __name__ == "__main__":
    print("🔥 Starting AutoFire AI Application...")
    app = AutoFireApp()
    app.run()