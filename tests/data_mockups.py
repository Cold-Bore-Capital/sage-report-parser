import pandas as pd

class DataMockups:
    @property
    def P_and_L_Budget(self):
        df = pd.read_csv('tests/mock_data/mock_data.csv')
        return df

    @property
    def P_and_L_Budget_Once_CC(self):
        df = pd.read_csv('tests/mock_data/mock_data_one_cc.csv')
        return df

    @property
    def P_and_L_Budget_Three_CC(self):
        df = pd.read_csv('tests/mock_data/mock_data_three_cc.csv')
        return df

    @property
    def P_and_L_Budget_One_Col(self):
        df = pd.read_csv('tests/mock_data/mock_data_one_column.csv')
        return df

