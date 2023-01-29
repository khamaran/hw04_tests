from django.test import TestCase


class ViewTestClass(TestCase):
    def test_page_not_found(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)

    def test_page_not_found_uses_correct_template(self):
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
