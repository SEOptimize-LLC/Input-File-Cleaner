
import streamlit as st
import pandas as pd
import re
import numpy as np
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="GSC Data Cleaner",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🧹 Google Search Console Data Cleaner")
st.markdown("Upload your Google Search Console organic performance report to automatically clean and standardize the data.")

# Sidebar with instructions
st.sidebar.header("📋 Cleaning Rules")
st.sidebar.markdown("""
**Query Column Cleaning:**
- Remove non-English characters, words, or phrases
- Remove URLs (strings starting with http: or https:)
- Remove special characters (except spaces)

**Page Column Cleaning:**
- Keep only URLs starting with https:

**Numeric Column Cleaning:**
- Keep only numeric values in Clicks, Impressions, Position columns
""")

st.sidebar.header("📁 Supported Column Names")
st.sidebar.markdown("""
**Query Column:** Query, Queries, query, Keyword, Keywords

**Page Column:** Page, page, Landing Page, Address

**Position Column:** Position, position, avg pos, avg position, Avg Position, Avg. Pos, Avg. Position
""")

def detect_english_text(text):
    """Check if text contains primarily English characters"""
    if pd.isna(text) or text == "":
        return False

    # Convert to string
    text = str(text)

    # Check if text contains mostly Latin characters
    latin_chars = re.findall(r'[a-zA-Z\s]', text)
    total_chars = len(text.replace(' ', ''))

    if total_chars == 0:
        return False

    latin_ratio = len(''.join(latin_chars).replace(' ', '')) / total_chars
    return latin_ratio > 0.7  # At least 70% Latin characters

def is_url(text):
    """Check if text is a URL"""
    if pd.isna(text):
        return False
    text = str(text).strip()
    return text.startswith(('http:', 'https:'))

def clean_query_column(series):
    """Clean the query column according to specifications"""
    cleaned_series = series.copy()

    # Track cleaning statistics
    stats = {
        'original_count': len(cleaned_series),
        'non_english_removed': 0,
        'urls_removed': 0,
        'special_chars_cleaned': 0,
        'final_count': 0
    }

    # Remove non-English entries
    english_mask = cleaned_series.apply(detect_english_text)
    stats['non_english_removed'] = (~english_mask).sum()
    cleaned_series = cleaned_series[english_mask]

    # Remove URLs
    if len(cleaned_series) > 0:
        url_mask = cleaned_series.apply(lambda x: not is_url(x))
        stats['urls_removed'] = (~url_mask).sum()
        cleaned_series = cleaned_series[url_mask]

    # Clean special characters (keep only letters, numbers, and spaces)
    if len(cleaned_series) > 0:
        original_length = len(cleaned_series)
        cleaned_series = cleaned_series.apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x)) if pd.notna(x) else x)
        cleaned_series = cleaned_series.apply(lambda x: re.sub(r'\s+', ' ', str(x).strip()) if pd.notna(x) else x)
        # Remove empty strings after cleaning
        cleaned_series = cleaned_series[cleaned_series.str.len() > 0]
        stats['special_chars_cleaned'] = original_length - len(cleaned_series)

    stats['final_count'] = len(cleaned_series)

    return cleaned_series, stats

def clean_page_column(series):
    """Clean the page column - keep only URLs starting with https:"""
    cleaned_series = series.copy()

    stats = {
        'original_count': len(cleaned_series),
        'non_https_removed': 0,
        'final_count': 0
    }

    # Keep only URLs starting with https:
    https_mask = cleaned_series.apply(lambda x: str(x).strip().startswith('https:') if pd.notna(x) else False)
    stats['non_https_removed'] = (~https_mask).sum()
    cleaned_series = cleaned_series[https_mask]
    stats['final_count'] = len(cleaned_series)

    return cleaned_series, stats

def clean_numeric_column(series):
    """Clean numeric columns - keep only valid numbers"""
    cleaned_series = series.copy()

    stats = {
        'original_count': len(cleaned_series),
        'non_numeric_removed': 0,
        'final_count': 0
    }

    # Convert to numeric, coercing errors to NaN
    numeric_series = pd.to_numeric(cleaned_series, errors='coerce')

    # Remove NaN values
    non_null_mask = numeric_series.notna()
    stats['non_numeric_removed'] = (~non_null_mask).sum()
    cleaned_series = numeric_series[non_null_mask]
    stats['final_count'] = len(cleaned_series)

    return cleaned_series, stats

