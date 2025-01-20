# html_report_renderer.py
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from parameters import (
    PATH_TEMPLATES_DIRECTORY,
    REPORT_ALT_ROW_BG_COLOR,
    REPORT_FONT_FAMILY,
    REPORT_FONT_SIZE,
    REPORT_HEADER_BG_COLOR
)

class HTMLReportRenderer:
    def render_report_html(
        self,
        assistant_name: str,
        df_single_full: pd.DataFrame,
        df_worst_of_4_per_question: pd.DataFrame,
        percentage_worst_of_4_above_threshold: float,
        threshold: float,
        df_worst_of_4_below_threshold_no_repeat: pd.DataFrame
    ) -> str:

        env = Environment(
            loader=FileSystemLoader(PATH_TEMPLATES_DIRECTORY),
            autoescape=select_autoescape(["html", "xml"])
        )

        template_source = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Report for {{ assistant_name }}</title>
    <style>
        :root {
            --font-family: {{ font_family }};
            --font-size: {{ font_size }};
            --header-bg-color: {{ header_bg_color }};
            --alt-row-bg-color: {{ alt_row_bg_color }};
        }
        body {
            font-family: var(--font-family);
            font-size: var(--font-size);
            margin: 20px;
            color: #333;
            background-color: #fafafa;
        }
        h1, h2 {
            text-align: center;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border: 1px solid #ccc;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: #fff;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: var(--header-bg-color);
        }
        tr:nth-child(odd) {
            background-color: var(--alt-row-bg-color);
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .stats-table {
            margin-top: 30px;
        }
        .stats-table th {
            background-color: #e0e0e0;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Report for {{ assistant_name }}</h1>

    <!-- 1) Single-Assessment Summary -->
    {% if single_summary_columns %}
    <h2>Single Assessment Summary</h2>
    <table class="stats-table">
        <thead>
            <tr>
            {% for col in single_summary_columns %}
                <th>{{ col }}</th>
            {% endfor %}
            </tr>
        </thead>
        <tbody>
        {% for row in single_summary_rows %}
            <tr>
            {% for col in single_summary_columns %}
                <td>{{ row[col] }}</td>
            {% endfor %}
            </tr>
        {% endfor %}
        </tbody>
    </table>
    {% endif %}

    <!-- 2) Worst-of-4 Summary (Single Worst per Question) -->
    {% if worst_summary_columns %}
    <h2>Worst-of-4 Summary (Single Worst per Question)</h2>
    <table class="stats-table">
        <thead>
            <tr>
            {% for col in worst_summary_columns %}
                <th>{{ col }}</th>
            {% endfor %}
            </tr>
        </thead>
        <tbody>
        {% for row in worst_summary_rows %}
            <tr>
            {% for col in worst_summary_columns %}
                <td>{{ row[col] }}</td>
            {% endfor %}
            </tr>
        {% endfor %}
        </tbody>
    </table>
    {% endif %}

    <!-- 3) Threshold & Percentage ABOVE Threshold -->
    <h2>Threshold & Percentage Above Threshold</h2>
    <p><strong>Threshold:</strong> {{ threshold }}</p>
    <p><strong>Percentage of Worst-of-4 (single worst per question) above threshold:</strong> {{ percentage_worst_of_4_above_threshold }}%</p>

    <!-- 4) Worst-of-4 Below Threshold (no repeated questions) -->
    {% if worst_of_4_below_threshold_columns %}
    <h2>Worst-of-4 Below Threshold (No Repeats)</h2>
    <table>
        <thead>
            <tr>
            {% for col in worst_of_4_below_threshold_columns %}
                <th>{{ col }}</th>
            {% endfor %}
            </tr>
        </thead>
        <tbody>
        {% for row in worst_of_4_below_threshold_rows %}
            <tr>
            {% for col in worst_of_4_below_threshold_columns %}
                <td>{{ row[col] }}</td>
            {% endfor %}
            </tr>
        {% endfor %}
        </tbody>
    </table>
    {% endif %}

</body>
</html>
        """

        template = env.from_string(template_source)

        # 1) Single-assessment summary
        try:
            df_single_summary = df_single_full.describe()
        except ValueError:
            df_single_summary = pd.DataFrame()  # fallback if empty

        df_single_summary = df_single_summary.T.reset_index()
        single_summary_rows = df_single_summary.to_dict(orient="records")
        single_summary_columns = df_single_summary.columns.tolist()

        # 2) Worst-of-4 summary (single worst per question)
        try:
            df_worst_summary = df_worst_of_4_per_question.describe()
        except ValueError:
            df_worst_summary = pd.DataFrame()

        df_worst_summary = df_worst_summary.T.reset_index()
        worst_summary_rows = df_worst_summary.to_dict(orient="records")
        worst_summary_columns = df_worst_summary.columns.tolist()

        # 3) Final table: single worst below threshold
        worst_of_4_below_threshold_rows = df_worst_of_4_below_threshold_no_repeat.to_dict(orient="records")
        worst_of_4_below_threshold_columns = df_worst_of_4_below_threshold_no_repeat.columns.tolist()

        # Prepare data for Jinja
        context_data = {
            "assistant_name": assistant_name,
            "font_family": REPORT_FONT_FAMILY,
            "font_size": REPORT_FONT_SIZE,
            "header_bg_color": REPORT_HEADER_BG_COLOR,
            "alt_row_bg_color": REPORT_ALT_ROW_BG_COLOR,

            # Single-assessment summary data
            "single_summary_rows": single_summary_rows,
            "single_summary_columns": single_summary_columns,

            # Worst-of-4 summary (single worst per question)
            "worst_summary_rows": worst_summary_rows,
            "worst_summary_columns": worst_summary_columns,

            # Threshold & Percentage ABOVE threshold
            "threshold": threshold,
            "percentage_worst_of_4_above_threshold": f"{percentage_worst_of_4_above_threshold:.2f}",

            # Final table: worst-of-4 below threshold (no repeats)
            "worst_of_4_below_threshold_rows": worst_of_4_below_threshold_rows,
            "worst_of_4_below_threshold_columns": worst_of_4_below_threshold_columns,
        }

        return template.render(**context_data)
