import pandas as pd

from src.analyze_bot_data.paths_manager.paths_manager import PathsManager
from src.analyze_bot_data.create_report.html_report_renderer import HTMLReportRenderer

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