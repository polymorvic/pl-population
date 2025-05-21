import pandas as pd
import numpy as np
from typing import Optional
from .const import GUS_COLNAMES

class ExcelLoaderMixin:
    """Simple mixin to load Excel files."""
    def load_excel(self, path, **kwargs):
        return pd.read_excel(path, **kwargs)


class PopulationDataProcessor(ExcelLoaderMixin):
    def __init__(self, historical_path: str, recent_path: str):
        self.historical_path = historical_path
        self.recent_path = recent_path
        self.historical_df: Optional[pd.DataFrame] = None
        self.recent_df: Optional[pd.DataFrame] = None

    def __process_historical(self) -> None:
        cols_idxs = np.r_[0:10, 11, 13, 14]
        self.historical_df = self.load_excel(self.historical_path, skiprows=5).iloc[1:75, cols_idxs]
        self.historical_df.columns = GUS_COLNAMES

        for col in self.historical_df.columns[1:]:
            s = self.historical_df[col]
            if not pd.api.types.is_numeric_dtype(s):
                s = pd.to_numeric(s.str.replace('[a-zA-Z]', '', regex=True).str.replace(',', '.'), errors='coerce')

    def __process_recent(self) -> None:
        df = self.load_excel(self.recent_path, skiprows=5).iloc[:, [0, 1, 15]]
        df.columns = ['rok', 'populacja', 'przyrost_naturalny']

        df = df[df['rok'].astype(str).str.startswith('2024')]

        for col in ['populacja', 'przyrost_naturalny']:
            if pd.api.types.is_object_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df['rok'] = '2024'

        self.recent_df = df.groupby('rok', as_index=False).agg({
            'populacja': lambda x: int(np.mean(x.dropna())), 
            'przyrost_naturalny': 'sum'
        })

    def get_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        try:
            self.__process_historical()
            self.__process_recent()
        except Exception as error:
            print(f'Something went wrong processing data - {error}')
            return tuple(pd.DataFrame() for _ in range(2))
        
        return self.historical_df, pd.concat([self.historical_df, self.recent_df], ignore_index=True)[['rok', 'populacja', 'przyrost_naturalny']]
