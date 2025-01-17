import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

# NOTE: We avoid using os.path.join; we just concatenate paths with "/"

from parameters import (
    PATH_TEMPLATES_DIRECTORY, 
    BEST_WORST, 
    REPORT_ALT_ROW_BG_COLOR,
    REPORT_FONT_FAMILY,
    REPORT_FONT_SIZE,
    REPORT_HEADER_BG_COLOR
)


class HTMLReportRenderer:
    def render_report_html(self,
                           assistant_name: str,
                           df_single_full: pd.DataFrame,      # ADDED
                           df_single_best: pd.DataFrame,
                           df_single_worst: pd.DataFrame,
                           df_worst_of_4_full: pd.DataFrame,  # ADDED
                           df_worst_each_question: pd.DataFrame
                           ) -> str:
        """
        - Use df_single_full and df_worst_of_4_full for computing the stats.
        - Show df_single_best, df_single_worst, df_worst_each_question in the tables.
        """
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
                }
                h1, h2 {
                    text-align: center;
                }
                table {
                    width: 100%;
                    border: 1px solid #ccc;
                    border-collapse: collapse;
                    margin: 20px 0;
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
            </style>
        </head>
        <body>
            <h1>Report for {{ assistant_name }}</h1>

            <!-- 1) STATISTICAL SUMMARY for Single-Assessment (using the ENTIRE dataset) -->
            {% if single_summary_columns %}
            <h2>Statistical Summary: Single Assessment (All Data)</h2>
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

            <!-- 2) STATISTICAL SUMMARY for Worst-of-4 (using the ENTIRE dataset) -->
            {% if worst_summary_columns %}
            <h2>Statistical Summary: Worst-of-4 (All Data)</h2>
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


            <!-- 3) TABLE: Single Assessment BEST (subset) -->
            <h2>Single Assessment: BEST (Top {{ BEST_WORST }})</h2>
            <table>
                <thead>
                    <tr>
                        {% for col in single_best_columns %}
                            <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in single_best_rows %}
                    <tr>
                        {% for col in single_best_columns %}
                            <td>{{ row[col] }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <!-- 4) TABLE: Single Assessment WORST (subset) -->
            <h2>Single Assessment: WORST (Bottom {{ BEST_WORST }})</h2>
            <table>
                <thead>
                    <tr>
                        {% for col in single_worst_columns %}
                            <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in single_worst_rows %}
                    <tr>
                        {% for col in single_worst_columns %}
                            <td>{{ row[col] }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <!-- 5) TABLE: Worst-of-4 (Max Difference subset) -->
            <h2>Worst-of-4 (Max Difference Subset)</h2>
            <table>
                <thead>
                    <tr>
                        {% for col in worst_each_q_columns %}
                            <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in worst_each_q_rows %}
                    <tr>
                        {% for col in worst_each_q_columns %}
                            <td>{{ row[col] }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

        </body>
        </html>
        """

        template = env.from_string(template_source)

        # Convert "best" subset to dict for Jinja2
        single_best_rows = df_single_best.to_dict(orient="records")
        single_best_columns = df_single_best.columns.tolist()

        # Convert "worst" subset to dict for Jinja2
        single_worst_rows = df_single_worst.to_dict(orient="records")
        single_worst_columns = df_single_worst.columns.tolist()

        # Convert "biggest difference" subset to dict for Jinja2
        worst_each_q_rows = df_worst_each_question.to_dict(orient="records")
        worst_each_q_columns = df_worst_each_question.columns.tolist()

        # 1) Compute stats on the FULL single-assessment DataFrame
        try:
            df_single_summary = df_single_full.describe()
        except ValueError:
            df_single_summary = pd.DataFrame()

        # 2) Compute stats on the FULL worst-of-4 DataFrame
        try:
            df_worst_summary = df_worst_of_4_full.describe()
        except ValueError:
            df_worst_summary = pd.DataFrame()

        # Transpose so that rows=stats, columns=features
        df_single_summary = df_single_summary.T.reset_index()
        df_worst_summary = df_worst_summary.T.reset_index()

        single_summary_rows = df_single_summary.to_dict(orient='records')
        single_summary_columns = df_single_summary.columns.tolist()

        worst_summary_rows = df_worst_summary.to_dict(orient='records')
        worst_summary_columns = df_worst_summary.columns.tolist()

        # Render
        context_data = {
            "assistant_name": assistant_name,
            "font_family": REPORT_FONT_FAMILY,
            "font_size": REPORT_FONT_SIZE,
            "header_bg_color": REPORT_HEADER_BG_COLOR,
            "alt_row_bg_color": REPORT_ALT_ROW_BG_COLOR,

            # Full-data stats
            "single_summary_rows": single_summary_rows,
            "single_summary_columns": single_summary_columns,
            "worst_summary_rows": worst_summary_rows,
            "worst_summary_columns": worst_summary_columns,

            # Subset for display
            "single_best_rows": single_best_rows,
            "single_best_columns": single_best_columns,
            "single_worst_rows": single_worst_rows,
            "single_worst_columns": single_worst_columns,
            "worst_each_q_rows": worst_each_q_rows,
            "worst_each_q_columns": worst_each_q_columns,

            "BEST_WORST": BEST_WORST
        }

        return template.render(**context_data)