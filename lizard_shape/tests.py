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
