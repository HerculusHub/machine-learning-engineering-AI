from pathlib import Path

import pandas as pd

from mobile_ai_system.core.config import get_settings


class CustomerDataClient:
    """
    Business Database (CSV)
    """

    def __init__(self):

        self.settings = get_settings()

        self.csv_path = Path(
            self.settings.business_data_path
        )

        self.data = None

    def load(self):

        self.data = pd.read_csv(
            self.csv_path
        )

        return self.data

    def get_dataframe(self):

        if self.data is None:
            self.load()

        return self.data

    def row_count(self):

        return len(
            self.get_dataframe()
        )

    def columns(self):

        return list(
            self.get_dataframe().columns
        )