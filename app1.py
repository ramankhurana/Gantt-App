import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def create_gantt_chart_app():
    st.set_page_config(layout="wide")
    st.title("Advanced Gantt Chart Creator")

    st.write("Enter your project tasks, their segments, and customize the chart.")

    st.sidebar.header("Project Management")
    uploaded_files = st.sidebar.file_uploader(
        "Upload saved project CSVs", type="csv", accept_multiple_files=True
    )
    download_button_placeholder = st.sidebar.empty()

    # Initialize session state defaults
    if 'tasks_data' not in st.session_state:
        st.session_state.tasks_data = []
    if 'num_main_tasks' not in st.session_state:
        st.session_state.num_main_tasks = 1
    if 'current_plot_title' not in st.session_state:
        st.session_state.current_plot_title = "My Project Timeline"
    if 'selected_theme' not in st.session_state:
        st.session_state.selected_theme = "White Background"
    if 'use_single_color' not in st.session_state:
        st.session_state.use_single_color = True
    if 'selected_discrete_color_name' not in st.session_state:
        st.session_state.selected_discrete_color_name = "Default Blue"
    if 'selected_continuous_scale' not in st.session_state:
        st.session_state.selected_continuous_scale = "Plasma"
    if 'task_names' not in st.session_state:
        st.session_state.task_names = [f"Task {i+1}" for i in range(st.session_state.num_main_tasks)]

    # --- File Upload Processing with Proper Rerun Handling ---
    if uploaded_files:
        try:
            df_list = []
            for f in uploaded_files:
                df_tmp = pd.read_csv(f)
                df_tmp['Start'] = pd.to_datetime(df_tmp['Start'], errors='coerce')
                df_tmp['End'] = pd.to_datetime(df_tmp['End'], errors='coerce')

                if df_tmp['Start'].isnull().any() or df_tmp['End'].isnull().any():
                    raise ValueError("Invalid datetime format in CSV.")

                df_list.append(df_tmp)

            loaded_df = pd.concat(df_list, ignore_index=True)

            st.session_state.tasks_data = loaded_df.to_dict('records')
            st.session_state.num_main_tasks = loaded_df['Task'].nunique()
            st.session_state.current_plot_title = uploaded_files[0].name.replace(".csv", "").replace("_gantt_project", "").replace("_", " ")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
            st.session_state.tasks_data = []
            st.session_state.num_main_tasks = 1
            st.session_state.current_plot_title = "My Project Timeline"

    # --- Chart Configuration UI ---
    plot_title = st.text_input("Enter the title for your Gantt Chart:", value=st.session_state.current_plot_title, key="plot_title_input")
    st.session_state.current_plot_title = plot_title

    st.sidebar.subheader("Chart Theme")
    theme_options = ["White Background", "Dark Background (Default Plotly)"]
    selected_theme = st.sidebar.radio("Choose background theme:", theme_options, index=theme_options.index(st.session_state.selected_theme), key="theme_selector")
    st.session_state.selected_theme = selected_theme

    predefined_colors = {
        "Default Blue": "#1f77b4",
        "Emerald Green": "#2ca02c",
        "Crimson Red": "#d62728",
        "Goldenrod Yellow": "#ff7f0e",
        "Purple Haze": "#9467bd"
    }
    selected_discrete_color_name = st.selectbox("Choose a single color for all tasks:", list(predefined_colors.keys()), index=list(predefined_colors.keys()).index(st.session_state.selected_discrete_color_name), key="discrete_color_selector")
    st.session_state.selected_discrete_color_name = selected_discrete_color_name
    selected_discrete_color_code = predefined_colors[selected_discrete_color_name]

    continuous_color_scales = ["Plasma", "Viridis", "Inferno", "Magma", "Cividis", "Blues", "Greens", "Reds", "Purples", "RdBu", "Portland", "Greys"]
    selected_continuous_scale = st.selectbox("Or choose a color temperature scale:", continuous_color_scales, index=continuous_color_scales.index(st.session_state.selected_continuous_scale), key="continuous_color_selector")
    st.session_state.selected_continuous_scale = selected_continuous_scale

    use_single_color = st.checkbox("Use single color for all tasks", value=st.session_state.use_single_color, key="use_single_color_checkbox")
    st.session_state.use_single_color = use_single_color

    st.subheader("Task Details")
    num_tasks = st.number_input(
        "How many main tasks do you have?",
        min_value=1,
        value=st.session_state.num_main_tasks,
        step=1,
        key="main_task_count_input",
    )
    st.session_state.num_main_tasks = num_tasks

    if len(st.session_state.task_names) < num_tasks:
        for _ in range(num_tasks - len(st.session_state.task_names)):
            st.session_state.task_names.append(
                f"Task {len(st.session_state.task_names)+1}"
            )
    elif len(st.session_state.task_names) > num_tasks:
        st.session_state.task_names = st.session_state.task_names[:num_tasks]

    current_tasks_input_data = []

    task_df = pd.DataFrame(st.session_state.tasks_data)
    if not task_df.empty and 'Task' in task_df.columns and not st.session_state.get("loaded_names_set"):
        st.session_state.task_names = list(task_df['Task'].drop_duplicates())
        st.session_state.loaded_names_set = True

    ordered_task_names = st.session_state.task_names

    for i in range(num_tasks):
        st.markdown("---")
        cols = st.columns(4)
        if cols[0].button("Move Up", key=f"move_up_{i}") and i > 0:
            st.session_state.task_names[i - 1], st.session_state.task_names[i] = (
                st.session_state.task_names[i],
                st.session_state.task_names[i - 1],
            )
            st.experimental_rerun()
        if cols[1].button("Move Down", key=f"move_down_{i}") and i < num_tasks - 1:
            st.session_state.task_names[i], st.session_state.task_names[i + 1] = (
                st.session_state.task_names[i + 1],
                st.session_state.task_names[i],
            )
            st.experimental_rerun()
        if cols[2].button("Add Above", key=f"add_above_{i}"):
            st.session_state.task_names.insert(i, f"Task {len(st.session_state.task_names)+1}")
            st.session_state.num_main_tasks += 1
            st.experimental_rerun()
        if cols[3].button("Add Below", key=f"add_below_{i}"):
            st.session_state.task_names.insert(i + 1, f"Task {len(st.session_state.task_names)+1}")
            st.session_state.num_main_tasks += 1
            st.experimental_rerun()

        task_name = st.text_input(
            f"Main Task {i+1} Name",
            value=st.session_state.task_names[i],
            key=f"main_task_name_{i}",
        )
        st.session_state.task_names[i] = task_name
        st.subheader(f"Task {i+1}")

        task_segments = [row for row in st.session_state.tasks_data if row.get("Task") == task_name]
        default_num_segments = max([row.get("Segment", 1) for row in task_segments], default=1)

        num_segments = st.number_input(
            f"How many segments for '{task_name}'?",
            min_value=1,
            value=default_num_segments,
            step=1,
            key=f"segments_count_{i}",
        )

        last_end = None
        for j in range(num_segments):
            st.markdown(f"**Segment {j+1} for '{task_name}'**")
            default_start_date = datetime.now().date()
            default_duration = 1.0

            if j < len(task_segments):
                seg = task_segments[j]
                start_val = seg["Start"]
                if isinstance(start_val, str):
                    start_val = pd.to_datetime(start_val)
                default_start_date = start_val.date()
                default_duration = float(seg["Duration_Months"])
                last_end = seg["End"]
            elif last_end is not None:
                if isinstance(last_end, str):
                    last_end = pd.to_datetime(last_end)
                default_start_date = pd.to_datetime(last_end).date()

            start_date_val = st.date_input(
                f"Start Date (Segment {j+1}) for '{task_name}'",
                value=default_start_date,
                key=f"start_date_{i}_{j}",
            )
            duration_months = st.number_input(
                f"Duration (Segment {j+1}) in months",
                min_value=0.1,
                value=default_duration,
                step=0.1,
                key=f"duration_{i}_{j}",
            )

            start_datetime_obj = datetime.combine(start_date_val, datetime.min.time())
            end_datetime_obj = start_datetime_obj + timedelta(days=duration_months * 30.44)
            last_end = end_datetime_obj

            current_tasks_input_data.append({
                'Task': task_name,
                'Segment': j + 1,
                'Start': start_datetime_obj,
                'End': end_datetime_obj,
                'Duration_Months': duration_months
            })

    st.session_state.tasks_data = current_tasks_input_data

    if st.button("Generate Gantt Chart"):
        if not st.session_state.tasks_data:
            st.warning("Please add at least one task segment.")
            return

        df = pd.DataFrame(st.session_state.tasks_data).sort_values(by=['Start', 'Task', 'Segment'])

        if use_single_color:
            fig = px.timeline(df, x_start="Start", x_end="End", y="Task", title=plot_title)
            fig.update_traces(marker_color=selected_discrete_color_code)
        else:
            fig = px.timeline(df, x_start="Start", x_end="End", y="Task", color="Duration_Months", color_continuous_scale=selected_continuous_scale, title=plot_title)

        fig.update_yaxes(autorange="reversed")
        fig.update_layout(xaxis_title="Timeline", yaxis_title="Task")


        if selected_theme == "White Background":
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='black'),
                title_font=dict(color='black'),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='lightgrey',
                tickfont=dict(color='black'),
                    title_font=dict(color='black')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='lightgrey',
                    tickfont=dict(color='black'),
                    title_font=dict(color='black')
                ),
                legend=dict(font=dict(color='black'))
            )
            
        else:
            fig.update_layout(plot_bgcolor='#222', paper_bgcolor='#111', font_color='white')

        st.plotly_chart(fig, use_container_width=True)

        csv_data = df.to_csv(index=False, date_format='%Y-%m-%dT%H:%M:%S').encode('utf-8')
        download_button_placeholder.download_button(
            label="Download Project Data (CSV)",
            data=csv_data,
            file_name=f"{plot_title.replace(' ', '_')}_gantt_project.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    create_gantt_chart_app()
