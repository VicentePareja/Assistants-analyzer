# -*- coding: utf-8 -*-
"""
analyze_bot_data.py

This version focuses on creating an HTML file with:
1) A table with all the rows from the single-assessment CSV (_grades_single_assessment).
2) A table with the "worst" answer for each question from the worst-of-4 CSV (_grades_worst_of_4).
3) A statistical summary for each of the above.
"""

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

# NOTE: We avoid using os.path.join; we just concatenate paths with "/"
# as requested by the instructions.

from parameters import (
    PATH_STATIC_GRADES_DIRECTORY,
    PATH_PROCESSED_RESULTS_DIRECTORY,
    PATH_REPORTS_DIRECTORY,
    PATH_TEMPLATES_DIRECTORY, 
    BEST_WORST, 
    MOST_DIFFERENT
)


class PathsManager:
    """
    Handles updating and creating necessary paths/directories based on the assistant name.
    """
    def __init__(self):
        self.assistant_name = None
        self.worst_of_4_file = None
        self.single_assessment_file = None
        self.processed_dir = None
        self.report_dir = None

    def update_paths(self, assistant_name: str):
        """
        Prepare file paths and directories based on the assistant name.
        We won't use os.makedirs or os.path.exists; 
        but in your environment, you may want to ensure the folders exist.
        """
        self.assistant_name = assistant_name
        self.worst_of_4_file = PATH_STATIC_GRADES_DIRECTORY + f"/{assistant_name}_grades_worst_of_4.csv"
        self.single_assessment_file = PATH_STATIC_GRADES_DIRECTORY + f"/{assistant_name}_grades_single_assessment.csv"
        self.processed_dir = PATH_PROCESSED_RESULTS_DIRECTORY
        self.report_dir = PATH_REPORTS_DIRECTORY


class BotDataLoader:
    """
    Loads the worst-of-4 and single-assessment CSVs.
    """
    def load_data(self, paths_manager: PathsManager):
        df_worst_of_4 = pd.DataFrame()
        df_single = pd.DataFrame()

        try:
            df_worst_of_4 = pd.read_csv(paths_manager.worst_of_4_file, sep=';')
        except Exception as e:
            print(f"Warning: Could not load worst_of_4 file {paths_manager.worst_of_4_file}. Error: {e}")

        try:
            df_single = pd.read_csv(paths_manager.single_assessment_file, sep=';')
        except Exception as e:
            print(f"Warning: Could not load single_assessment file {paths_manager.single_assessment_file}. Error: {e}")

        return df_worst_of_4, df_single


class BotDataProcessor:
    """
    Processes data frames. We will create a new method to find the top
    MOST_DIFFERENT questions, each with best & worst attempts.
    """

    def get_worst_answer_per_question(self, df_worst: pd.DataFrame):
        # (Keep or remove this old method as needed)
        if df_worst.empty or "Grading" not in df_worst.columns:
            return pd.DataFrame()

        worst_df = df_worst.loc[df_worst.groupby("Question")["Grading"].idxmin()].copy()
        return worst_df

    def get_best_and_worst_with_biggest_difference(self, df_worst: pd.DataFrame, top_n: int):
        """
        For each question, find the best (max) and worst (min) rows by 'Grading'.
        Compute the difference (max - min). Keep only the top 'top_n' questions 
        with the largest difference. Return a DataFrame with 2*top_n rows 
        (the best and worst for each question).
        """
        if df_worst.empty or "Grading" not in df_worst.columns:
            return pd.DataFrame()

        # Group by question
        grouped = df_worst.groupby("Question")

        # For each group, find:
        #   * best_row (max Grading)
        #   * worst_row (min Grading)
        #   * difference = best_row.Grading - worst_row.Grading
        results = []
        for question, group_df in grouped:
            # If the group is empty or missing columns, skip
            if group_df.empty:
                continue

            max_idx = group_df["Grading"].idxmax()
            min_idx = group_df["Grading"].idxmin()

            best_row = group_df.loc[max_idx]
            worst_row = group_df.loc[min_idx]
            difference = best_row["Grading"] - worst_row["Grading"]

            results.append({
                "Question": question,
                "BestRow": best_row,
                "WorstRow": worst_row,
                "Difference": difference
            })

        # Sort by difference descending, keep top N
        sorted_results = sorted(results, key=lambda x: x["Difference"], reverse=True)
        top_results = sorted_results[:top_n]

        # Build a final DataFrame with both best & worst rows
        # We'll keep the original columns, plus a "Type" column 
        # so you know if it's "BEST" or "WORST" in the final table
        final_rows = []
        for item in top_results:
            best_row_data = item["BestRow"].to_dict()
            worst_row_data = item["WorstRow"].to_dict()

            # Tag them for clarity
            best_row_data["Type"] = "BEST"
            worst_row_data["Type"] = "WORST"

            # We might also store the difference if you want to see it in the HTML
            best_row_data["Difference"] = item["Difference"]
            worst_row_data["Difference"] = item["Difference"]

            final_rows.append(best_row_data)
            final_rows.append(worst_row_data)

        df_final = pd.DataFrame(final_rows)
        return df_final.reset_index(drop=True)

    def filter_single_assessment_top_and_bottom(self, df_single: pd.DataFrame, n: int, grading_col: str = "Grading"):
        # (This method stays the same if you still want top & bottom rows)
        if df_single.empty or grading_col not in df_single.columns:
            return df_single  
        df_single_sorted = df_single.sort_values(by=grading_col, ascending=False)
        top_n = df_single_sorted.head(n)
        bottom_n = df_single_sorted.tail(n)
        return pd.concat([top_n, bottom_n], axis=0).reset_index(drop=True)
    
    def get_top_n(self, df: pd.DataFrame, n: int, grading_col: str = "Grading") -> pd.DataFrame:
        """
        Return the top-n rows sorted by `grading_col` descending.
        """
        if df.empty or grading_col not in df.columns:
            return pd.DataFrame()  # Return an empty DataFrame if conditions are not met
        return df.sort_values(by=grading_col, ascending=False).head(n)

    def get_bottom_n(self, df: pd.DataFrame, n: int, grading_col: str = "Grading") -> pd.DataFrame:
        """
        Return the bottom-n rows sorted by `grading_col` ascending.
        """
        if df.empty or grading_col not in df.columns:
            return pd.DataFrame()  # Return an empty DataFrame if conditions are not met
        return df.sort_values(by=grading_col, ascending=False).tail(n)




