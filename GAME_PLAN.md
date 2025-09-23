# AutoFire - Project Game Plan

## 1. Project Vision

To create a premier, intelligent design suite for fire alarm and low-voltage systems. AutoFire will be a "designer's assistant," moving beyond simple CAD to become a comprehensive tool that understands the components, rules, and logic of system design. The goal is to automate tedious tasks, ensure accuracy, and provide a polished, intuitive user experience that surpasses existing solutions.

## 2. Competitive Analysis Summary

Our primary benchmarks are **FireCAD** and **Bosch Safety Systems Designer**. Key takeaways from our analysis include:

- **Data-Centric Approach:** Both systems are built around extensive parts databases that drive the design process. This is more than just a block library; it includes detailed electrical properties, manufacturer data, and compliance information.
- **AutoCAD Integration:** Both leverage AutoCAD as a familiar front-end, augmenting it with specialized palettes and tools.
- **Workflow Automation:** Core features include automated circuiting, wirepath labeling, and riser diagram generation.
- **Comprehensive Reporting:** A major value-add is the automated generation of reports like Bills of Materials (BOM), voltage drop calculations, battery calculations, and various device schedules.
- **Project Management:** The tools manage projects as a whole, synchronizing drawing files with a project database.

**Our Opportunity:** We can surpass these tools by creating a more modern, intuitive, and flexible standalone application. Our key differentiators will be a superior user experience, greater customization (especially with user-defined formulas), and the eventual integration of an AI assistant (AiHJ).

## 3. High-Level Development Roadmap

This roadmap is divided into logical phases, allowing us to build foundational features first and add complexity over time.

**Phase 1: Core Workflow & UI/UX Refinement (Current Focus)**
- **Objective:** To create a stable, intuitive, and visually appealing core application that designers can immediately find useful. This involves refining the main user interface and the foundational design workflows.
- **Key Tasks:**
    - **Task 1.1:** Reorganize the main window into logical, collapsible panels (System, Devices, Connections).
    - **Task 1.2:** Implement a robust, customizable Settings Menu.
    - **Task 1.3:** Polish the database schema and integration, ensuring all necessary data points for devices and wires are present.
    - **Task 1.4:** Fix any outstanding UI/menu issues.

**Phase 2: Core CAD Functionality**
- **Objective:** Implement fundamental CAD tools that are essential for a professional design workflow.
- **Key Tasks:**
    - **Task 2.1:** Create a dedicated CAD toolbar for core tools.
    - **Task 2.2:** Implement and refine the Measurement Tool.
    - **Task 2.3:** Implement and refine the Scaling Tool.
    - **Task 2.4:** Implement a robust Layer Management system.

**Phase 3: Annotation & Data Integration**
- **Objective:** To create data-driven text placeholders (tokens) for device attributes.
- **Key Tasks:**
    - **Task 3.1:** Define a clear list of available tokens based on the fields in the `devices` table.
    - **Task 3.2:** Create a new tool to select a token from a list and place it on the canvas, associating it with a specific device.
    - **Task 3.3:** Implement the logic that links the placed token's text to the corresponding data field of the device.
    - **Task 3.4:** Enhance the Layer Manager to provide more granular control over the visibility of each specific token type.

**Phase 4: Intelligent Circuiting & Connection Management**
- **Objective:** To build the core intelligence of the application, allowing it to understand and manage electrical circuits.
- **Key Tasks:**
    - **Task 4.1:** Enhance the "Connections Tree" to be a fully interactive circuit management tool.
    - **Task 4.2:** Implement smart wiring tools that understand circuit types (SLC, NAC) and device compatibility.
    - **Task 4.3:** Add functionality to manage circuit properties, like adding extra cable length for calculations.

**Phase 5: Automation & Reporting**
- **Objective:** To automate the most time-consuming documentation and calculation tasks.
- **Key Tasks:**
    - **Task 5.1:** Implement real-time voltage drop and battery size calculations.
    - **Task 5.2:** Build the automated reporting engine for BOMs, device legends, and submittal packages.
    - **Task 5.3:** Create the automatic Riser Diagram generation tool.

**Phase 6: Paperspace & Professional Output**
- **Objective:** To allow users to create complete, professional, multi-page drawing sets for printing and export.
- **Key Tasks:**
    - **Task 6.1:** Build out a full Paperspace mode with viewports, page tabs, and drawing tools.
    - **Task 6.2:** Implement custom Title Blocks and a Job Information manager.
    - **Task 6.3:** Add export functionality for PDF, DXF, and raster image formats.

**Phase 7: Advanced Features & Future-Proofing**
- **Objective:** To introduce next-generation features that will set AutoFire apart.
- **Key Tasks:**
    - **Task 7.1:** Integrate the "AiHJ" assistant.
    - **Task 7.2:** Explore and potentially implement an online, centralized parts database.
    - **Task 7.3:** Implement user accounts and roles (Designer, Salesman).
    - **Task 7.4:** Investigate and plan for potential integrations with platforms like ServiceTrade and Procore.

## 4. Immediate Next Steps

Based on this plan, I will now proceed with **Phase 1**. The first actionable task is to implement the UI/UX feedback you provided.

- **Current Task:** Reorganize the left panel to make the "System" and "Device Palette" sections collapsible, and move the "Device Search" bar into the "Device Palette."
