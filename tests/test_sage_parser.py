from unittest import TestCase

import pandas as pd
import os
import sys

sys.path.append(os.getcwd())

from app.parsers.sage_parser import SageParser
from tests.data_mockups import DataMockups
from dotenv import load_dotenv, find_dotenv


class TestSageParser(TestCase):
    def test__drop_col_index(self):
        # Test to drop 3 columns and 4 columns
        sp = SageParser
        df = DataMockups().P_and_L_Budget
        sp._drop_col_index(df, 3)
        self.assertEqual(df.shape[1], 3)

        df = DataMockups().P_and_L_Budget
        sp._drop_col_index(df, 4)
        self.assertEqual(df.shape[1], 4)

    def test__identify_column_names(self):
        # Test to identify column names
        sp = SageParser
        df = DataMockups().P_and_L_Budget
        sp._drop_col_index(df, 3)

        count_ = 0
        for c in df.columns.values:
            if 'Unnamed' in c:
                count_ += 1

        self.assertTrue(count_ > 0)
        sp._identify_column_names(df)

        count_ = 0
        for c in df.columns.values:
            if 'Unnamed' in c:
                count_ += 1

        self.assertTrue(count_ == 0)

    def test__drop_agg_rows(self, remove_str: str = "Total"):
        # Test to drop rows with name Total in them
        sp = SageParser
        df = DataMockups().P_and_L_Budget

        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        totals_count = sum(df.Totals.str.contains(remove_str, na=False))
        self.assertTrue(totals_count > 0)

        sp._drop_agg_rows(df)

        totals_count = sum(df.Totals.str.contains(remove_str, na=False))
        self.assertTrue(totals_count == 0)

    def test___remove_extra_rows(self):
        # Test to remove extra rows based off of user input
        sp = SageParser
        df = DataMockups().P_and_L_Budget

        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)

        x = len(df)
        sp._remove_extra_rows(df, remove_rows=['M&A Travel', 'Dues and Subscriptions'])
        self.assertEqual(x - 2, len(df))

    def test__create_cc_and_levels_columns(self):
        # Create consecutive count column and level columns
        sp = SageParser
        df = DataMockups().P_and_L_Budget

        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        # Assert that max level is 2
        self.assertEqual(max_f, 2)

        # Asert that consec_count column exists
        self.assertTrue('consec_count' in df.columns)

    def test___generate_levels(self):
        # Identify how many levels associated when value > 0 in consec_count col
        # 1 column
        sp = SageParser
        df = DataMockups().P_and_L_Budget_One_Col
        sp._drop_col_index(df, 2)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        index_sleep = 0
        for i in range(len(df)):
            if index_sleep:
                index_sleep -= 1
                continue
            # If consec_count = 0 then skip to next row
            elif df.loc[i, 'consec_count'] == 0:
                continue
            elif i == 4:
                raise Exception

        # 1 cc column
        sp = SageParser
        df = DataMockups().P_and_L_Budget_Once_CC
        sp._drop_col_index(df, 2)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        index_sleep = 0
        for i in range(len(df)):
            if index_sleep:
                index_sleep -= 1
                continue
            # If consec_count = 0 then skip to next row
            elif df.loc[i, 'consec_count'] == 0:
                continue

            elif i == 4:
                raise Exception

    def test__generate_level_1(self):
        # Identify next 1 in consec_count col
        # Identify on normal mock
        sp = SageParser
        df = DataMockups().P_and_L_Budget
        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        index_sleep = 0
        for i in range(len(df)):
            if index_sleep:
                index_sleep -= 1
                continue
            # If consec_count = 0 then skip to next row
            if df.loc[i, 'consec_count'] == 0:
                continue

            cc_max = sp._generate_levels(df, i, max_f)
            if cc_max == 1:
                index_sleep = sp._generate_level_1(df, i)
                self.assertEqual(df.loc[i,'Totals'], df.loc[i,'level_1'])

            # find next corresponding value
            elif cc_max > 1:
                index_sleep = sp._generate_level_greater_than_1(df, i, cc_max, index_sleep)

        # Identify on 1 cc
        sp = SageParser
        df = DataMockups().P_and_L_Budget_Once_CC
        sp._drop_col_index(df, 2)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        index_sleep = 0
        for i in range(len(df)):
            if index_sleep:
                index_sleep -= 1
                continue
            # If consec_count = 0 then skip to next row
            if df.loc[i, 'consec_count'] == 0:
                continue

            cc_max = sp._generate_levels(df, i, max_f)
            if cc_max == 1:
                index_sleep = sp._generate_level_1(df, i)
                self.assertEqual(df.loc[i, 'Totals'], df.loc[i, 'level_1'])

            # find next corresponding value
            elif cc_max > 1:
                index_sleep = sp._generate_level_greater_than_1(df, i, cc_max, index_sleep)

        # Test on one column
        sp = SageParser
        df = DataMockups().P_and_L_Budget_One_Col
        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        index_sleep = 0
        for i in range(len(df)):
            if index_sleep:
                index_sleep -= 1
                continue
            # If consec_count = 0 then skip to next row
            if df.loc[i, 'consec_count'] == 0:
                continue

            cc_max = sp._generate_levels(df, i, max_f)
            if cc_max == 1:
                index_sleep = sp._generate_level_1(df, i)
                self.assertEqual(df.loc[i,'Totals'], df.loc[i,'level_1'])

            # find next corresponding value
            elif cc_max > 1:
                index_sleep = sp._generate_level_greater_than_1(df, i, cc_max, index_sleep)

    def test___generate_level_greater_than_1(self):
        # Identify next val > 1 in consec_count col
        sp = SageParser
        df = DataMockups().P_and_L_Budget_Three_CC
        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        # Assert that max level is 2
        self.assertEqual(max_f, 3)

        index_sleep = 0
        for i in range(len(df)):
            if index_sleep:
                index_sleep -= 1
                continue
            # If consec_count = 0 then skip to next row
            if df.loc[i, 'consec_count'] == 0:
                continue

            cc_max = sp._generate_levels(df, i, max_f)
            if cc_max == 1:
                index_sleep = sp._generate_level_1(df, i)

            # find next corresponding value
            elif cc_max > 1:
                index_sleep = sp._generate_level_greater_than_1(df, i, cc_max, index_sleep)
                self.assertEqual(df.loc[i,'Totals'], df.loc[i,f'level_{cc_max}'])


        sp = SageParser
        df = DataMockups().P_and_L_Budget
        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        index_sleep = 0
        for i in range(len(df)):
            if index_sleep:
                index_sleep -= 1
                continue
            # If consec_count = 0 then skip to next row
            if df.loc[i, 'consec_count'] == 0:
                continue

            cc_max = sp._generate_levels(df, i, max_f)
            if cc_max == 1:
                index_sleep = sp._generate_level_1(df, i)

            # find next corresponding value
            elif cc_max > 1:
                index_sleep = sp._generate_level_greater_than_1(df, i, cc_max, index_sleep)
                self.assertEqual(df.loc[i,'Totals'], df.loc[i,f'level_{cc_max}'])

    def test__convert_column_levels(self):
        # 1 Levels
        sp = SageParser
        df = DataMockups().P_and_L_Budget
        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        df = sp._convert_column_levels(df, levels=['top'])
        self.assertCountEqual(df.columns[:1], ['top'])

        # 2 Levels
        sp = SageParser
        df = DataMockups().P_and_L_Budget
        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        df = sp._convert_column_levels(df, levels=['top','bottom'])
        self.assertCountEqual(df.columns[:2], ['top','bottom'])

        # 3 Levels
        sp = SageParser
        df = DataMockups().P_and_L_Budget
        sp._drop_col_index(df, 3)
        sp._identify_column_names(df)
        sp._drop_agg_rows(df)
        df, max_f = sp._create_cc_and_levels_columns(df)

        df = sp._convert_column_levels(df, levels=['top', 'middle', 'bottom'])
        self.assertCountEqual(df.columns[:3], ['top', 'middle','bottom'])

if __name__ == '__main__':
    x = TestSageParser()
    x.test__drop_col_index()
    x.test__identify_column_names()
    x.test__drop_agg_rows()
    x.test___remove_extra_rows()
    x.test__create_cc_and_levels_columns()
    x.test___generate_levels()
    x.test__generate_level_1()
    x.test___generate_level_greater_than_1()
    x.test__convert_column_levels()
