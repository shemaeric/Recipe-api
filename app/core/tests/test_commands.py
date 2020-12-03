from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase

class CommandTests(TestCase):

    def test_waiting_for_db_to_start(self):
        """Test waiting for db to start"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')

            self.assertEqual(gi.call_count, 1)

    # Mock and remove the time it takes to ping the database
    @patch('time.sleep', return_value = True)
    def test_wait_for_db(self, ts):
        """Waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')

            self.assertEqual(gi.call_count, 6)
