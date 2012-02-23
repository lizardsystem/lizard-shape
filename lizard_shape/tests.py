# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import datetime

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
from django.test.client import Client
import pkg_resources

import lizard_shape.layers
from lizard_shape.admin import check_extension_or_error
from lizard_shape.layers import AdapterShapefile
from lizard_shape.layers import LEGEND_TYPE_SHAPELEGENDCLASS
from lizard_shape.models import Category
from lizard_shape.models import Shape
from lizard_shape.models import ShapeLegend
from lizard_shape.models import ShapeLegendClass
from lizard_shape.models import ShapeLegendPoint
from lizard_shape.models import ShapeTemplate
from lizard_shape.models import ShapeNameError


class IntegrationTest(TestCase):
    fixtures = ['lizard_shape_test']

    def test_homepage(self):
        c = Client()
        url = reverse('lizard_shape.homepage')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_shape_legend_class(self):
        """
        How to add shape legend class. This is de default legend type.
        """
        s = Shape.objects.all()[0]  # Just take first shape
        s.template.shapelegendclass_set.create(
            descriptor='_test legend',
            value_field='test_field')

    # def test_shape_legend(self):
    #     """
    #     How to add shape legend.
    #     """
    #     s = Shape.objects.all()[0]  # Just take first shape
    #     s.template.shapelegend_set.create(
    #         descriptor='_test legend',
    #         default_color='ffffff',
    #         min_color='ffffff',
    #         max_color='ffffff',
    #         too_low_color='ffffff',
    #         too_high_color='ffffff',
    #         value_field='test_field')

    def test_shape_legend_point(self):
        """
        How to add shape legend point.
        """
        s = Shape.objects.all()[0]  # Just take first shape
        s.template.shapelegendpoint_set.create(
            descriptor='_test legend',
            default_color='ffffff',
            min_color='ffffff',
            max_color='ffffff',
            too_low_color='ffffff',
            too_high_color='ffffff',
            value_field='test_field')


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

    def test_no_infinite_recursion_in_unicode(self):
        """Pointing a category's parent field at itself would give an infinite
        recursion error in __unicode__().
        """
        category = Category(
            name='root', slug='root')
        category.save()
        category.parent = category
        self.assertRaises(ValidationError, category.save)


