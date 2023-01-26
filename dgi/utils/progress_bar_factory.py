# Fancy Progress Bar
import os
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    SpinnerColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
    TimeRemainingColumn
)

class ProgressBarFactory:
    @classmethod
    def get_progress_bar(cls):
        progress_bar = Progress(
            SpinnerColumn(),
            TextColumn("•"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            BarColumn(),
            TextColumn("• Completed/Total:"),
            MofNCompleteColumn(),
            TextColumn("• Elapsed:"),
            TimeElapsedColumn(),
            TextColumn("• Remaining:"),
            TimeRemainingColumn())
        return progress_bar
