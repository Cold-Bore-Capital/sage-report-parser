import pandas as pd
import numpy as np

from typing import Tuple, List


# TODO: play with # of levels, play with # of columns, play with rand # in select columns.

class SageParser:
    def __init__(self):
        pass

    def start(self,
              file_path: str = 'tests/mock_data/mock_data.csv',
              levels: List[str] = ['top', 'lower'],
              remove_rows: List[str] = None,
              drop_col_index: int = 3):
        df = pd.read_csv(file_path)

        self._drop_col_index(df, drop_col_index)

        self._identify_column_names(df)

        self._drop_agg_rows(df)

        if remove_rows:
            self._remove_extra_rows(df, remove_rows)

        df, max_f = self._create_cc_and_levels_columns(df)

        index_sleep = 0
        for i in range(len(df)):
            if index_sleep:
                index_sleep -= 1
                continue
            # If consec_count = 0 then skip to next row
            if df.loc[i, 'consec_count'] == 0:
                continue

            cc_max = self._generate_levels(df, i, max_f)

            if cc_max == 1:
                index_sleep = self._generate_level_1(df, i)

            # find next corresponding value
            elif cc_max > 1:
                index_sleep = self._generate_level_greater_than_1(df, i, cc_max, index_sleep=1)

        if levels:
            df = self._convert_column_levels(df, levels)

        df.dropna(inplace=True)
        return df

    @staticmethod
    def _drop_col_index(df: pd.DataFrame, drop_col_index: int) -> None:
        """
        Index for max col to keep
        Args:
            df: Dataframe that will be filtered
        Returns:
            None
        """
        df.drop(columns=df.columns[drop_col_index:], inplace=True)

    @staticmethod
    def _identify_column_names(df: pd.DataFrame) -> None:
        """
        Find first row where there is only one NA where the rest of the columns have
        Args:
            df: Invoice Listing dataframe
        Returns:
            None
        """
        for i in range(len(df)):
            if df.iloc[i].count() == (df.shape[1] - 1):
                cols = df.iloc[i].values
                cols[0] = 'Totals'
                break
        df.columns = cols

    @staticmethod
    def _drop_agg_rows(df: pd.DataFrame,
                       remove_str: str = 'Total') -> None:
        """
        Remove records with a string. Typically used with identifying aggregate rows.
        Args:
            df: Invoice Listing dataframe
            remove_str: Any row containing any str from remove_str will be dropped.

        Returns:
            None
        """
        mask_test = (df.Totals.str.contains(remove_str, na=False))
        df.drop(df[mask_test].index, inplace=True)
        df.reset_index(drop=True, inplace=True)

    @staticmethod
    def _remove_extra_rows(df: pd.DataFrame,
                           remove_rows: List):
        """
        Removes rows identified by users.
        Not that this method uses "str.contians()" notation.
        Args:
            df: Invoice Listing dataframe
            remove_rows: List of rows

        Returns:
            None
        """
        for i in remove_rows:
            mask_test = (df.Totals.str.contains(f"{i}", na=False))
            df.drop(df[mask_test].index, inplace=True)
            df.reset_index(drop=True, inplace=True)

    @staticmethod
    def _create_cc_and_levels_columns(df) -> Tuple[pd.DataFrame, int]:
        """
        Create the consec_count column which indicates level by index
        Args:
            df: Invoice Listing dataframe

        Returns:
            None
        """
        col = df.columns[1]
        df_ = pd.concat([df,
                         (
                             df[col].isnull().astype(int).groupby(
                                 df[col].notnull().astype(int).cumsum()).cumsum().to_frame('consec_count')
                         )], axis=1)
        max_f = df_.consec_count.max()
        for i in range(1, max_f + 1):
            df_[f'level_{i}'] = np.nan
        return df_, max_f

    @staticmethod
    def _generate_levels(df: pd.DataFrame, i: int, max_f: int) -> int:  # Tuple[int, int]:
        """
        Iteration has hit an index where consec_count != 0. The script needs to identify how many levels
        are associated in the following indexes.

        ie. if df.loc[i, 'consec_count] == 1 and df.loc[i+1, 'consec_count] == 0 then cc_max = 1
        ie. if df.loc[i, 'consec_count] == 1 and df.loc[i+1, 'consec_count] == 2 then check df.loc[i+2, 'consec_count]
        and iterate until no new levels

        Args:
            df: Index used in loop
            i: Highest leveln found
            max_f: Identifies if the next index is a lower level (x > 0) or an actual value (x = 0)

        Returns:
            cc_max: Invoice listing dataframe
        """
        # Loop through potential levels
        if max_f > 1:
            for cc in range(1, max_f):
                # If conec_count != 0 then determine which level
                if df.loc[i, 'consec_count'] == cc:
                    # Loop through multiple levels
                    for cc_max in range(cc, max_f + 1):
                        if i + cc_max >= len(df):
                            cc_max -= - 1
                            break
                        elif df.loc[i + cc_max, 'consec_count'] != cc + cc_max:
                            break
        else:
            cc_max = 1
        return cc_max

    @staticmethod
    def _generate_level_1(df: pd.DataFrame,
                          i: int) -> int:
        """
        Identify where the next level 1 index is
        Args:
            df: Invoice listing dataframe
            i: Index used in loop

        Returns:
            index_sleep: # of indexes to steps over before hitting next 1
        """
        for ii in range(i + 1, len(df)):
            if df.loc[ii, 'consec_count'] == 1:
                df.loc[i:ii, 'level_1'] = df.loc[i, 'Totals']
                index_sleep = ii - i - 1
                break
            elif ii == len(df) - 1:
                df.loc[i:, f'level_1'] = df.loc[i, 'Totals']
                index_sleep = 0
        return index_sleep

    @staticmethod
    def _generate_level_greater_than_1(df: pd.DataFrame,
                                       i: int,
                                       cc_max: int,
                                       index_sleep: int) -> int:
        """

        Args:
            df: Invoice listing dataframe
            i: Index used in loop
            cc_max: Identifies if the next index is a lower level (x > 0) or an actual value (x = 0)

        Returns:
            # of indexes to steps over before hitting next cc_max
        """
        df.loc[i:i + cc_max - 1, 'consec_count'] = df.loc[i:i + cc_max - 1, 'consec_count'].values[::-1]
        for cc_1 in range(cc_max, 0, -1):
            level_index = abs(cc_max - cc_1)
            for ii in range(i + 1 + level_index, len(df)):
                if df.loc[ii, 'consec_count'] == cc_1:
                    df.loc[i:ii, f'level_{cc_1}'] = df.loc[i + level_index, 'Totals']
                    # Set a time for lowest level
                    if cc_1 == 1:
                        index_sleep = ii - i - 1
                    break
                elif ii == len(df) - 1:
                    df.loc[i:, f'level_{cc_1}'] = df.loc[i + level_index, 'Totals']
                    index_sleep = 0
                    break
        return index_sleep

    @staticmethod
    def _convert_column_levels(df: pd.DataFrame,
                               levels: List) -> pd.DataFrame:
        """
        Seperate original and new level columns.
        Reverse the level columns and rename them
        Args:
            df: Invoice listing dataframe
            levels: User identified levels

        Returns:
            New dataframe
        """
        non_level_features = [x for x in df.columns if 'level' not in x][:-1]
        levels_old_names = [x for x in df.columns if 'level' in x][::-1]
        name_dict = dict(zip(levels_old_names, levels))
        df.rename(columns=name_dict, inplace=True)
        df_ = df.reindex(columns=levels + non_level_features)
        return df_


if __name__ == '__main__':
    sp = SageParser()
    df = sp.start()
    print('hi')
