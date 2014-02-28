# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from lizard_map.mapnik_helper import point_rule
from lizard_map.fields import ColorField
from lizard_map.models import Legend
from lizard_map.models import LegendPoint
#from nens.sobek import HISFile
from treebeard.al_tree import AL_Node
import mapnik

# The default location from MEDIA_ROOT to upload files to.
UPLOAD_TO = "lizard_shape/shapes"
UPLOAD_HIS = "lizard_shape/his"

logger = logging.getLogger(__name__)


class ShapeNameError(Exception):
    pass


class Shape(models.Model):
    """
    Here you can upload your shapefiles: .dbf, .prj, .shp, .shx
    files. Select a shape template and you got your shapefile layout.
    """

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=20, unique=True)
    description = models.TextField(null=True, blank=True)

    shp_file = models.FileField(upload_to=UPLOAD_TO)
    dbf_file = models.FileField(upload_to=UPLOAD_TO)
    shx_file = models.FileField(upload_to=UPLOAD_TO)
    prj_file = models.FileField(upload_to=UPLOAD_TO)

    prj = models.TextField(
        help_text=u'Auto-filled when saving model.')

    his = models.ForeignKey('His', null=True, blank=True)
    his_parameter = models.CharField(
        max_length=80, null=True, blank=True,
        help_text=u'i.e. Discharge max (m\xb3/s)')

    template = models.ForeignKey('ShapeTemplate')

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.slug)

    def save(self, *args, **kwargs):
        """Check if constraints are met before saving model.

        Also read contents of prj_file and put it in field prj.
        """
        shp_first = self.shp_file.name.rpartition('.')
        dbf_first = self.dbf_file.name.rpartition('.')
        shx_first = self.shx_file.name.rpartition('.')
        prj_first = self.prj_file.name.rpartition('.')

        try:
            self.prj = self.prj_file.file.read()  # fill prj field
        except IOError:
            self.prj = 'Could not read .prj file %s' % self.prj_file.name
            logger.exception(
                'Could not read .prj file %s' % self.prj_file.name)
            # TODO: inform user? It does not raise an error now
            # because I needed a development environment with Shape
            # objects, without the actual files.

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

    def timeseries(self, location_name, start=None, end=None):
        """
        Returns timeseries from hisfile in a dict associating
        timestamp to value. Returns [] if no hisfile defined.
        """
        if False and self.his and self.his_parameter:
            hf = self.his.hisfile()
            return hf.get_timeseries(
                location_name, self.his_parameter, start=start, end=end)
        return []


class ShapeTemplate(models.Model):
    """
    A shape template contains fieldnames. It also has configured
    legends and fields referenced to it. Create a template once and
    use it many times in shapes.
    """

    name = models.CharField(
        max_length=80,
        help_text='Display name.',
        unique=True)
    id_field = models.CharField(
        max_length=20, null=True, blank=True,
        help_text='The id field must be filled for searching and his files.')
    name_field = models.CharField(
        max_length=20, null=True, blank=True,
        help_text='The name field must be filled for mouseovers, popups.')

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        try:
            return '%s' % self.name
        except:
            return '(not displayable)'


class ShapeField(models.Model):
    """
    Which fields do we want to display in a popup? Used by adapter in
    lizard-map.
    """
    FIELD_TYPE_NORMAL = 1
    FIELD_TYPE_LINK_IMAGE = 2
    FIELD_TYPE_WEBLINK = 3

    FIELD_TYPE_CHOICES = (
        (FIELD_TYPE_NORMAL, _('normal')),
        (FIELD_TYPE_LINK_IMAGE, _('link to image')),
        (FIELD_TYPE_WEBLINK, _('weblink')),
        )

    name = models.CharField(max_length=80)
    field = models.CharField(max_length=20)
    field_type = models.IntegerField(
        choices=FIELD_TYPE_CHOICES,
        default=FIELD_TYPE_NORMAL)
    index = models.IntegerField(default=1000)

    shape_template = models.ForeignKey('ShapeTemplate')

    class Meta:
        ordering = ('index', )

    def __unicode__(self):
        # Only add the dash if both self.shape_template and self.name exist,
        # otherwise just show the one that does
        return u' - '.join(unicode(s) for s in (self.shape_template, self.name)
                           if s)


