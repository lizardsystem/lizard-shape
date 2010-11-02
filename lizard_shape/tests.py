# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase
from django.test.client import Client

from lizard_shape.models import Category
from lizard_shape.models import Shape
from lizard_shape.models import ShapeNameError


class IntegrationTest(TestCase):
    fixtures = ['lizard_shape_test']

    def test_homepage(self):
        c = Client()
        url = reverse('lizard_shape.homepage')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)


class ModelsTest(TestCase):

    def test_category(self):
        """Adding parents and childs.
        """
        root_category = Category(
            name='root', slug='root')
        root_category.save()
        child_category = Category(
            name='child',
            slug='child',
            parent=root_category)
        child_category.save()
        children = root_category.get_children()
        self.assertEquals(len(children), 1)
        self.assertEquals(str(children[0]), str(child_category))

    def test_category2(self):
        """Slugs are unique.
        """
        root_category = Category(
            name='root', slug='root')
        root_category.save()
        second_root_category = Category(
            name='root', slug='root')
        self.assertRaises(IntegrityError, second_root_category.save)


class ModelShapeTest(TestCase):
    fixtures = ['lizard_shape_test']

    def setUp(self):
        self.shape = Shape.objects.all()[0]

    def test_shape(self):
        """
        The fixture has a correctly defined Shape object.
        """
        self.shape.save()

    def test_shape2(self):
        """
        Check if wrong extension would allow you to save.
        """
        self.shape.shp_file.name = 'oeloebloe.txt'
        self.assertRaises(ShapeNameError, self.shape.save)

    def test_shape3(self):
        """
        Check if wrong extension would allow you to save.
        """
        self.shape.dbf_file.name = 'oeloebloe.txt'
        self.assertRaises(ShapeNameError, self.shape.save)

    def test_shape4(self):
        """
        Check if wrong extension would allow you to save.
        """
        self.shape.shx_file.name = 'oeloebloe.txt'
        self.assertRaises(ShapeNameError, self.shape.save)

    def test_shape5(self):
        """
        Check if wrong extension would allow you to save.
        """
        self.shape.prj_file.name = 'oeloebloe.txt'
        self.assertRaises(ShapeNameError, self.shape.save)

    def test_shape6(self):
        """
        Check if inconsistent filenames would allow you to save.
        """
        self.shape.shp_file.name = 'oeloebloe.shp'
        self.assertRaises(ShapeNameError, self.shape.save)