class ModelShapeTest(TestCase):
    fixtures = ['lizard_shape_test']

    def setUp(self):
        """
        One can make a shape template. The shape template contains
        fields for id, name and legend info.
        """
        self.shape = Shape.objects.all()[0]
        self.shape_template = ShapeTemplate(
            name='test_template',
            id_field='mock_id_field',
            name_field='mock_name_field')
        self.shape_template.save()

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

    def test_timeseries(self):
        """
        There is not his-file associated with the shape.
        """
        self.assertEquals(self.shape.timeseries('asdf'), [])

    def test_shapelegend(self):
        """
        Make a shape legend.
        """
        shape_legend = ShapeLegend(
            shape_template=self.shape_template,
            value_field='mock_value_field')
        shape_legend.save()  # MUST use a saved shape_legend.
        shape_legend.adapter_layer_json(self.shape)

    def test_shapelegendpoint(self):
        """
        Make a shape legend.
        """
        shape_legend_point = ShapeLegendPoint(
            shape_template=self.shape_template,
            value_field='mock_value_field')
        shape_legend_point.save()  # MUST use a saved shape_legend.
        shape_legend_point.adapter_layer_json(self.shape)

    def test_shapelegendclass_mapnik(self):
        """
        Test mapnik output of shapelegendclass
        """
        slc = ShapeLegendClass.objects.all()[0]
        slc.mapnik_style()


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
    """WMS layer functions are generally defined in layers.py. One can
    add his own in other apps.

    There are 3 ways to define a shapefile:
    - Using a shape_id which refers to lizard_shape.models.Shape
    - Using resource_module and resource_name.
    - Using the layer_argument layer_filename.
    """
    fixtures = ['lizard_shape_test', ]

    def setUp(self):
        """Set up the following variables:

        - resource_module
        - resource_name
        - layer_filename
        - noext (=layer_filename without extension)
        - shape
        - adapter
        """

        self.resource_module = 'lizard_map'
        self.resource_name = 'test_shapefiles/KRWwaterlichamen_merge'
        self.layer_filename = pkg_resources.resource_filename(
            self.resource_module, self.resource_name + '.shp')
        self.noext = pkg_resources.resource_filename(
            self.resource_module, self.resource_name)

        # Upload files for shape with id=1 so that it points to a
        # valid shapefile
        self.shape = Shape.objects.get(pk=1)

        content = ContentFile(open(self.noext + '.shp').read())
        self.shape.shp_file.save(self.noext + '.shp', content, save=False)
        content = ContentFile(open(self.noext + '.dbf').read())
        self.shape.dbf_file.save(self.noext + '.dbf', content, save=False)
        content = ContentFile(open(self.noext + '.shx').read())
        self.shape.shx_file.save(self.noext + '.shx', content, save=False)
        content = ContentFile(open(self.noext + '.prj').read())
        self.shape.prj_file.save(self.noext + '.prj', content, save=False)

        self.shape.save()

        # Now make the adapter.
        mock_workspace = None
        layer_arguments = {
            'layer_name': 'Waterlichamen',
            'shape_id': 1,
            'search_property_name': 'OWANAAM',
            'search_property_id': 'OWAIDENT',
            'value_field': 'OWANAAM',
            'legend_id': 1,
            'legend_type': LEGEND_TYPE_SHAPELEGENDCLASS}
        self.adapter = lizard_shape.layers.AdapterShapefile(
            mock_workspace, layer_arguments=layer_arguments)

    def tearDown(self):
        # Ensures deletion of uploaded files.
        self.shape.delete()

    def test_initialization1(self):
        """Init using shape_id - the shapefile is in
        var/media/lizard_shape/shapes/..."""
        layers, styles = self.adapter.layer()

    def test_initialization2(self):
        """Init using resource_module and resource_name"""
        mock_workspace = None
        layer_arguments = {
            'layer_name': 'Waterlichamen',
            'resource_module': self.resource_module,
            'resource_name': self.resource_name + '.shp',
            'search_property_name': 'OWANAAM'}
        ws_adapter = lizard_shape.layers.AdapterShapefile(
            mock_workspace, layer_arguments=layer_arguments)
        layers, styles = ws_adapter.layer()
        # TODO: test output.

    def test_initialization3(self):
        """Init using layer_filename"""
        mock_workspace = None
        layer_arguments = {
            'layer_name': 'Waterlichamen',
            'layer_filename': self.layer_filename,
            'search_property_name': 'OWANAAM'}
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

    def test_legend(self):
        result = self.adapter.legend()
        self.assertEquals(len(result), 2)

    def test_search(self):
        """
        Searches on coordinate. On these coordinates there should only
        be one result: Kortenhoefse plasen.
        """
        result = self.adapter.search(567427.0, 6841286.0, 2000.0)
        self.assertEquals(result[0]['identifier']['id'], 'NL11_6_4')

    def test_symbol_url(self):
        url = self.adapter.symbol_url()
        self.assertTrue('.png' in url)

    def test_location(self):
        result = self.adapter.location('NL11_6_4')
        self.assertEquals(result['identifier']['id'], 'NL11_6_4')

    def test_html(self):
        """Tests html output"""

        # Does it crash?
        self.adapter.html(identifiers=[{'id': 'NL11_6_4'}])

    def test_image(self):
        """
        Tests if image will be generated.
        """
        # Only works if his file is present. Otherwise you get an
        # empty graph.
        start_date = datetime.date(2009, 1, 1)
        end_date = datetime.date(2010, 1, 1)
        self.adapter.image([{'id': 'NL11_6_4'}], start_date, end_date)

    def test_extent(self):
        """
        Tests extent.
        """
        result = self.adapter.extent()
        self.assertTrue('north' in result)
        self.assertTrue('south' in result)
        self.assertTrue('east' in result)
        self.assertTrue('west' in result)