class Category(AL_Node):
    """
    Tree structure for ordering objects.

    Optionally connect shapes to nodes.
    """

    name = models.CharField(
        max_length=80,
        help_text='i.e. max debiet.')
    slug = models.SlugField(
        max_length=20, unique=True)
    parent = models.ForeignKey(
        'Category', null=True, blank=True)
    index = models.IntegerField(default=1000)

    # For treebeard.
    node_order_by = ['index', 'name']

    shapes = models.ManyToManyField('Shape', null=True, blank=True)

    class Meta:
        ordering = ('index', 'name')

    def save(self, *args, **kwargs):
        if self.parent_id and self.parent_id == self.pk:
            raise ValidationError("Parent field points at itself.")
        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.parent is None:
            return u'%s' % self.name
        else:
            return ' -> '.join([unicode(self.parent), self.name])


class ShapeLegend(Legend):
    """
    Legend for shapefile:
    - Which field to use for value?
    """

    shape_template = models.ForeignKey('ShapeTemplate')
    value_field = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s - %s' % (self.shape_template, self.descriptor)

    def adapter_layer_json(self, shape):
        """
        Defines adapter_layer_json for adapter_shapefile (from
        lizard-map).
        """
        id_field = (self.shape_template.id_field
                    if self.shape_template.id_field else "")
        name_field = (self.shape_template.name_field
                      if self.shape_template.name_field else "")
        display_fields = [{'name': sf.name, 'field': sf.field}
                          for sf in self.shape_template.shapefield_set.all()]
        result = ((
                '{"layer_name": "%s", '
                '"legend_id": "%d", '
                '"legend_type": "ShapeLegend", '
                '"value_field": "%s", '
                '"value_name": "%s", '
                '"layer_filename": "%s", '
                '"search_property_id": "%s", '
                '"search_property_name": "%s", '
                '"shape_id": "%d", '
                '"display_fields": %s}') % (
                str(self),
                self.id,
                self.value_field,
                self.descriptor,
                shape.shp_file.path,
                id_field,
                name_field,
                shape.id,
                json.dumps(display_fields)))
        return result


class ShapeLegendPoint(LegendPoint):
    """
    Legend for point shapefile.
    """

    shape_template = models.ForeignKey(
        'ShapeTemplate',
        help_text='Select a shape template for visualization.')
    value_field = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s - %s' % (self.shape_template, self.descriptor)

    def adapter_layer_json(self, shape):
        """
        Defines adapter_layer_json for adapter_shapefile (from
        lizard-map).
        """
        id_field = (self.shape_template.id_field
                    if self.shape_template.id_field else "")
        name_field = (self.shape_template.name_field
                      if self.shape_template.name_field else "")
        display_fields = [{'name': sf.name, 'field': sf.field}
                          for sf in self.shape_template.shapefield_set.all()]
        result = ((
                '{"layer_name": "%s", '
                '"legend_id": "%d", '
                '"legend_type": "ShapeLegendPoint", '
                '"value_field": "%s", '
                '"value_name": "%s", '
                '"layer_filename": "%s", '
                '"search_property_id": "%s", '
                '"search_property_name": "%s", '
                '"shape_id": "%d", '
                '"display_fields": %s}') % (
                str(self),
                self.id,
                self.value_field,
                self.descriptor,
                shape.shp_file.path,
                id_field,
                name_field,
                shape.id,
                json.dumps(display_fields)))
        return result


