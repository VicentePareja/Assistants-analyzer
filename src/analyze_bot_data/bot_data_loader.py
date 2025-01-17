import pandas as pd

from src.analyze_bot_data.paths_manager.paths_manager import PathsManager

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