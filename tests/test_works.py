import unittest
from unittest.mock import patch, MagicMock, call, DEFAULT
from collections import namedtuple

from sqlalchemy.orm.exc import NoResultFound

from sfrCore.model.work import Work, AgentWorks
from sfrCore.model.date import DateField

from sfrCore.helpers import DataError, DBError

TestDate = namedtuple('TestDate', ['id', 'display_date', 'date_range', 'date_type'])

class WorkTest(unittest.TestCase):
    def test_work_init(self):
        testWork = Work()
        testWork.summary = 'Summary'
        testWork.title = 'Testing'
        self.assertEqual(testWork.summary, 'Summary')
        self.assertEqual(str(testWork), '<Work(title=Testing)>')

    def test_create_tmp(self):
        workData = {
            'links': ['link1', 'link2'],
            'identifiers': ['id1', 'id2', 'id3']
        }
        testWork = Work()
        testWork.createTmpRelations(workData)
        self.assertEqual(testWork.tmp_identifiers[1], 'id2')
        self.assertEqual(len(testWork.tmp_links), 2)
        self.assertEqual(testWork.links, set())
    
    def test_remove_tmp(self):
        testWork = Work()
        testWork.createTmpRelations({})
        testWork.tmp_links = ['link1', 'link2']
        testWork.removeTmpRelations()
        with self.assertRaises(AttributeError):
            tmpLinks = testWork.tmp_links
    
    def test_work_insert(self):
        testData = {
            'title': 'Test Title'
        }
        mock_session = MagicMock()
        testWork = Work(session=mock_session)
        testWork.epubsToLoad = []
        with patch.multiple(Work,
            createTmpRelations=DEFAULT,
            addImportJson=DEFAULT,
            addIdentifiers=DEFAULT,
            addInstances=DEFAULT,
            addAgents=DEFAULT,
            addAltTitles=DEFAULT,
            addSubjects=DEFAULT,
            addMeasurements=DEFAULT,
            addLinks=DEFAULT,
            addDates=DEFAULT,
            addLanguages=DEFAULT,
            removeTmpRelations=DEFAULT
        ) as item_mocks:
            newEpubs = testWork.insert(testData)
            self.assertEqual(testWork.title, 'Test Title')
            self.assertEqual(newEpubs, [])
    
    def test_item_update(self):
        testData = {
            'title': 'Title',
            'series': 'newSeries'
        }
        testWork = Work()
        testWork.title = 'Title'
        testWork.series = 'oldSeries'
        testWork.epubsToLoad = []
        with patch.multiple(Work,
            createTmpRelations=DEFAULT,
            addImportJson=DEFAULT,
            addTitles=DEFAULT,
            updateIdentifiers=DEFAULT,
            updateInstances=DEFAULT,
            updateAgents=DEFAULT,
            updateSubjects=DEFAULT,
            updateMeasurements=DEFAULT,
            updateLinks=DEFAULT,
            updateDates=DEFAULT,
            updateLanguages=DEFAULT,
            removeTmpRelations=DEFAULT
        ) as item_mocks:
            newEpubs = testWork.update(testData)
            self.assertEqual(testWork.series, 'newSeries')
            self.assertEqual(newEpubs, [])

    @patch('sfrCore.model.work.RawData')
    def test_import_json(self, mock_raw):
        testWork = Work()
        testWork.tmp_storeJson = ['testJSON']
        mock_val = MagicMock()
        mock_val.value = 'testJSON'
        mock_raw.return_value = mock_val
        testWork.addImportJson()
        self.assertEqual(list(testWork.import_json)[0].value, 'testJSON')

    @patch('sfrCore.model.work.Instance.createNew')
    def test_add_instances(self, mock_create):
        testWork = Work()
        testWork.tmp_instances = ['inst1', 'inst2']

        mock_inst = MagicMock()
        mock_inst.name = 'testInstance'
        
        mock_create.side_effect = [(mock_inst, []), (mock_inst, [])]

        testWork.addInstances()
        self.assertEqual(list(testWork.instances)[0].name, 'testInstance')
    
    @patch.object(Work, 'updateInstance')
    def test_update_instances(self, mock_update):
        testWork = Work()
        testWork.tmp_instances = ['inst1']
        testWork.updateInstances()
        mock_update.called_once_with('inst1')
    
    @patch('sfrCore.model.work.Instance')
    def test_update_instance(self, mock_inst):
        testWork = Work()
        mock_val = MagicMock()
        mock_val.value = 'testInst'
        mock_inst.updateOrInsert.return_value = mock_val

        testWork.updateInstance('inst1')
        self.assertEqual(list(testWork.instances)[0].value, 'testInst')
    
    @patch('sfrCore.model.work.Instance')
    def test_update_instance_err(self, mock_inst):
        testWork = Work()
        mock_val = MagicMock()
        mock_val.value = 'testInst'
        mock_inst.updateOrInsert.side_effect = DataError('test err')

        testWork.updateInstance('inst1')
        self.assertEqual(testWork.instances, set())
    
    @patch.object(Work, 'addIdentifier')
    def test_add_identifiers(self, mock_add):
        testWork = Work()
        testWork.tmp_identifiers = ['id1']
        mock_val = MagicMock()
        mock_val.value = 'testID'
        mock_add.return_value = mock_val

        testWork.addIdentifiers()
        self.assertEqual(list(testWork.identifiers)[0].value, 'testID')
    
    @patch('sfrCore.model.work.Identifier')
    def test_add_identifier(self, mock_identifier):
        testWork = Work()
        mock_id = MagicMock()
        mock_id.value = 'id1'
        mock_identifier.returnOrInsert.return_value = mock_id

        testID = testWork.addIdentifier('id1')
        self.assertEqual(testID.value, 'id1')
    
    @patch('sfrCore.model.work.Identifier')
    def test_add_identifier_err(self, mock_identifier):
        testWork = Work()
        mock_identifier.returnOrInsert.side_effect = DataError('test error')
        testID = testWork.addIdentifier('id1')
        self.assertEqual(testID, None)
    
    @patch.object(Work, 'updateIdentifier')
    def test_update_identifiers(self, mock_update):
        testWork = Work()
        testWork.tmp_identifiers = ['id1']
        testWork.updateIdentifiers()
        mock_update.assert_has_calls([call('id1')])
    
    @patch('sfrCore.model.work.Identifier')
    def test_update_identifier(self, mock_identifier):
        testWork = Work()
        mock_id = MagicMock()
        mock_id.value = 'id1'
        mock_identifier.returnOrInsert.return_value = mock_id

        testWork.updateIdentifier('id1')
        self.assertEqual(list(testWork.identifiers)[0].value, 'id1')
    
    @patch('sfrCore.model.work.Identifier')
    def test_update_identifier_err(self, mock_identifier):
        testWork = Work()
        mock_identifier.returnOrInsert.side_effect = DataError('test error')
        testWork.updateIdentifier('id1')
        self.assertEqual(testWork.identifiers, set())

    @patch('sfrCore.model.work.Agent')
    @patch('sfrCore.model.work.AgentWorks')
    def test_add_agent(self, mock_agent_works, mock_agent):
        testWork = Work()
        mock_name = MagicMock()
        mock_name.name = 'test_agent'
        mock_agent.updateOrInsert.return_value = mock_name, ['tester']

        testWork.addAgent('agent1')
        mock_agent_works.assert_called_once()

    @patch('sfrCore.model.work.AltTitle')
    def test_add_alt_titles(self, mock_alt):
        testWork = Work()
        testWork.tmp_alt_titles = ['alt1']
        mock_val = MagicMock()
        mock_val.value = 'test_title'
        mock_alt.return_value = mock_val

        testWork.addAltTitles()
        self.assertEqual(list(testWork.alt_titles)[0].value, 'test_title')
    
    @patch('sfrCore.model.work.Subject')
    def test_add_subjects(self, mock_subj):
        testWork = Work()
        testWork.tmp_subjects = ['subject1']
        mock_val = MagicMock()
        mock_val.value = 'test_subject'
        mock_subj.updateOrInsert.return_value = mock_val

        testWork.addSubjects()
        self.assertEqual(list(testWork.subjects)[0].value, 'test_subject')
    
    @patch('sfrCore.model.work.Measurement')
    def test_add_measurement(self, mock_meas):
        testWork = Work()
        testWork.tmp_measurements = ['measure1']
        mock_val = MagicMock()
        mock_val.value = 'test_measure'

        mock_meas.insert.return_value = mock_val

        testWork.addMeasurements()
        self.assertEqual(list(testWork.measurements)[0].value, 'test_measure')
    
    @patch('sfrCore.model.work.Link')
    def test_add_link(self, mock_link):
        testWork = Work()
        testWork.tmp_links = [{'link': 'link1'}]
        mock_val = MagicMock()
        mock_val.value = 'test_link'

        mock_link.return_value = mock_val

        testWork.addLinks()
        self.assertEqual(list(testWork.links)[0].value, 'test_link')
    
    @patch('sfrCore.model.work.DateField')
    def test_add_date(self, mock_date):
        testWork = Work()
        testWork.tmp_dates = ['date1']
        mock_val = MagicMock()
        mock_val.value = 'test_date'

        mock_date.insert.return_value = mock_val

        testWork.addDates()
        self.assertEqual(list(testWork.dates)[0].value, 'test_date')
    
    @patch.object(Work, 'addLanguage')
    def test_add_languages(self, mock_add):
        testWork = Work()
        testWork.tmp_language = ['lang1']
        mock_val = MagicMock()
        mock_val.value = 'test_language'

        mock_add.return_value = mock_val

        testWork.addLanguages()
        self.assertEqual(len(list(testWork.language)), 1)
        self.assertEqual(list(testWork.language)[0].value, 'test_language')
    
    @patch.object(Work, 'addLanguage')
    def test_add_languages_str(self, mock_add):
        testWork = Work()
        testWork.tmp_language = 'lang1'
        mock_val = MagicMock()
        mock_val.value = 'test_language'

        mock_add.return_value = mock_val

        testWork.addLanguages()
        self.assertEqual(len(list(testWork.language)), 1)
        self.assertEqual(list(testWork.language)[0].value, 'test_language')


    @patch.object(Work, 'getByUUID', return_value='test_id')
    def test_lookup_uuid(self, mock_get_uuid):
        testID = Work.lookupWork('session', ['id1'], {
            'type': 'uuid',
            'identifier': 'test_uuid'
        })
        self.assertEqual(testID, 'test_id')
    
    @patch('sfrCore.model.work.Identifier')
    def test_lookup_work(self, mock_iden):
        mock_session = MagicMock()
        mock_session.query().get.return_value = 'test_work'
        mock_iden.getByIdentifier.return_value = 'test_id'
        testID = Work.lookupWork(mock_session, ['id1'], None)
        self.assertEqual(testID, 'test_work')
    
    @patch('sfrCore.model.work.Identifier')
    def test_lookup_work_by_instance(self, mock_iden):
        mock_session = MagicMock()
        mock_session.query().filter().one.return_value = (1,)
        mock_session.query().get.return_value = 'test_work'
        mock_iden.getByIdentifier.side_effect = [None, 'test_id']
        testID = Work.lookupWork(mock_session, ['id1'], None)
        self.assertEqual(testID, 'test_work')
    
    @patch('sfrCore.model.work.Identifier')
    def test_lookup_work_not_found(self, mock_iden):
        mock_session = MagicMock()
        mock_session.query().get().work.uuid = 'test_uuid'
        mock_iden.getByIdentifier.side_effect = [None, None]
        testID = Work.lookupWork(mock_session, ['id1'], None)
        self.assertEqual(testID, None)

    @patch('sfrCore.model.work.uuid.UUID', return_value='test_uuid')
    def test_get_by_uuid(self, mock_uuid):
        mock_session = MagicMock()
        mock_session.query().filter().one.return_value = 'exist_uuid'
        testUUID = Work.getByUUID(mock_session, 'uuid')
        self.assertEqual(testUUID, 'exist_uuid')
    
    @patch('sfrCore.model.work.uuid.UUID', return_value='test_uuid')
    def test_get_by_uuid_missing(self, mock_uuid):
        mock_session = MagicMock()
        mock_session.query().filter().one.side_effect = NoResultFound
        with self.assertRaises(DBError):
            Work.getByUUID(mock_session, 'uuid')
    
    def test_create_agent_work(self):
        testRec = AgentWorks(role='tester')
        testRec.work_id = 1
        testRec.agent_id = 1
        self.assertEqual(str(testRec), '<AgentWorks(work=1, agent=1, role=tester)>')
    
    def test_role_exists(self):
        mock_session = MagicMock()
        mock_session.query().filter().filter().filter().one_or_none.return_value = 'test_role'
        mock_agent = MagicMock()
        mock_agent.id = 1
        role = AgentWorks.roleExists(mock_session, mock_agent, 'role', 1)
        self.assertEqual(role, 'test_role')

    # Special test case to ensure that dates are handled properly
    def test_date_backref(self):
        testWork = Work()
        tDate = DateField.insert({
            'id': 1,
            'display_date': 'January 1, 2019',
            'date_range': '2019-01-01',
            'date_type': 'test'
        })
        testWork.dates.add(tDate)
        self.assertIsInstance(testWork, Work)
        self.assertEqual(len(testWork.dates), 1)
        self.assertEqual(list(testWork.dates)[0].date_range, '[2019-01-01,)')