class ShapeLegendClass(models.Model):
    """
    Legend for classes.
    """

    descriptor = models.CharField(max_length=80)
    shape_template = models.ForeignKey(
        'ShapeTemplate',
        help_text='Select a shape template for visualization.')
    value_field = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s' % (self.descriptor)

    def adapter_layer_json(self, shape):
        id_field = (self.shape_template.id_field
                    if self.shape_template.id_field else "")
        name_field = (self.shape_template.name_field
                      if self.shape_template.name_field else "")
        display_fields = [{'name': sf.name,
                           'field': sf.field,
                           'field_type': sf.field_type}
                          for sf in self.shape_template.shapefield_set.all()]
        result = json.dumps({
                'layer_name': str(self),
                'legend_type': 'ShapeLegendClass',
                'legend_id': self.id,
                'shape_id': shape.id,
                'display_fields': display_fields,
                'value_field': self.value_field,
                'value_name': self.descriptor,
                'layer_filename': shape.shp_file.path,
                'search_property_id': id_field,
                'search_property_name': name_field,
                })
        return result

    def mapnik_style(self, value_field=None):
        """
        Generates mapnik style from this object.
        """
        if value_field is None:
            value_field = 'value'
        style = mapnik.Style()
        classes = self.shapelegendsingleclass_set.all()

        # Add a rule for each class
        for c in classes:
            layout_rule = mapnik.Rule()
            if c.color_inside:
                area_looks = mapnik.PolygonSymbolizer(
                    mapnik.Color('#' + c.color_inside))
                area_looks.fill_opacity = 0.5
                layout_rule.symbols.append(area_looks)
                logger.debug('adding polygon symbolizer')
            if c.color:
                line_looks = mapnik.LineSymbolizer(
                    mapnik.Color('#' + c.color), c.size)
                layout_rule.symbols.append(line_looks)
                logger.debug('adding line symbolizer')
            mapnik_filter = None
            if c.is_exact or c.min_value and c.min_value == c.max_value:
                # Check if c.min_value is parsable as float. Yes:
                # compare like float.
                try:
                    float(c.min_value)
                    mapnik_filter = str("[%s] = %s" % (
                            value_field, c.min_value))
                except ValueError:
                    mapnik_filter = str("[%s] = '%s'" % (
                            value_field, c.min_value))
            else:
                if c.min_value and c.max_value:
                    mapnik_filter = str("[%s] >= %s and [%s] < %s"
                                        % (value_field,
                                           c.min_value,
                                           value_field,
                                           c.max_value))
                elif c.min_value and not c.max_value:
                    mapnik_filter = str("[%s] >= %s"
                                        % (value_field,
                                           c.min_value))
                elif not c.min_value and c.max_value:
                    mapnik_filter = str("[%s] < %s"
                                        % (value_field,
                                           c.max_value))
            if mapnik_filter is not None:
                logger.debug('adding mapnik_filter: %s' % mapnik_filter)
                layout_rule.filter = mapnik.Filter(mapnik_filter)

            style.rules.append(layout_rule)

            # Add icon rule, if applicable.
            if c.icon:
                style.rules.append(
                    point_rule(c.icon, c.mask,
                               c.color, mapnik_filter))

        return style

    def icon_style(self):
        icon = 'polygon.png'
        color = (1.0, 1.0, 1.0, 1.0)
        try:
            singleclass = self.shapelegendsingleclass_set.all()[0]
            if singleclass.color:
                color = singleclass.color.to_tuple()
            if singleclass.icon:
                icon = singleclass.icon
        except IndexError:
            # Do nothing, everything has its default value.
            pass
        return {'icon': icon,
                'mask': ('empty_mask.png', ),
                'color': color}


class ShapeLegendSingleClass(models.Model):
    """
    Single entry for ShapeLegendClasses.

    if is_exact == True, only the min_value will be taken.

    if is_exact == False:
    - if min_value is omitted, it is considered a lower boundary
    - if max_value is omitted, it is considered a upper boundary
    - thus, if both are omitted, it is considered a default value,

    If icon is omitted, the entry is considered a line or area.

    Size is:
    - the linewidth in case of a line
    - the border width in case of an area (TODO)
    - the relative size in case of an icon (TODO)

    color can be omitted for areas where the inside has a color.
    color_inside is used for areas only.

    TODO: if icon is used, mask must be filled in too.
    """

    shape_legend_class = models.ForeignKey('ShapeLegendClass')

    label = models.CharField(
        max_length=200, null=True, blank=True,
        help_text="Fill in if you want a custom label.")

    min_value = models.CharField(max_length=80, null=True, blank=True)
    max_value = models.CharField(max_length=80, null=True, blank=True)

    is_exact = models.BooleanField(default=False)

    color = ColorField(null=True, blank=True)
    color_inside = ColorField(null=True, blank=True)
    size = models.FloatField(default=1.0)
    icon = models.CharField(max_length=80, null=True, blank=True)
    mask = models.CharField(max_length=80, null=True, blank=True)

    # Determines the order of rows.
    index = models.IntegerField(default=100)

    class Meta:
        ordering = ('index', )

    def legend_color(self):
        """Returns a color_iside if not color."""
        if self.color_inside:
            return self.color_inside
        else:
            return self.color

    def __unicode__(self):
        if self.is_exact:
            return '%s: %s - %s' % (
                self.shape_legend_class,
                self.min_value,
                self.legend_color())
        else:
            return '%s: (%s, %s) - %s' % (
                self.shape_legend_class,
                self.min_value,
                self.max_value,
                self.legend_color())


class His(models.Model):
    """
    Sobek HIS files and their relation to a shapefile.
    """

    name = models.CharField(max_length=80,
                            help_text='Display name.')
    filename = models.FileField(upload_to=UPLOAD_HIS)

    def __unicode__(self):
        return '%s' % self.name

    def hisfile(self):
        result = HISFile(self.filename.path)
        return result
