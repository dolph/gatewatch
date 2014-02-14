import unittest

import pasteraw


class OpenStackHUDTestCase(unittest.TestCase):
    def setUp(self):
        pasteraw.app.config['TESTING'] = True
        pasteraw.app.config['CSRF_ENABLED'] = False
        self.app = pasteraw.app.test_client()

    def tearDown(self):
        pass

    def test_favicon(self):
        r = self.app.get('/favicon.ico')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content_type, 'image/x-icon')
        self.assertIn('public', r.cache_control)

    def test_static_favicon(self):
        r = self.app.get('/static/favicon.ico')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content_type, 'image/x-icon')
        self.assertIn('public', r.cache_control)

    def test_index(self):
        self.app.get('/')


if __name__ == '__main__':
    unittest.main()
