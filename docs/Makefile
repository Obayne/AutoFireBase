# Build Sphinx documentation

.PHONY: help html clean serve

help:
	@echo "AutoFire Documentation Builder"
	@echo ""
	@echo "Available targets:"
	@echo "  make html    - Build HTML documentation"
	@echo "  make clean   - Remove built documentation"
	@echo "  make serve   - Build and serve documentation locally"
	@echo "  make help    - Show this help message"

html:
	@echo "Building HTML documentation..."
	sphinx-build -b html . _build/html
	@echo ""
	@echo "✓ Documentation built successfully"
	@echo "  Output: _build/html/index.html"

clean:
	@echo "Cleaning built documentation..."
	rm -rf _build
	@echo "✓ Clean complete"

serve: html
	@echo ""
	@echo "Starting documentation server..."
	@echo "  URL: http://localhost:8000"
	@echo "  Press Ctrl+C to stop"
	@echo ""
	python -m http.server 8000 --directory _build/html
