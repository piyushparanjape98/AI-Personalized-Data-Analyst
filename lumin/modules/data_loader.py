import pandas as pd
import streamlit as st


def load_file(uploaded_file) -> pd.DataFrame | None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def find_common_columns(dfs: dict[str, pd.DataFrame]) -> list[tuple[str, str, str]]:
    """Returns list of (file1, file2, common_col) tuples for potential join keys."""
    names = list(dfs.keys())
    suggestions = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            common = set(dfs[a].columns) & set(dfs[b].columns)
            for col in common:
                suggestions.append((a, b, col))
    return suggestions


def merge_dataframes(dfs: dict[str, pd.DataFrame], left: str, right: str, on: str, how: str = "inner") -> pd.DataFrame:
    """Merge two dataframes by name."""
    return pd.merge(dfs[left], dfs[right], on=on, how=how)


def display_data_preview(df: pd.DataFrame):
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Dataset Shape**")
        st.write(f"Rows: {df.shape[0]}")
        st.write(f"Columns: {df.shape[1]}")

    with col2:
        st.write("**Columns & Types**")
        types_df = pd.DataFrame(df.dtypes, columns=['Data Type'])
        st.dataframe(types_df, use_container_width=True)

    with col3:
        st.write("**Missing Values**")
        missing_df = pd.DataFrame(df.isnull().sum(), columns=['Null Count'])
        st.dataframe(missing_df, use_container_width=True)

    st.write("**Descriptive Statistics (Numeric)**")
    if not df.select_dtypes(include=['number']).empty:
        st.dataframe(df.describe(), use_container_width=True)
    else:
        st.write("No numeric columns available.")


def get_schema(df: pd.DataFrame) -> str:
    schema = ""
    for col in df.columns:
        schema += f"- {col} ({df[col].dtype})\n"
    return schema


def get_sample(df: pd.DataFrame, n: int = 5) -> str:
    return df.head(n).to_markdown(index=False)