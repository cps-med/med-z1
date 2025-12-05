# app

This is the initial FastAPI + HTMX + Jinja UI shell for med-z1. Current pages are demo-only (overview, HTMX basics, timer) and will be gradually replaced with JLV-like patient views.

## Overview

**app** is a subsystem of the med-z1 application that provides a web-based interface for exploring and understanding data stored in the application’s data mart. It is built using a modern Python stack centered on FastAPI, HTMX, and Jinja2 templates, with support for connecting to Microsoft SQL Server and other backend data sources.

The app subsystem is developed with **Python + FastAPI + HTMX + Jinja2**, using traditional server-side rendering (SSR) enhanced with lightweight, dynamic interactions powered by HTMX. The application uses standard web technologies—HTML, CSS, and JavaScript—along with clean, component-driven templates for consistent UI design.  

## Dependencies

From project root folder:
```
pip install fastapi "uvicorn[standard]" jinja2 python-multipart
```

Then:
```
cd med-z1
uvicorn app.main:app --reload
```