def identify_columns(df):
    """Identify the relevant columns in the dataframe"""
    columns = df.columns.str.lower()

    # Query column variations
    query_variations = ['query', 'queries', 'keyword', 'keywords']
    query_col = None
    for col in query_variations:
        matches = [c for c in df.columns if c.lower() == col]
        if matches:
            query_col = matches[0]
            break

    # Page column variations  
    page_variations = ['page', 'landing page', 'address']
    page_col = None
    for col in page_variations:
        matches = [c for c in df.columns if c.lower() == col]
        if matches:
            page_col = matches[0]
            break

    # Position column variations
    position_variations = ['position', 'avg pos', 'avg position', 'avg. pos', 'avg. position']
    position_col = None
    for col in position_variations:
        matches = [c for c in df.columns if c.lower() == col]
        if matches:
            position_col = matches[0]
            break

    # Numeric columns (clicks, impressions)
    numeric_variations = ['clicks', 'impressions', 'click', 'impression']
    numeric_cols = []
    for col in numeric_variations:
        matches = [c for c in df.columns if c.lower() == col]
        numeric_cols.extend(matches)

    return query_col, page_col, position_col, numeric_cols

def process_dataframe(df):
    """Process the entire dataframe"""
    # Identify columns
    query_col, page_col, position_col, numeric_cols = identify_columns(df)

    cleaning_stats = {}
    cleaned_df = df.copy()

    # Store original indices to track what gets removed
    original_indices = df.index.tolist()
    valid_indices = set(original_indices)

    # Clean query column
    if query_col:
        st.write(f"🔍 Cleaning Query column: **{query_col}**")
        cleaned_queries, query_stats = clean_query_column(df[query_col])
        cleaning_stats[query_col] = query_stats
        valid_indices = valid_indices.intersection(set(cleaned_queries.index))

    # Clean page column
    if page_col:
        st.write(f"📄 Cleaning Page column: **{page_col}**")
        cleaned_pages, page_stats = clean_page_column(df[page_col])
        cleaning_stats[page_col] = page_stats
        valid_indices = valid_indices.intersection(set(cleaned_pages.index))

    # Clean position column
    if position_col:
        st.write(f"📊 Cleaning Position column: **{position_col}**")
        cleaned_position, position_stats = clean_numeric_column(df[position_col])
        cleaning_stats[position_col] = position_stats
        valid_indices = valid_indices.intersection(set(cleaned_position.index))

    # Clean numeric columns
    for col in numeric_cols:
        if col in df.columns:
            st.write(f"🔢 Cleaning Numeric column: **{col}**")
            cleaned_numeric, numeric_stats = clean_numeric_column(df[col])
            cleaning_stats[col] = numeric_stats
            valid_indices = valid_indices.intersection(set(cleaned_numeric.index))

    # Filter the dataframe to keep only rows with valid indices
    final_indices = list(valid_indices)
    cleaned_df = df.loc[final_indices].copy()

    # Apply the actual cleaning to the remaining rows
    if query_col and query_col in cleaned_df.columns:
        cleaned_df[query_col] = cleaned_df[query_col].apply(
            lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x)) if pd.notna(x) else x
        )
        cleaned_df[query_col] = cleaned_df[query_col].apply(
            lambda x: re.sub(r'\s+', ' ', str(x).strip()) if pd.notna(x) else x
        )

    if position_col and position_col in cleaned_df.columns:
        cleaned_df[position_col] = pd.to_numeric(cleaned_df[position_col], errors='coerce')

    for col in numeric_cols:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')

    return cleaned_df, cleaning_stats

