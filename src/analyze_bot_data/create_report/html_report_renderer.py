# html_report_renderer.py

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from parameters import (
    PATH_TEMPLATES_DIRECTORY,

    REPORT_FONT_FAMILY,
    REPORT_FONT_SIZE,
    REPORT_TEXT_COLOR,

    REPORT_HEADING_FONT_SIZE,
    REPORT_SUBHEADING_FONT_SIZE,

    REPORT_HEADER_BG_COLOR,
    REPORT_HEADER_TEXT_COLOR,

    REPORT_ALT_ROW_BG_COLOR,
    REPORT_HOVER_ROW_BG,

    REPORT_MAIN_BG_COLOR,
    REPORT_TABLE_SHADOW_COLOR,
    REPORT_TABLE_BORDER_RADIUS,
    REPORT_TABLE_BORDER_COLOR,
    REPORT_TABLE_TEXT_COLOR,

    REPORT_HEADING_COLOR,
    REPORT_SUBHEADING_COLOR,

    REPORT_CONTAINER_MAX_WIDTH,
    REPORT_CONTAINER_MARGIN,
    REPORT_CONTAINER_PADDING,

    REPORT_BODY_MARGIN,
    REPORT_BODY_PADDING,

    REPORT_THRESHOLD_BOX_BG_COLOR,
    REPORT_THRESHOLD_BOX_BORDER_COLOR,
    REPORT_THRESHOLD_BOX_TEXT_COLOR,

    REPORT_THRESHOLD_SECTION_BG_COLOR,
    REPORT_THRESHOLD_SECTION_TEXT_COLOR,

    REPORT_PERCENTAGE_SECTION_BG_COLOR,
    REPORT_PERCENTAGE_SECTION_TEXT_COLOR,

    REPORT_PARAGRAPH_LINE_HEIGHT,
    REPORT_PARAGRAPH_MARGIN,

    REPORT_BOLD_HIGHLIGHT_COLOR,

    REPORT_THRESHOLD_BOX_HOVER_BG_COLOR,
    REPORT_THRESHOLD_BOX_HOVER_SHADOW
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
        """
        Renders an HTML report using provided data and styling parameters.
        """

        # Initialize Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(PATH_TEMPLATES_DIRECTORY),
            autoescape=select_autoescape(["html", "xml"])
        )

        try:
            # Manually load the template file as a string
            with open("src/analyze_bot_data/create_report/templates/report_template.html", "r", encoding="utf-8") as f:
                template_content = f.read()

            # Parse the template content into a Jinja2 Template object
            template = env.from_string(template_content)

        except Exception as e:
            print(f"Error loading template: {str(e)}")
            return None

        # Prepare summary data
        df_single_summary = df_single_full.describe().T.reset_index()
        single_summary_rows = df_single_summary.to_dict(orient="records")
        single_summary_columns = df_single_summary.columns.tolist()

        df_worst_summary = df_worst_of_4_per_question.describe().T.reset_index()
        worst_summary_rows = df_worst_summary.to_dict(orient="records")
        worst_summary_columns = df_worst_summary.columns.tolist()

        worst_of_4_below_threshold_rows = df_worst_of_4_below_threshold_no_repeat.to_dict(orient="records")
        worst_of_4_below_threshold_columns = df_worst_of_4_below_threshold_no_repeat.columns.tolist()

        # Render HTML using the template
        return template.render(
            assistant_name=assistant_name,

            # Style parameters
            font_family=REPORT_FONT_FAMILY,
            font_size=REPORT_FONT_SIZE,
            text_color=REPORT_TEXT_COLOR,

            heading_font_size=REPORT_HEADING_FONT_SIZE,
            subheading_font_size=REPORT_SUBHEADING_FONT_SIZE,

            heading_color=REPORT_HEADING_COLOR,
            subheading_color=REPORT_SUBHEADING_COLOR,

            header_bg_color=REPORT_HEADER_BG_COLOR,
            header_text_color=REPORT_HEADER_TEXT_COLOR,

            alt_row_bg_color=REPORT_ALT_ROW_BG_COLOR,
            hover_row_bg=REPORT_HOVER_ROW_BG,

            main_bg_color=REPORT_MAIN_BG_COLOR,
            table_shadow_color=REPORT_TABLE_SHADOW_COLOR,
            table_border_radius=REPORT_TABLE_BORDER_RADIUS,
            table_border_color=REPORT_TABLE_BORDER_COLOR,
            table_text_color=REPORT_TABLE_TEXT_COLOR,

            container_max_width=REPORT_CONTAINER_MAX_WIDTH,
            container_margin=REPORT_CONTAINER_MARGIN,
            container_padding=REPORT_CONTAINER_PADDING,

            body_margin=REPORT_BODY_MARGIN,
            body_padding=REPORT_BODY_PADDING,

            threshold_box_bg_color=REPORT_THRESHOLD_BOX_BG_COLOR,
            threshold_box_border_color=REPORT_THRESHOLD_BOX_BORDER_COLOR,
            threshold_box_text_color=REPORT_THRESHOLD_BOX_TEXT_COLOR,

            threshold_section_bg_color=REPORT_THRESHOLD_SECTION_BG_COLOR,
            threshold_section_text_color=REPORT_THRESHOLD_SECTION_TEXT_COLOR,

            percentage_section_bg_color=REPORT_PERCENTAGE_SECTION_BG_COLOR,
            percentage_section_text_color=REPORT_PERCENTAGE_SECTION_TEXT_COLOR,

            paragraph_line_height=REPORT_PARAGRAPH_LINE_HEIGHT,
            paragraph_margin=REPORT_PARAGRAPH_MARGIN,

            bold_highlight_color=REPORT_BOLD_HIGHLIGHT_COLOR,

            # Data for tables
            single_summary_rows=single_summary_rows,
            single_summary_columns=single_summary_columns,
            worst_summary_rows=worst_summary_rows,
            worst_summary_columns=worst_summary_columns,

            percentage_worst_of_4_above_threshold=percentage_worst_of_4_above_threshold,
            threshold=threshold,

            worst_of_4_below_threshold_rows=worst_of_4_below_threshold_rows,
            worst_of_4_below_threshold_columns=worst_of_4_below_threshold_columns,
            threshold_box_hover_bg_color=REPORT_THRESHOLD_BOX_HOVER_BG_COLOR,
            threshold_box_hover_shadow=REPORT_THRESHOLD_BOX_HOVER_SHADOW

        )
