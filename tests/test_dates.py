import unittest
from unittest.mock import patch, MagicMock
from collections import namedtuple

from sfrCore.model import DateField

TestDate = namedtuple('TestDate', ['id', 'display_date', 'date_range', 'date_type'])


class TestDates(unittest.TestCase):
    def test_date_repr(self):
        testDate = DateField()
        testDate.display_date = '2019'
        self.assertEqual(str(testDate), '<Date(date=2019)>')

    @patch.object(DateField, 'lookupDate', return_value=None)
    @patch.object(DateField, 'insert', return_value='newDate')
    def test_updateInsert_insert(self, mock_insert, mock_lookup):
        dateInst = {'date_type': 'test', 'display_date': '0000'}
        testDate = DateField.updateOrInsert('session', dateInst, 'test', 1)
        mock_lookup.assert_called_once()
        mock_insert.assert_called_once_with(dateInst)
        self.assertEqual(testDate, 'newDate')
    
    def test_updateInsert_update(self):
        dateInst = {'date_type': 'test', 'display_date': '0000'}
        with patch.object(DateField, 'lookupDate') as mock_lookup:
            mock_date = MagicMock()
            mock_lookup.return_value = mock_date
            testDate = DateField.updateOrInsert('session', dateInst, 'test', 1)
            mock_lookup.assert_called_once()
            self.assertEqual(testDate, mock_date)
    
    def test_date_lookup(self):
        mock_session = MagicMock()
        mock_session.query.return_value\
            .join.return_value\
            .filter.return_value.filter.return_value\
            .one_or_none.return_value = 'testDate'
        dateInst = {'date_type': 'test'}
        mock_table = MagicMock()
        mock_table.__tablename__ = 'teesting'
        testDate = DateField.lookupDate(mock_session, dateInst, mock_table, 1)
        self.assertEqual(testDate, 'testDate')
    
    @patch.object(DateField, 'cleanDateData')
    @patch.object(DateField, 'setDateRange')
    def test_update_date(self, mock_range, mock_clean):
        testDate = DateField()
        dateData = {
            'display_date': '1066',
            'date_range': '[1066-01-01,1066-12-31)'
        }
        testDate.update(dateData)
        self.assertEqual(testDate.display_date, '1066')
        self.assertEqual(testDate.date_range, None)

    @patch.object(DateField, 'setDateRange')
    @patch.object(DateField, 'cleanDateData')
    def test_insert_date(self, mock_clean, mock_parse):
        newDate = {
            'display_date': 'new',
            'date_range': '[3,4)',
            'date_type': 'tester'
        }
        res = DateField.insert(newDate)
        self.assertEqual(res.display_date, 'new')
        self.assertEqual(res.date_range, None)
        self.assertEqual(res.date_type, 'tester')
    
    @patch.object(DateField, 'parseUncertainty')
    def test_clean_date(self, mock_uncertain):
        dateData = {
            'date_range': 'date [1999?]',
            'display_date': '[1999]'
        }
        DateField.cleanDateData(dateData)
        self.assertEqual(dateData['date_range'], '1999?')
        self.assertEqual(dateData['display_date'], '1999')

    def test_parse_uncertain_4(self):
        dateData = {
            'date_range': '1999?',
            'display_date': '1999'
        }
        DateField.parseUncertainty(dateData)
        self.assertEqual(dateData['date_range'], '1998-2000')
    
    def test_parse_uncertain_3(self):
        dateData = {
            'date_range': '199?',
            'display_date': 'the 90s'
        }
        DateField.parseUncertainty(dateData)
        self.assertEqual(dateData['date_range'], '1990-1999')
    
    def test_parse_uncertain_2(self):
        dateData = {
            'date_range': '19-?',
            'display_date': '1900s'
        }
        DateField.parseUncertainty(dateData)
        self.assertEqual(dateData['date_range'], '1900-1999')

    def test_parse_single_date(self):
        testDate = DateField()
        testDate.setDateRange('2018-01-10')
        self.assertEqual(testDate.date_range, '[2018-01-10,)')

    def test_parse_date_list(self):
        testDate = DateField()
        testDate.setDateRange(['2018', '2019'])
        self.assertEqual(testDate.date_range, '[2018-01-01, 2019-12-31)')

    def test_parse_year(self):
        testDate = DateField()
        testDate.setDateRange('2018')
        self.assertEqual(testDate.date_range, '[2018-01-01, 2018-12-31)')
    
    def test_parse_years(self):
        testDate = DateField()
        testDate.setDateRange('2006-2010')
        self.assertEqual(testDate.date_range, '[2006-01-01, 2010-12-31)')
    
    def test_parse_years_reversed(self):
        testDate = DateField()
        testDate.setDateRange('2010-2006')
        self.assertEqual(testDate.date_range, None)

    def test_parse_month(self):
        testDate = DateField()
        testDate.setDateRange('2018-02')
        self.assertEqual(testDate.date_range, '[2018-02-01, 2018-02-28)')

    def test_parse_bad_date(self):
        testDate = DateField()
        testDate.setDateRange('Modnay, Dec 01, 87')
        self.assertEqual(testDate.date_range, None)