def create_download_link(df, filename="cleaned_gsc_data.csv"):
    """Create a download link for the cleaned dataframe"""
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    b64 = base64.b64encode(csv_buffer.read()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="display: inline-block; padding: 10px 20px; background-color: #0066cc; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">📥 Download Cleaned CSV</a>'
    return href

def load_file(uploaded_file):
    """Load file based on its extension"""
    file_extension = uploaded_file.name.lower().split('.')[-1]

    try:
        if file_extension == 'csv':
            # Try different encodings for CSV files
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                except UnicodeDecodeError:
                    df = pd.read_csv(uploaded_file, encoding='cp1252')
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return None

        return df
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

# File uploader with multiple format support
uploaded_file = st.file_uploader(
    "Choose a file",
    type=['csv', 'xlsx', 'xls'],
    help="Upload your Google Search Console organic performance report in CSV, XLSX, or XLS format"
)

if uploaded_file is not None:
    try:
        # Load the dataframe
        df = load_file(uploaded_file)

        if df is not None:
            st.success(f"✅ File uploaded successfully! Shape: {df.shape}")

            # Display original data preview
            st.subheader("📊 Original Data Preview")
            st.dataframe(df.head(10), use_container_width=True)

            # Show column information
            st.subheader("📋 Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes,
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum()
            })
            st.dataframe(col_info, use_container_width=True)

            # Identify columns
            query_col, page_col, position_col, numeric_cols = identify_columns(df)

            st.subheader("🎯 Identified Columns")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Query Column:**")
                if query_col:
                    st.success(f"✅ {query_col}")
                else:
                    st.error("❌ Not found")

            with col2:
                st.write("**Page Column:**")
                if page_col:
                    st.success(f"✅ {page_col}")
                else:
                    st.error("❌ Not found")

            with col3:
                st.write("**Position Column:**")
                if position_col:
                    st.success(f"✅ {position_col}")
                else:
                    st.error("❌ Not found")

            if numeric_cols:
                st.write("**Numeric Columns:**")
                for col in numeric_cols:
                    st.success(f"✅ {col}")
            else:
                st.write("**Numeric Columns:**")
                st.error("❌ Not found")

            # Process button
            if st.button("🧹 Clean Data", type="primary"):
                if not any([query_col, page_col, position_col, numeric_cols]):
                    st.warning("⚠️ No relevant columns found. Please check your file format and column names.")
                else:
                    with st.spinner("Cleaning data..."):
                        cleaned_df, cleaning_stats = process_dataframe(df)

                        st.success("✨ Data cleaning completed!")

                        # Display cleaning statistics
                        st.subheader("📈 Cleaning Statistics")

                        stats_data = []
                        for col, stats in cleaning_stats.items():
                            stats_data.append({
                                'Column': col,
                                'Original Rows': stats['original_count'],
                                'Rows Removed': stats['original_count'] - stats['final_count'],
                                'Final Rows': stats['final_count'],
                                'Retention Rate': f"{(stats['final_count'] / stats['original_count'] * 100):.1f}%"
                            })

                        if stats_data:
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(stats_df, use_container_width=True)

                        # Overall statistics
                        st.subheader("🎯 Overall Results")
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Original Rows", f"{len(df):,}")

                        with col2:
                            st.metric("Cleaned Rows", f"{len(cleaned_df):,}")

                        with col3:
                            rows_removed = len(df) - len(cleaned_df)
                            st.metric("Rows Removed", f"{rows_removed:,}")

                        with col4:
                            retention_rate = (len(cleaned_df) / len(df)) * 100
                            st.metric("Retention Rate", f"{retention_rate:.1f}%")

                        # Display cleaned data
                        st.subheader("✨ Cleaned Data Preview")
                        st.dataframe(cleaned_df.head(20), use_container_width=True)

                        # Download link
                        st.subheader("💾 Download Cleaned Data")
                        download_link = create_download_link(cleaned_df, "cleaned_gsc_data.csv")
                        st.markdown(download_link, unsafe_allow_html=True)

                        # Store cleaned data in session state for further use
                        st.session_state.cleaned_df = cleaned_df

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please make sure you've uploaded a valid file with the correct format.")

# Additional information
st.markdown("---")
st.subheader("ℹ️ Additional Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What this tool does:**
    - ✅ Removes non-English queries and special characters
    - ✅ Filters pages to keep only HTTPS URLs
    - ✅ Validates numeric data in clicks, impressions, and position columns
    - ✅ Provides detailed cleaning statistics
    - ✅ Supports CSV, XLSX, and XLS file formats
    """)

with col2:
    st.markdown("""
    **Tips for best results:**
    - 📤 Export your GSC data in CSV, XLSX, or XLS format
    - 📝 Ensure your file has standard column names
    - 📊 Include necessary columns (Query, Page, Clicks, Impressions, Position)
    - 📈 Review cleaning statistics to understand what was removed
    - 🔍 Preview your data before and after cleaning
    """)

# Examples section
with st.expander("📋 Example of Expected Column Names"):
    st.markdown("""
    **Query Column Examples:**
    - Query, Queries, query, Keyword, Keywords

    **Page Column Examples:**
    - Page, page, Landing Page, Address

    **Position Column Examples:**
    - Position, position, avg pos, avg position, Avg Position, Avg. Pos, Avg. Position

    **Numeric Column Examples:**
    - Clicks, Impressions, click, impression
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        🛠️ Built with Streamlit | 📊 GSC Data Cleaner v2.0<br>
        <small>Supports CSV, XLSX, and XLS file formats</small>
    </div>
    """, 
    unsafe_allow_html=True
)
