# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''
This is an integration test of the old console version.

Its slow and cumbersome.
Integration test of structjour. Especially tests on Overnight holds. Its valuable because it uses
real data as input. Other tests a random trade generator.

@created_on Feb 2, 2019

@author: Mike Petersen
'''
import os
from unittest import TestCase
from unittest.mock import patch
import unittest
from collections import deque
import re

import pandas as pd

# pylint: disable = C0103, W0603, W0613


DD = deque()
D = deque()


def mock_askUser(dummy, dummy2):
    '''
    Mock the specific askUser function that asks how many shares are currently owned or owned
    before trading today.
    '''
    global D
    x = D.popleft()
    # print("Returning from the mock ", x)
    return x


def findTrade(df, t):
    '''
    Locate the trade represented by t in the dataFrame.
    :params df: A dataFrame of the output data as found in the upper portion of the output file.
    :params t: Data of a trade as presented in testdata.csv.
    '''

    # iterate through each trade as a dataFrame dfx
    for i in range(12):
        s = "Trade " + str(i+1)
        dfx = df[df['Tindex'] == s]

        # pick out trades with the symbol
        # print(dfx)
        # print()
        if dfx.symb.unique()[0] == t[0].strip():

            wegood = False
            if t[2].lower().strip().startswith('short'):
                #  and [m.group] 'HOLD-' in list(dfx.side):
                li = list(dfx.side)
                regex = re.compile('HOLD-*')
                if [m.group(0) for l in li for m in [regex.search(l)] if m]:
                    amnt = float(-t[4])
                    wegood = True
            elif t[2].lower().strip().startswith('long'):
                li = list(dfx.side)
                regex = re.compile('HOLD-*')
                if [m.group(0) for l in li for m in [regex.search(l)] if m]:

                    # print(dfx.account.unique()[0], 'long')
                    amnt = float(t[4])
                    wegood = True
            if wegood:
                if(t[3].lower().strip().startswith('after') and
                   dfx.iloc[-1].side.startswith('HOLD') and
                   float(dfx.iloc[-2].bal) == amnt):
                    return dfx
                if(t[3].lower().strip().startswith('before') and
                   dfx.iloc[0].side.startswith('HOLD') and
                   float(dfx.iloc[0].bal) == amnt):
                    return dfx
    return pd.DataFrame()




class TestStructjour(TestCase):
    '''
    Run all of structjour with a collection of input files and test the outcome
    '''

    def __init__(self, *args, **kwargs):
        super(TestStructjour, self).__init__(*args, **kwargs)
        global DD


        self.DD = DD
        if not DD or len(D) < 11:
            DD.clear()

            # These are overnight hold shares. They are mocked user input here in mock_askUser.
            # Each list corresponds to each infile.
            DD = deque(
                [[-4000], [3923, -750], [], [600, 241, 50], [-169],
                 [], [0, -600], [], [0, 750, 50], [-600], [0, -200]])

        # Input test files can be added here. And place the test data in testdata.xlsx. Should add
        # files with potential difficulties
        self.infiles = ['trades.1116_messedUpTradeSummary10.csv', 'trades.8.WithHolds.csv',
                        'trades.8.csv', 'trades.907.WithChangingHolds.csv',
                        'trades_190117_HoldError.csv', 'trades.8.ExcelEdited.csv',
                        'trades.910.tickets.csv', 'trades_tuesday_1121_DivBy0_bug.csv',
                        'trades.8.WithBothHolds.csv', 'trades1105HoldShortEnd.csv',
                        'trades190221.BHoldPreExit.csv']

        self.getTestData(r'data/')

    def setUp(self):
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr + '/../'))

    def getTestData(self, indir):
        '''
        Open the csv file testdata and oraganze the data into a usable data structure. The file is
        necessarily populated by 'hand.' To add a file to test, copy it to the data dir and enter
        the information to test.
        :return data: List  containing the data to check against the output files.
        '''

        df = pd.read_excel(os.path.join(indir, 'testdata.xlsx'))

        l = len(df)
        # print(l)
        data = list()

        data = list()
        for i, row in df.iterrows():
            entry = list()
            if not pd.isnull(df.at[i, 'Order']):
                entry.extend((row['Order'], row['NumTrades'], row['Name']))
                j = i
                trades = list()
                begginning = True
                while j < l and not pd.isnull(df.at[j, 'Ticker']):
                    # Check these specific trades
                    if not begginning:
                        if isinstance(df.at[j, 'Name'], str):
                            break

                    trades.append([df.at[j, 'Ticker'], df.at[j, 'Account'],
                                   df.at[j, 'Side'], df.at[j, 'Held'], df.at[j, 'Pos'], ])
                    begginning = False
                    j = j+1
                entry.append(trades)
                data.append(entry)
        self.tests = data

def main():
    unittest.main()

if __name__ == '__main__':
    # pylint: disable = E1120
    # ttt = TestStructjour()
    # ttt.test_run()
    main()