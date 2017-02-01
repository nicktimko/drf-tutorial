import io
import json

from django.test import TestCase
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient

from .models import Snippet
from .serializers import SnippetSerializer


class SnippetObject(TestCase):
    def test_creation(self):
        snippet = Snippet(code='foo = "bar"\n')
        snippet.save()

        snippet2 = Snippet(code='print "hello, world"\n')
        snippet2.save()

        self.assertEqual(Snippet.objects.count(), 2)


class SnippetSerializing(TestCase):
    def test_serial(self):
        snippet = Snippet(code='foo = "bar"\n')
        serializer = SnippetSerializer(snippet)
        serialized = JSONRenderer().render(serializer.data)

        try:
            json.loads(serialized)
        except ValueError:
            self.fail("Serializer produced invalid JSON")

    def test_deserial(self):
        content = json.dumps({
            'code': 'print("hello world!")',
        })
        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)

        serializer = SnippetSerializer(data=data)
        assert serializer.is_valid()
        assert 'code' in serializer.validated_data


class SnippetList(TestCase):
    def setUp(self):
        self.client = APIClient()
        snip1 = Snippet.objects.create(code='print("hello world!")')

    def test_get_list(self):
        response = self.client.get('/snippets/')
        data = response.json()
        self.assertEqual(1, len(data))
        self.assertEqual(200, response.status_code)


class SnippetGet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.snip1 = Snippet.objects.create(code='print("hello world!")')

    def test_get_one(self):
        response = self.client.get(
            '/snippets/{}/'.format(self.snip1.id)
        )
        self.assertEqual(200, response.status_code)
        snip = response.json()
        self.assertEqual(self.snip1.code, snip['code'])

    def test_get_missing(self):
        response = self.client.get('/snippets/40404040404/')
        self.assertEqual(404, response.status_code)


class SnippetCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_form_post(self):
        response = self.client.post(
            '/snippets/',
            data={
                'code': '#include <stdio.h>',
                'language': 'c',
            },
        )
        c_stuff = response.json()
        self.assertEqual(201, response.status_code)

    def test_json_post(self):
        response = self.client.post(
            '/snippets/',
            content_type='application/json',
            data=json.dumps({
                'code': '#include <stdio.h>',
                'language': 'c',
            }),
        )
        c_stuff = response.json()
        self.assertEqual(201, response.status_code)

    def test_reject_empty(self):
        response = self.client.post(
            '/snippets/',
            content_type='application/json',
            data=json.dumps({}),
        )
        self.assertEqual(400, response.status_code)

    def test_reject_missing_code(self):
        response = self.client.post(
            '/snippets/',
            content_type='application/json',
            data=json.dumps({
                # 'code': 'asdf',
                'bode': 'zxcv',
                'mode': 'qwer',
            }),
        )
        self.assertEqual(400, response.status_code)


class SnippetDelete(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.snip1 = Snippet.objects.create(code='print("hello world!")')

    def test_delete(self):
        nstart = Snippet.objects.count()
        response = self.client.delete(
            '/snippets/{}/'.format(self.snip1.id),
        )
        nend = Snippet.objects.count()
        self.assertEqual(204, response.status_code)
        self.assertEqual(nstart - nend, 1)


class SnippetUpdate(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.snip1 = Snippet.objects.create(code='print("hello world!")')

    def test_update(self):
        response = self.client.put(
            '/snippets/{}/'.format(self.snip1.id),
            content_type='application/json',
            data=json.dumps({
                'code': 'print("hello update!")'
            }),
        )
        self.assertEqual(200, response.status_code)
        snip = response.json()
        assert 'update' in snip['code']
