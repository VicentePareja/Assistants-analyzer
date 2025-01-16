# -*- coding: utf-8 -*-
"""
analize_bot_data.py

This file has a class that does two main things:
1. Analyzes the data (worst_of_4 + single_assessment) and processes it.
2. Creates a PDF report using the ReportLab library.
"""

import os
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Adjust these imports to your actual project structure.
from parameters import (
    PATH_STATIC_GRADES_DIRECTORY,
    PATH_PROCESSED_RESULTS_DIRECTORY,
    PATH_REPORTS_DIRECTORY,
    PATH_TEMPLATES_DIRECTORY,
)


class BotDataAnalyzer:
    """
    A class to analyze the data for a single assistant and produce a PDF report.
    """

    def __init__(self):
        """
        Parameters
        ----------
        assistant_name : str
            The name/identifier of the assistant to analyze.
        """
        # DataFrames for loaded data
        self.df_worst_of_4 = pd.DataFrame()
        self.df_single = pd.DataFrame()

        # Combined data or any derived subsets
        self.df_combined = pd.DataFrame()
        self.df_only_worst = pd.DataFrame()

        # Basic stats store
        self.stats = {}

    def load_data(self):
        """
        Load the data from CSV files into DataFrames.
        """
        if os.path.exists(self.worst_of_4_file):
            self.df_worst_of_4 = pd.read_csv(self.worst_of_4_file, sep=';')
        else:
            print(f"Warning: worst_of_4 file not found: {self.worst_of_4_file}")

        if os.path.exists(self.single_assessment_file):
            self.df_single = pd.read_csv(self.single_assessment_file, sep=';')
        else:
            print(f"Warning: single_assessment file not found: {self.single_assessment_file}")

        # Optionally combine them (if needed)
        self.df_combined = pd.concat([self.df_worst_of_4, self.df_single], ignore_index=True)

    def process_data(self):
        """
        Process the data to compute basic statistics, filter or transform as needed.
        """
        if not self.df_combined.empty and "Grading" in self.df_combined.columns:
            valid_grades = self.df_combined["Grading"].dropna()
            if not valid_grades.empty:
                self.stats = {
                    "count": len(valid_grades),
                    "mean": np.mean(valid_grades),
                    "std": np.std(valid_grades),
                    "min": np.min(valid_grades),
                    "25%": np.percentile(valid_grades, 25),
                    "50%": np.median(valid_grades),
                    "75%": np.percentile(valid_grades, 75),
                    "max": np.max(valid_grades),
                }
            else:
                self.stats = {}
        else:
            self.stats = {}

        self.df_only_worst = self.df_worst_of_4.copy()

    def save_extracted_worst_data(self):
        """
        Save the "worst of the four" subset into a CSV in the processed directory.
        """
        output_file = self.processed_dir + f"/{self.assistant_name}_only_worst.csv"

        if not self.df_only_worst.empty:
            self.df_only_worst.to_csv(output_file, index=False, sep=';')
            print(f"Extracted worst-of-4 data saved to: {output_file}")
        else:
            print("No data in df_only_worst. Skipping save.")

    def render_report_html(self) -> str:
        """
        Render an HTML string using a Jinja2 template.
        Returns
        -------
        str
            The rendered HTML content.
        """
        templates_dir = PATH_TEMPLATES_DIRECTORY
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template("report_template.html")

        context_data = {
            "assistant_name": self.assistant_name,
            "stats": self.stats,
            "worst_rows": self.df_only_worst.to_dict(orient="records"),
            "single_rows": self.df_single.to_dict(orient="records"),
        }
        return template.render(**context_data)

    def create_pdf_report(self):
        """
        Generate a PDF report using ReportLab.
        """
        pdf_filename = self.report_dir + f"/{self.assistant_name}_report.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 50, f"Report for Assistant: {self.assistant_name}")

        # Draw statistics
        c.setFont("Helvetica", 12)
        y_position = height - 80
        for key, value in self.stats.items():
            c.drawString(30, y_position, f"{key.capitalize()}: {value}")
            y_position -= 20

        # Add table headers for "worst of 4"
        y_position -= 30
        if not self.df_only_worst.empty:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, y_position, "Worst of 4:")
            y_position -= 20
            for row in self.df_only_worst.to_dict(orient="records"):
                c.setFont("Helvetica", 10)
                c.drawString(30, y_position, str(row))
                y_position -= 15

        c.save()
        print(f"PDF report generated: {pdf_filename}")

    def update_paths(self, assistant_name: str):
        self.assistant_name = assistant_name
        self.worst_of_4_file = PATH_STATIC_GRADES_DIRECTORY + f"/{assistant_name}_grades_worst_of_4.csv"
        self.single_assessment_file = PATH_STATIC_GRADES_DIRECTORY + f"/{assistant_name}_grades_single_assessment.csv"

        self.processed_dir = PATH_PROCESSED_RESULTS_DIRECTORY
        self.report_dir = PATH_REPORTS_DIRECTORY

        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)

    def run_analysis(self, assistant_name: str):
        self.update_paths(assistant_name)
        self.load_data()
        self.process_data()
        self.save_extracted_worst_data()
        self.create_pdf_report()


def main():
    bot_name = "name_assistant"
    analyzer = BotDataAnalyzer()
    analyzer.run_analysis(bot_name)


if __name__ == "__main__":
    main()
