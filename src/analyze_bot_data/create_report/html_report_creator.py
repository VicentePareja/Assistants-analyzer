# html_report_creator.py
import pandas as pd
from src.analyze_bot_data.paths_manager.paths_manager import PathsManager
from src.analyze_bot_data.create_report.html_report_renderer import HTMLReportRenderer

class HTMLReportCreator:
    def create_html_report(
        self,
        assistant_name: str,
        df_single_full: pd.DataFrame,
        df_worst_of_4_per_question: pd.DataFrame,
        percentage_worst_of_4_above_threshold: float,
        threshold: float,
        df_worst_of_4_below_threshold_no_repeat: pd.DataFrame,
        paths_manager: PathsManager
    ):
        renderer = HTMLReportRenderer()
        html_content = renderer.render_report_html(
            assistant_name=assistant_name,
            df_single_full=df_single_full,

            # Summaries & metrics
            df_worst_of_4_per_question=df_worst_of_4_per_question,
            percentage_worst_of_4_above_threshold=percentage_worst_of_4_above_threshold,
            threshold=threshold,

            # Final table
            df_worst_of_4_below_threshold_no_repeat=df_worst_of_4_below_threshold_no_repeat
        )

        html_filename = paths_manager.report_dir + f"/{assistant_name}_report.html"
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML report generated: {html_filename}")
