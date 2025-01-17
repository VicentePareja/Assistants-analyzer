import pandas as pd

from src.analyze_bot_data.paths_manager.paths_manager import PathsManager
from src.analyze_bot_data.create_report.html_report_creator import HTMLReportCreator
from src.analyze_bot_data.bot_data_loader import BotDataLoader
from src.analyze_bot_data.bot_data_processor import BotDataProcessor, WorstOf4Saver

from parameters import (
    BEST_WORST, 
    MOST_DIFFERENT, 
)


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