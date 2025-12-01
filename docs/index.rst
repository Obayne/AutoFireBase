AutoFire Documentation
======================

**AutoFire** is a professional fire protection CAD system for designing automatic fire sprinkler systems.

.. image:: https://img.shields.io/badge/version-0.4.7-blue.svg
   :alt: Version

.. image:: https://img.shields.io/badge/python-3.11+-blue.svg
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :alt: License

Features
--------

* **CAD Drawing**: Professional 2D CAD engine for fire protection systems
* **DXF Import/Export**: Industry-standard file format support
* **Geometry Operations**: Advanced line, circle, and fillet operations
* **Performance**: Optimized for large-scale projects
* **Extensible**: Plugin architecture for custom tools

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt

Running AutoFire
~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m app.main

Or use the built executable:

.. code-block:: powershell

   .\dist\AutoFire\AutoFire.exe

User Guide
----------

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   user/getting_started
   user/interface
   user/tools
   user/workflows

Developer Guide
---------------

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation

   dev/architecture
   dev/contributing
   dev/testing
   dev/performance

API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   api/backend
   api/cad_core
   api/frontend
   api/app

DevOps & Operations
-------------------

.. toctree::
   :maxdepth: 1
   :caption: Operations

   ops/build_caching
   ops/benchmarking
   ops/monitoring
   ops/ci_cd

Additional Resources
--------------------

.. toctree::
   :maxdepth: 1
   :caption: Resources

   resources/changelog
   resources/roadmap
   resources/faq
   resources/glossary

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