class WorstOf4Saver:
    """
    Saves the entire worst-of-4 data (or any processed subset) to a CSV file (optional).
    """
    def save_worst_data(self, df_worst: pd.DataFrame, paths_manager: PathsManager, assistant_name: str):
        if df_worst.empty:
            print("No data to save for worst-of-4.")
            return
        output_file = paths_manager.processed_dir + f"/{assistant_name}_only_worst.csv"
        df_worst.to_csv(output_file, index=False, sep=';')
        print(f"Worst-of-4 data saved to: {output_file}")


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
                table, th, td {
                    border: 1px solid #ccc;
                    border-collapse: collapse;
                    padding: 5px;
                }
                th {
                    background-color: #f0f0f0;
                }
                .stats-table {
                    margin: 20px 0;
                }
                h1, h2 {
                    margin-top: 20px;
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




class HTMLReportCreator:
    def create_html_report(
        self,
        assistant_name: str,
        df_single_full: pd.DataFrame,     # ADDED
        df_single_best: pd.DataFrame,
        df_single_worst: pd.DataFrame,
        df_worst_of_4_full: pd.DataFrame, # ADDED
        df_worst_each_question: pd.DataFrame,
        paths_manager: PathsManager
    ):
        renderer = HTMLReportRenderer()
        html_content = renderer.render_report_html(
            assistant_name=assistant_name,
            df_single_full=df_single_full,           # PASS the full single data
            df_single_best=df_single_best,
            df_single_worst=df_single_worst,
            df_worst_of_4_full=df_worst_of_4_full,   # PASS the full worst-of-4
            df_worst_each_question=df_worst_each_question
        )

        html_filename = paths_manager.report_dir + f"/{assistant_name}_report.html"
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML report generated: {html_filename}")



class BotDataAnalyzer:
    """
    Coordinates the data loading, processing, 
    and creation of the HTML report with two tables and their stats.
    """
    def __init__(self):
        self.paths_manager = PathsManager()
        self.data_loader = BotDataLoader()
        self.data_processor = BotDataProcessor()
        self.worst_saver = WorstOf4Saver()
        self.html_report_creator = HTMLReportCreator()

        # Data holders
        self.df_worst_of_4 = pd.DataFrame()
        self.df_single = pd.DataFrame()
        self.df_worst_each_question = pd.DataFrame()

    def run_analysis(self, assistant_name: str):
        self.paths_manager.update_paths(assistant_name)

        # 2. Load data - the ENTIRE data sets
        self.df_worst_of_4, self.df_single = self.data_loader.load_data(self.paths_manager)

        # Generate the "biggest difference" subset for display
        self.df_worst_each_question = self.data_processor.get_best_and_worst_with_biggest_difference(
            df_worst=self.df_worst_of_4,
            top_n=MOST_DIFFERENT
        )

        if "Difference" in self.df_worst_each_question.columns:
            self.df_worst_each_question.drop(columns=["Difference"], inplace=True)

        # Generate “best” and “worst” subsets for single assessment
        self.df_single_best = self.data_processor.get_top_n(
            self.df_single, 
            n=BEST_WORST, 
            grading_col="Grading"
        )
        self.df_single_worst = self.data_processor.get_bottom_n(
            self.df_single,
            n=BEST_WORST,
            grading_col="Grading"
        )

        # Save data if you want
        # self.worst_saver.save_worst_data(self.df_worst_each_question, self.paths_manager, assistant_name)

        # CREATE HTML REPORT, passing both full DataFrames + subset DataFrames
        self.html_report_creator.create_html_report(
            assistant_name,
            df_single_full=self.df_single,                # The entire single-assessment dataset
            df_single_best=self.df_single_best,
            df_single_worst=self.df_single_worst,
            df_worst_of_4_full=self.df_worst_of_4,         # The entire worst-of-4 dataset
            df_worst_each_question=self.df_worst_each_question,
            paths_manager=self.paths_manager
        )



def main():
    bot_name = "Ai Bot You"
    analyzer = BotDataAnalyzer()
    analyzer.run_analysis(bot_name)


if __name__ == "__main__":
    main()
