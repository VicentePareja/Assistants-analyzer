# analyze_bot_data.py
import pandas as pd

from src.analyze_bot_data.paths_manager.paths_manager import PathsManager
from src.analyze_bot_data.create_report.html_report_creator import HTMLReportCreator
from src.analyze_bot_data.bot_data_loader import BotDataLoader
from src.analyze_bot_data.bot_data_processor import BotDataProcessor

from parameters import THRESHOLD

class BotDataAnalyzer:
    def __init__(self):
        self.paths_manager = PathsManager()
        self.data_loader = BotDataLoader()
        self.data_processor = BotDataProcessor()
        self.html_report_creator = HTMLReportCreator()

        self.df_single = pd.DataFrame()
        self.df_worst_of_4 = pd.DataFrame()

    def run_analysis(self, assistant_name: str):
        # 1) Update paths
        self.paths_manager.update_paths(assistant_name)

        # 2) Load data
        #    df_worst_of_4: possibly multiple entries per question
        #    df_single: single-assessment dataset
        self.df_worst_of_4, self.df_single = self.data_loader.load_data(self.paths_manager)

        # 3) Get the single worst answer per question (no duplicates)
        worst_of_4_per_question = self.data_processor.get_worst_answer_per_question(self.df_worst_of_4)

        # 4) Compute how many are ABOVE the threshold (instead of below)
        above_threshold_df = worst_of_4_per_question[worst_of_4_per_question["Grading"] >= THRESHOLD]
        if len(worst_of_4_per_question) > 0:
            percentage_worst_of_4_above_threshold = (
                len(above_threshold_df) / len(worst_of_4_per_question) * 100
            )
        else:
            percentage_worst_of_4_above_threshold = 0.0

        # 5) Final table: only the worst answers per question that are BELOW threshold
        #    (thus, no repeated questions)
        worst_of_4_below_threshold_no_repeat = self.data_processor.get_rows_below_threshold(
            worst_of_4_per_question, threshold=THRESHOLD
        )

        # 6) Generate the HTML report
        self.html_report_creator.create_html_report(
            assistant_name=assistant_name,
            df_single_full=self.df_single,

            # Only the single-worst-per-question subset for summary
            df_worst_of_4_per_question=worst_of_4_per_question,

            # We are now showing the percentage above threshold
            percentage_worst_of_4_above_threshold=percentage_worst_of_4_above_threshold,
            threshold=THRESHOLD,

            # Final table: only the below-threshold worst answers
            df_worst_of_4_below_threshold_no_repeat=worst_of_4_below_threshold_no_repeat,

            paths_manager=self.paths_manager
        )
