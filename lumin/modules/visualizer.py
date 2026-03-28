import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from modules.nl_query import ask_groq

def determine_chart_type(df: pd.DataFrame):
    if not isinstance(df, pd.DataFrame):
        if isinstance(df, pd.Series):
            df = df.reset_index()
        else:
            return "Metric"

    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(exclude='number').columns.tolist()

    # Single row with multiple numeric cols → grouped bar
    if len(df) == 1 and len(num_cols) >= 2:
        return "MultiBar"

    # Few rows with multiple numeric cols + one categorical → grouped bar
    if len(df) <= 20 and len(num_cols) >= 2 and len(cat_cols) >= 1:
        return "GroupedBar"

    date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower() or 'month' in c.lower() or 'year' in c.lower()]
    if date_cols:
        return "Line"

    if len(cat_cols) == 1 and len(num_cols) == 1:
        # Only use Pie for very small category counts (≤4), Bar is clearer otherwise
        if df[cat_cols[0]].nunique() <= 4:
            return "Pie"
        return "Bar"

    if len(num_cols) >= 2 and len(cat_cols) == 0:
        return "Scatter"

    if len(num_cols) == 1 and len(cat_cols) >= 1:
        return "Bar"

    if len(num_cols) == 1 and len(cat_cols) == 0:
        return "Histogram"

    return "Table"


def generate_chart_titles(df, question):
    prompt = f"Given data with columns {df.columns.tolist()} answering the question '{question}', suggest a Title, X-axis label, and Y-axis label. Format exactly as: Title|X_Label|Y_Label."
    try:
        response = ask_groq(prompt, system="You are a data visualization assistant. Reply only in the format: Title|X_Label|Y_Label")
        parts = response.split('|')
        if len(parts) >= 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        pass
    return "Data Chart", "Category", "Value"


def render_chart(result, question: str, override_type: str = None):
    # Guard against matplotlib Axes/Figure objects leaking through
    result_type = type(result).__name__
    if result_type in ("Axes", "AxesSubplot", "Figure"):
        st.warning("Chart rendering skipped: result was a matplotlib object. Please rephrase your question to return data.")
        return

    # Handle scalar values
    if result is None:
        st.warning("No result to display.")
        return

    if not isinstance(result, (pd.DataFrame, pd.Series)):
        st.metric(label="Result", value=str(result))
        return

    if isinstance(result, pd.Series):
        result = result.reset_index()
        result.columns = [str(c) for c in result.columns]

    df = result.copy()
    df.columns = [str(c) for c in df.columns]

    suggested_type = determine_chart_type(df)

    # Honour explicit chart type keywords in the question
    q_lower = question.lower()
    if override_type and override_type != "Auto":
        chart_type = override_type
    elif "bar chart" in q_lower or "bar graph" in q_lower:
        chart_type = "Bar"
    elif "line chart" in q_lower or "line graph" in q_lower or "trend" in q_lower:
        chart_type = "Line"
    elif "pie chart" in q_lower or "pie graph" in q_lower:
        chart_type = "Pie"
    elif "scatter" in q_lower:
        chart_type = "Scatter"
    elif "histogram" in q_lower or "distribution" in q_lower:
        chart_type = "Histogram"
    else:
        chart_type = suggested_type

    if chart_type in ["Table", "Metric"]:
        st.dataframe(df, use_container_width=True)
        return

    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(exclude='number').columns.tolist()

    title, x_label, y_label = generate_chart_titles(df, question)

    fig = None

    try:
        # Single row, multiple numeric columns → melt into bar chart
        if chart_type == "MultiBar":
            melted = df[num_cols].T.reset_index()
            melted.columns = ["Metric", "Value"]
            fig = px.bar(melted, x="Metric", y="Value", title=title,
                         text_auto=True, color="Metric")
            fig.update_traces(textposition='outside')

        elif chart_type == "GroupedBar" and len(cat_cols) >= 1 and len(num_cols) >= 1:
            melted = df.melt(id_vars=cat_cols[0], value_vars=num_cols, var_name="Metric", value_name="Value")
            fig = px.bar(melted, x=cat_cols[0], y="Value", color="Metric",
                         barmode="group", title=title, text_auto=True)
            fig.update_traces(textposition='outside')

        elif chart_type == "Bar" and len(cat_cols) >= 1 and len(num_cols) >= 1:
            fig = px.bar(df, x=cat_cols[0], y=num_cols[0], title=title,
                         labels={cat_cols[0]: x_label, num_cols[0]: y_label},
                         text_auto=True, color=cat_cols[0])
            fig.update_traces(textposition='outside')

        elif chart_type == "Line":
            date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower() or 'month' in c.lower() or 'year' in c.lower()]
            x_col = date_cols[0] if date_cols else df.columns[0]
            y_cols = num_cols if num_cols else [df.columns[1]]
            fig = px.line(df, x=x_col, y=y_cols, title=title, markers=True)

        elif chart_type == "Pie" and len(cat_cols) >= 1 and len(num_cols) >= 1:
            fig = px.pie(df, names=cat_cols[0], values=num_cols[0], title=title,
                         hole=0.3)

        elif chart_type == "Scatter" and len(num_cols) >= 2:
            color_col = cat_cols[0] if cat_cols else None
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1], title=title,
                             color=color_col,
                             labels={num_cols[0]: x_label, num_cols[1]: y_label})

        elif chart_type == "Histogram" and len(num_cols) >= 1:
            fig = px.histogram(df, x=num_cols[0], title=title,
                               labels={num_cols[0]: x_label})

        else:
            st.dataframe(df, use_container_width=True)
            return

        if fig:
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                legend=dict(bgcolor='rgba(0,0,0,0)'),
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Could not render chart: {e}")
        st.dataframe(df, use_container_width=True)