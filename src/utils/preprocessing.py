import pandas as pd

class ExcelLoaderMixin:
    """Simple mixin to load Excel files."""
    def load_excel(self, path, **kwargs):
        return pd.read_excel(path, **kwargs)


class PopulationDataProcessor(ExcelLoaderMixin):
    def __init__(self, historical_path, recent_path):
        self.historical_path = historical_path
        self.recent_path = recent_path
        self.data = None

    def process(self):
        historical_df = self.load_excel(self.historical_path, skiprows=5).iloc[1:75, 0:2]
        historical_df.columns = ['rok', 'populacja']

        recent_df = self.load_excel(self.recent_path, sheet_name='Tabl. 1', skiprows=2)
        population_2024 = int(recent_df.iloc[1, 4] / 1000)

        historical_df.loc[len(historical_df)] = ['2024', population_2024]
        self.data = historical_df

    def get_data(self):
        if self.data is None:
            raise ValueError("Data not processed yet. Call `process()` first.")
        return self.data
