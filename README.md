# Gantt-App

This repository contains a simple [Streamlit](https://streamlit.io/) application for building interactive Gantt charts. It lets you manage tasks directly from the browser and visualize them as timelines using [Plotly](https://plotly.com/python/).

## Features

- Add main tasks and split them into multiple segments with custom start dates and durations.
- Upload a CSV file to load an existing project or continue editing a saved one.
- Choose a single color or a continuous color scale and switch between light or dark themes.
- Generate the chart and download the project data as a CSV file for future use.

## Installation

Install the required Python packages with

```bash
pip install -r requirements.txt
```

## Running the app

Start the application with

```bash
streamlit run app1.py
```

The Streamlit UI opens in your browser. Enter your project details in the sidebar or load a CSV file. Once all tasks and segments are configured, click the **Generate Gantt Chart** button to display the timeline.

## CSV format

CSV files used for loading or downloading projects contain the following columns:

- `Task` – name of the main task
- `Segment` – numeric segment identifier (starting from 1)
- `Start` – start date in ISO format (e.g. `2024-01-31T00:00:00`)
- `End` – end date in ISO format
- `Duration_Months` – duration used when generating the end date

## Saving and loading projects

After you generate a chart you can download the project data using the sidebar button. The downloaded CSV can be uploaded later to continue editing the same project.

---

This lightweight tool aims to make it easy to create and share Gantt charts without requiring additional spreadsheet or project management software.

