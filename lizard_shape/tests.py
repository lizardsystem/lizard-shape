# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
from django.test.client import Client

import lizard_shape.layers
from lizard_shape.admin import check_extension_or_error
from lizard_shape.layers import AdapterShapefile
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


class AdminTest(TestCase):

    def test_check_extension(self):
        """
        Checks filename with correct absolute filename.
        """
        filename = '/home/jack/shapefile.shp'
        check_extension_or_error(filename, 'shp')
        check_extension_or_error(filename, 'shp', extension_name='Shapefile')

    def test_check_extension2(self):
        """
        Checks filename with correct relative filename.
        """
        filename = 'shapefile.shp'
        check_extension_or_error(filename, 'shp')
        check_extension_or_error(filename, 'shp', extension_name='Shapefile')

    def test_check_extension_error(self):
        """
        Checks if an error is raised in case of an error.
        """
        filename = '/home/jack/shapefile.shx'
        self.assertRaises(
            ValidationError, check_extension_or_error, filename, 'shp')
        self.assertRaises(
            ValidationError, check_extension_or_error, filename, 'shp',
            extension_name='Shapefile')


class AdapterShapefileTestSuite(TestCase):
    """WMS layer functions are generally defined in layers.py. One can add his
    own in other apps. shapefile_layer is an example function.
    """

    def test_initialization(self):
        mock_workspace = None
        layer_arguments = {
            'layer_name': 'Waterlichamen',
            'resource_module': 'lizard_map',
            'resource_name': 'test_shapefiles/KRWwaterlichamen_merge.shp',
            'search_property_name': 'WGBNAAM'}
        ws_adapter = lizard_shape.layers.AdapterShapefile(
            mock_workspace, layer_arguments=layer_arguments)
        layers, styles = ws_adapter.layer()
        # TODO: test output.

    def test_b(self):
        """Test the layer info is initialized with the given parameters.

        Note: the resource_module must exist.
        """

        workspace_item = 0  # don't care for this test
        arguments = {'layer_name': 'Layer name',
                     'resource_module': 'lizard_map',
                     'resource_name': 'Resource name',
                     'search_property_name': 'Search property name'}

        adapter = AdapterShapefile(workspace_item,
                                   layer_arguments=arguments)

        self.assertEqual(adapter.layer_name, 'Layer name')
        self.assertEqual(adapter.resource_module, 'lizard_map')
        self.assertEqual(adapter.resource_name, 'Resource name')
        self.assertEqual(adapter.search_property_name, 'Search property name')

