# 🧹 Google Search Console Data Cleaner

A powerful Streamlit application designed to automatically clean and standardize Google Search Console organic performance reports. This tool helps you remove problematic data and ensure your GSC exports are ready for analysis.

## ✨ Features

- **Multi-format Support**: Works with CSV, XLSX, and XLS files
- **Intelligent Column Detection**: Automatically identifies Query, Page, Clicks, Impressions, and Position columns
- **Comprehensive Data Cleaning**: Removes non-English text, invalid URLs, special characters, and non-numeric values
- **Detailed Statistics**: Provides cleaning reports showing what was removed and retention rates
- **Easy Export**: Download cleaned data as CSV with one click

## 🚀 Quick Start

### Installation

1. Clone or download the application file
2. Install required dependencies:
```bash
pip install streamlit pandas numpy openpyxl
```

### Running the Application

```bash
streamlit run gsc_data_cleaner.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📊 How It Works

### Supported Column Names

The application automatically detects columns with these naming variations:

| Column Type | Supported Names |
|-------------|-----------------|
| **Query** | Query, Queries, query, Keyword, Keywords |
| **Page** | Page, page, Landing Page, Address |
| **Position** | Position, position, avg pos, avg position, Avg Position, Avg. Pos, Avg. Position |
| **Numeric** | Clicks, Impressions, click, impression |

### Cleaning Rules

#### Query Column 🔍
- **Non-English Removal**: Filters out queries containing primarily non-Latin characters
- **URL Removal**: Removes any strings starting with `http:` or `https:`
- **Special Character Cleaning**: Removes all special characters except spaces and alphanumeric characters
- **Whitespace Normalization**: Standardizes multiple spaces to single spaces

#### Page Column 📄
- **HTTPS Filtering**: Keeps only URLs that start with `https:`
- **Invalid URL Removal**: Removes non-URL entries and non-secure URLs

#### Numeric Columns 🔢
- **Type Conversion**: Converts values to numeric format
- **Invalid Value Removal**: Removes any non-numeric entries
- **NaN Handling**: Automatically removes null and invalid numeric values

## 💡 Usage Instructions

1. **Upload Your File**: 
   - Click "Choose a file" and select your GSC export
   - Supports CSV, XLSX, and XLS formats

2. **Review Column Detection**:
   - Check that columns are correctly identified
   - Green checkmarks indicate successful detection

3. **Clean Your Data**:
   - Click the "🧹 Clean Data" button
   - Review the cleaning progress and statistics

4. **Download Results**:
   - Review the cleaned data preview
   - Click "Download Cleaned CSV" to save your results

## 📈 Understanding the Results

### Cleaning Statistics

The application provides detailed statistics for each column:

- **Original Rows**: Number of rows before cleaning
- **Rows Removed**: Number of rows that didn't meet criteria
- **Final Rows**: Number of valid rows remaining
- **Retention Rate**: Percentage of data retained after cleaning

### Overall Metrics

- **Original vs Cleaned Rows**: Total row count comparison
- **Retention Rate**: Overall data quality percentage

## 🔧 Technical Details

### Dependencies
- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing
- `openpyxl`: Excel file support

### File Processing
- **CSV Files**: Supports multiple encodings (UTF-8, Latin-1, CP1252)
- **Excel Files**: Compatible with both .xlsx and .xls formats
- **Memory Efficient**: Processes data in chunks for large files

### Data Validation
- **English Text Detection**: Uses character frequency analysis
- **URL Validation**: Pattern matching for protocol validation
- **Numeric Validation**: Pandas `to_numeric` with error coercing

## 🎯 Best Practices

### Data Preparation
1. **Export Settings**: Use Google Search Console's standard export format
2. **Column Names**: Ensure standard GSC column naming conventions
3. **Data Range**: Consider cleaning smaller date ranges for better performance

### Quality Assurance
1. **Review Statistics**: Always check retention rates before proceeding
2. **Sample Validation**: Verify a few cleaned rows manually
3. **Backup Original**: Keep a copy of your original export file

## 🐛 Troubleshooting

### Common Issues

**File Upload Errors**
- Ensure file is in supported format (CSV, XLSX, XLS)
- Check for file corruption or unusual characters
- Try saving Excel files as CSV if issues persist

**Column Detection Problems**
- Verify column names match supported variations
- Check for extra spaces or special characters in headers
- Ensure first row contains column headers

**Low Retention Rates**
- Review specific cleaning statistics to identify issues
- Consider if your data source has quality problems
- Check if column content matches expected format

**Performance Issues**
- Large files may take time to process
- Consider splitting very large datasets
- Ensure sufficient system memory

### Error Messages

| Error | Solution |
|-------|----------|
| "Unsupported file format" | Use CSV, XLSX, or XLS files only |
| "No relevant columns found" | Check column names match expected formats |
| "Error reading file" | Verify file isn't corrupted and try re-exporting |

## 📝 Example Data

The application works best with standard GSC exports that include:

```
Query,Page,Clicks,Impressions,Position
"python tutorial","https://example.com/python",150,1250,5.6
"data science","https://example.com/data-science",89,890,8.9
```

## 🔄 Updates and Versions

### Version 2.0
- Multi-format file support (CSV, XLSX, XLS)
- Enhanced UI with better error handling
- Improved regex patterns for better cleaning
- Better encoding support for international files

### Version 1.0
- Basic CSV support
- Core cleaning functionality
- Simple statistics reporting

## 📞 Support

For issues, suggestions, or contributions:
- Review this documentation first
- Check the troubleshooting section
- Ensure you're using supported file formats
- Verify your data follows GSC export standards

## 📄 License

This application is provided as-is for data cleaning purposes. Please ensure compliance with Google Search Console's terms of service when using exported data.

---

**🛠️ Built with Streamlit | 📊 GSC Data Cleaner v2.0**
