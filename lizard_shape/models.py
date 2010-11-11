# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models
from django.utils import simplejson as json

from treebeard.al_tree import AL_Node

from lizard_map.models import Legend
from lizard_map.models import LegendPoint

# The default location from MEDIA_ROOT to upload files to.
UPLOAD_TO = "lizard_shape/shapes"


class ShapeNameError(Exception):
    pass


class Shape(models.Model):
    """
    Here you can upload your shapefiles: .dbf, .prj, .shp, .shx files
    """

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=20, unique=True)
    description = models.TextField(null=True, blank=True)

    shp_file = models.FileField(upload_to=UPLOAD_TO)
    dbf_file = models.FileField(upload_to=UPLOAD_TO)
    shx_file = models.FileField(upload_to=UPLOAD_TO)
    prj_file = models.FileField(upload_to=UPLOAD_TO)

    id_field = models.CharField(
        max_length=20, null=True, blank=True,
        help_text='The id field must be filled for searching.')
    name_field = models.CharField(
        max_length=20, null=True, blank=True,
        help_text='The name field must be filled for mouseovers, popups.')

    legend = models.ManyToManyField(Legend, through='ShapeLegend',
                                    null=True, blank=True)

    def __unicode__(self):
        return '%s' % self.name

    def save(self, *args, **kwargs):
        """Check if constraints are met before saving model."""
        shp_first = self.shp_file.name.rpartition('.')
        dbf_first = self.dbf_file.name.rpartition('.')
        shx_first = self.shx_file.name.rpartition('.')
        prj_first = self.prj_file.name.rpartition('.')

        if shp_first[-1] != 'shp':
            raise ShapeNameError(
                "Uploaded shp_file doest not have extension .shp.")
        if dbf_first[-1] != 'dbf':
            raise ShapeNameError(
                "Uploaded dbf_file doest not have extension .dbf.")
        if shx_first[-1] != 'shx':
            raise ShapeNameError(
                "Uploaded shx_file doest not have extension .shx.")
        if prj_first[-1] != 'prj':
            raise ShapeNameError(
                "Uploaded prj_file doest not have extension .prj.")

        if shp_first[0] == dbf_first[0] == shx_first[0] == prj_first[0]:
            super(Shape, self).save(*args, **kwargs)
        else:
            raise ShapeNameError(
                "Uploaded files do not have common filename base.")

    def get_adapter_layer_json_list(self):
        """
        Calculates all adapter_layer_jsons from available legends and
        return in list.
        """
        result = []
        # Add all shapelegends.
        result.extend([s.adapter_layer_json
                       for s in self.shapelegend_set.all()])
        # Add all shapelegendspoints.
        result.extend([s.adapter_layer_json
                       for s in self.shapelegendpoint_set.all()])
        return result


class ShapeField(models.Model):
    """
    Which fields do we want to display in a popup? Used by adapter in
    lizard-map.
    """
    name = models.CharField(max_length=80)
    field = models.CharField(max_length=20)

    shape = models.ForeignKey('Shape')

    def __unicode__(self):
        return u'%s - %s' % (self.shape, self.name)


class Category(AL_Node):
    """
    Tree structure for ordering objects.

    Optionally connect shapes to nodes.
    """

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=20, unique=True)
    parent = models.ForeignKey('Category', null=True, blank=True)

    # For treebeard.
    node_order_by = ['name']

    shapes = models.ManyToManyField('Shape', null=True, blank=True)

    def __unicode__(self):
        return '%s' % self.name


class ShapeLegend(models.Model):
    """
    Legend for shapefile:
    - Which field to use for value?
    """

    name = models.CharField(max_length=80)
    shape = models.ForeignKey(Shape)
    legend = models.ForeignKey(Legend)
    value_field = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s - %s' % (self.shape, self.name)

    @property
    def adapter_layer_json(self):
        """
        Defines adapter_layer_json for adapter_shapefile (from
        lizard-map).
        """
        id_field = (self.shape.id_field
                    if self.shape.id_field else "")
        name_field = (self.shape.name_field
                      if self.shape.name_field else "")
        display_fields = [{'name': sf.name, 'field': sf.field}
                          for sf in self.shape.shapefield_set.all()]
        result = ((
                '{"layer_name": "%s", '
                '"legend_id": "%d", '
                '"value_field": "%s", '
                '"value_name": "%s", '
                '"layer_filename": "%s", '
                '"search_property_id": "%s", '
                '"search_property_name": "%s", '
                '"display_fields": %s}') % (
                str(self),
                self.legend.id,
                self.value_field,
                self.name,
                self.shape.shp_file.path,
                id_field,
                name_field,
                json.dumps(display_fields)))
        return result


class ShapeLegendPoint(models.Model):
    """
    Legend for point shapefile.
    """

    name = models.CharField(max_length=80)
    shape = models.ForeignKey(Shape)
    legend_point = models.ForeignKey(LegendPoint)
    value_field = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s - %s' % (self.shape, self.name)

    @property
    def adapter_layer_json(self):
        """
        Defines adapter_layer_json for adapter_shapefile (from
        lizard-map).
        """
        id_field = (self.shape.id_field
                    if self.shape.id_field else "")
        name_field = (self.shape.name_field
                      if self.shape.name_field else "")
        display_fields = [{'name': sf.name, 'field': sf.field}
                          for sf in self.shape.shapefield_set.all()]
        result = ((
                '{"layer_name": "%s", '
                '"legend_point_id": "%d", '
                '"value_field": "%s", '
                '"value_name": "%s", '
                '"layer_filename": "%s", '
                '"search_property_id": "%s", '
                '"search_property_name": "%s", '
                '"display_fields": %s}') % (
                str(self),
                self.legend_point.id,
                self.value_field,
                self.name,
                self.shape.shp_file.path,
                id_field,
                name_field,
                json.dumps(display_fields)))
        return result
