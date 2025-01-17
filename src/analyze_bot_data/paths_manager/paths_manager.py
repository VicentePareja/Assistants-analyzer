from parameters import (
    PATH_STATIC_GRADES_DIRECTORY,
    PATH_PROCESSED_RESULTS_DIRECTORY,
    PATH_REPORTS_DIRECTORY)

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