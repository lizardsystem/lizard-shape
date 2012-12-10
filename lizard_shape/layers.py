from pyproj import Proj
from pyproj import transform
from shapely.geometry import Point
from shapely.wkt import loads
import datetime
import logging
import mapnik
import osgeo.ogr
import pkg_resources

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import simplejson as json

from lizard_map.adapter import Graph
from lizard_map.coordinates import detect_prj
from lizard_map.coordinates import google_projection
from lizard_map.models import WorkspaceItemError
from lizard_map.utility import float_to_string
from lizard_map.workspace import WorkspaceItemAdapter
from lizard_shape.models import Shape
from lizard_shape.models import ShapeField
from lizard_shape.models import ShapeLegend
from lizard_shape.models import ShapeLegendClass
from lizard_shape.models import ShapeLegendPoint

logger = logging.getLogger(__name__)

MAX_SEARCH_RESULTS = 3
LEGEND_TYPE_SHAPELEGEND = 'ShapeLegend'
LEGEND_TYPE_SHAPELEGENDCLASS = 'ShapeLegendClass'
LEGEND_TYPE_SHAPELEGENDPOINT = 'ShapeLegendPoint'


class AdapterShapefile(WorkspaceItemAdapter):
    """Render a WorkspaceItem using a shape file. Registered as
    'adapter_shapefile'

    Instance variables:
    * layer_name -- name of the WorkspaceItem that is rendered

    * search_property_name (optional) -- name of shapefile feature
      used in search results: mouse over, title of popup

    * search_property_id (optional) -- id of shapefile feature. Used
      to find the feature back.

    * value_field (optional, used by legend) -- value field for legend
      (takes 'value' if not given)

    * value_name (optional) -- name for value field

    * display_fields (optional) -- list of which columns to
      show in a popup.

    Legend:
    * legend_id (optional, preferenced) -- id of legend (linestyle)
    OR
    * legend_point_id (optional) -- id of legend_point_id (points)
    ELSE it takes default legend

    Shapefile:
    * layer_filename -- absolute path to shapefile
    OR
    * resource_module -- module that contains the shapefile resource
    * resource name -- name of the shapefile resource

    * shape_id OR shape_slug -- required by image function, or it will
      output an empty graph. If both shape_id and shape_slug, then it
      will take shape_slug.

    """
    def __init__(self, *args, **kwargs):
        """Store the name and location of the shapefile to render.

        kwargs can specify the shapefile to render, see the implementation of
        this method for details. If kwargs does not specify the shapefile, the
        object renders the shapefile that is specified by default_layer_name,
        default_resource_module and default_resource_name.

        There are a few possibilities to define your shape:

        - PREFERRED shape_slug is defined

        - shape_id is defined.

        - resource_module and resource_name are defined.

        - layer_filename is defined. It's a link to a absolute
          filename. Not recommended because it allows injections.

        - display_fields (optional): Defines the fields to be
          displayed. List of dicts with keys name, field, field_type.

        """
        super(AdapterShapefile, self).__init__(*args, **kwargs)

        layer_arguments = kwargs['layer_arguments']
        self.layer_name = str(layer_arguments['layer_name'])
        layer_filename = layer_arguments.get('layer_filename', None)
        self.shape_id = layer_arguments.get('shape_id', None)
        self.shape_slug = layer_arguments.get('shape_slug', None)

        self.shape = None
        self.prj = None  # Projection from .prj file
        try:
            if self.shape_id is not None:
                self.shape = Shape.objects.get(pk=self.shape_id)
            if self.shape_slug is not None:
                self.shape = Shape.objects.get(slug=self.shape_slug)
        except Shape.DoesNotExist:
            raise WorkspaceItemError
        if self.shape is not None:
            self.prj = self.shape.prj

        # Fill self.layer_filename
        if layer_filename is not None:
            self.layer_filename = str(layer_filename)
            self.resource_module = None
            self.resource_name = None
        else:
            # If layer_filename is not defined, resource_module and
            # resource_name must be defined OR shape(_id/_slug) must be
            # defined.
            if self.shape is not None:
                self.layer_filename = str(self.shape.shp_file.file.name)
            else:
                # resource_module and resource_name must be defined
                self.resource_module = str(layer_arguments['resource_module'])
                self.resource_name = str(layer_arguments['resource_name'])
                self.layer_filename = pkg_resources.resource_filename(
                    self.resource_module,
                    self.resource_name)

        self.search_property_name = layer_arguments.get(
            'search_property_name', "")
        self.search_property_id = layer_arguments.get(
            'search_property_id', "")
        self.legend_id = layer_arguments.get('legend_id', None)
        self.legend_type = layer_arguments.get('legend_type', None)
        self.value_field = layer_arguments.get('value_field', None)
        self.value_name = layer_arguments.get('value_name', None)
        self.display_fields = layer_arguments.get('display_fields', [])
        if not self.display_fields:
            self.display_fields = [
                {'name': self.value_name,
                 'field': self.value_field,
                 'field_type': ShapeField.FIELD_TYPE_NORMAL}]

    def _default_mapnik_style(self):
        """
        Makes default mapnik style
        """
        area_looks = mapnik.PolygonSymbolizer(mapnik.Color('#ffb975'))
        # ^^^ light brownish
        line_looks = mapnik.LineSymbolizer(mapnik.Color('#dd0000'), 1)
        area_looks.fill_opacity = 0.5
        layout_rule = mapnik.Rule()
        layout_rule.symbols.append(area_looks)
        layout_rule.symbols.append(line_looks)
        area_style = mapnik.Style()
        area_style.rules.append(layout_rule)
        return area_style

    @property
    def _legend_object(self):
        legend_models = {
            LEGEND_TYPE_SHAPELEGEND: ShapeLegend,
            LEGEND_TYPE_SHAPELEGENDPOINT: ShapeLegendPoint,
            LEGEND_TYPE_SHAPELEGENDCLASS: ShapeLegendClass}
        legend_model = legend_models[self.legend_type]

        legend_object = None
        if self.legend_id is not None:
            legend_object = legend_model.objects.get(pk=self.legend_id)
        return legend_object

    def legend(self, updates=None):
        if (self.legend_type == LEGEND_TYPE_SHAPELEGEND or
            self.legend_type == LEGEND_TYPE_SHAPELEGENDPOINT):
            return super(AdapterShapefile, self).legend_default(
                self._legend_object)

        # LEGEND_TYPE_SHAPELEGENDCLASS
        icon_style_template = {'icon': 'empty.png',
                               'mask': ('empty_mask.png',),
                               'color': (1, 1, 1, 1)}
        legend_result = []
        legend = self._legend_object

        if legend is not None:
            for single_class in legend.shapelegendsingleclass_set.all():
                icon_style = icon_style_template.copy()
                try:
                    icon_style.update({
                            'color': single_class.legend_color().to_tuple()})
                except TypeError:
                    # Some users forget setting the color. Don't crash.
                    # Take color alarming red.
                    icon_style.update({
                            'color': (1, 0.5, 0.5, 1)})
                if single_class.icon:
                    icon_style.update({'icon': single_class.icon})
                if single_class.mask:
                    icon_style.update({'mask': (single_class.mask,)})
                img_url = self.symbol_url(icon_style=icon_style)

                if single_class.label:
                    description = single_class.label
                else:
                    description = single_class.min_value
                legend_row = {'img_url': img_url,
                              'description': description}
                legend_result.append(legend_row)
        return legend_result

    def layer(self, layer_ids=None, request=None):
        """Return layer and styles for a shapefile.

        http://127.0.0.1:8000/map/workspace/1/wms/?LAYERS=basic&SERVICE=
        WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&EXCEPTIONS=application%
        2Fvnd.ogc.se_inimage&FORMAT=image%2Fjpeg&SRS=EPSG%3A900913&BBOX=
        523838.00391791,6818214.5267836,575010.91942212,6869720.7532931&
        WIDTH=140&HEIGHT=140
        """
        layers = []
        styles = {}
        layer = mapnik.Layer(self.layer_name, detect_prj(self.prj))
        # TODO: ^^^ translation!
        logging.debug("Giving shapefile %s to a mapnik layer...",
                      self.layer_filename)
        layer.datasource = mapnik.Shapefile(
            file=self.layer_filename)

        if self.legend_id is not None:
            legend = self._legend_object
            style = legend.mapnik_style(
                value_field=str(self.value_field))
        else:
            # Show layer with default legend.
            style = self._default_mapnik_style()

        style_name = str('Area style %s::%s::%s' % (
                self.layer_filename,
                self.legend_id,
                self.value_field))
        styles[style_name] = style
        layer.styles.append(style_name)
        layers = [layer]
        logging.debug("Giving shapefile %s as layer to mapnik...",
                      self.layer_filename)
        return layers, styles

    def extent(self, identifiers=None):
        """Calculate extent using ogr GetExtent function
        """
        layer = mapnik.Layer(self.layer_name, detect_prj(self.prj))

        layer.datasource = mapnik.Shapefile(
            file=self.layer_filename)

        ds = osgeo.ogr.Open(self.layer_filename)
        lyr = ds.GetLayer()
        lyr.ResetReading()
        w, e, s, n = lyr.GetExtent()

        w, s = transform(
            Proj(detect_prj(self.prj)), google_projection, w, s)
        e, n = transform(
            Proj(detect_prj(self.prj)), google_projection, e, n)

        return {
            'north': n,
            'west': w,
            'south': s,
            'east': e}

    def search(self, x, y, radius=None):
        """
        Search area, line or point.

        Make sure that value_field, search_property_id,
        search_property_name are valid columns in your shapefile.

        x,y are google coordinates

        Note: due to mapnik #503 (http://trac.mapnik.org/ticket/503)
        the search does not work for lines and points. So the
        implementation was done with shapely.

        """
        logger.debug("Searching coordinates (%0.2f, %0.2f) radius %r..." %
                     (x, y, radius))

        if not self.search_property_name:
            # We don't have anything to return, so don't search.
            return []

        if radius is not None:
            # Manually make radius smaller

            # RG, way later: it used to say 0.2 on the line below, but
            # there were complaints saying that this was too
            # small. From some manual testing, 1 (the default) is too
            # large. I'll put 0.8. Obviously a very well argued value.
            logger.debug("Adjusting radius...")
            radius = radius * 0.8

        transformed_x, transformed_y = transform(
            google_projection, Proj(detect_prj(self.prj)), x, y)
        query_point = Point(transformed_x, transformed_y)

        ds = osgeo.ogr.Open(self.layer_filename)
        try:
            lyr = ds.GetLayer()
        except AttributeError:
            # #3033
            # This one occurs when the file does not exist.
            logger.error("The search function crashed. Probably due "
                         "to a missing shapefile.")
            return []

        if radius is not None:

            # The radius needs to be transformed as well, but how?
            # A transformed square will no longer be a square!
            # This needs further attention...

            transformed_x_radius, transformed_y_radius = transform(
                google_projection, Proj(detect_prj(self.prj)),
                x + radius, y + radius)

            radius = max(abs(transformed_x - transformed_x_radius),
                         abs(transformed_y - transformed_y_radius))

            lyr.SetSpatialFilterRect(
                transformed_x - radius,
                transformed_y - radius,
                transformed_x + radius,
                transformed_y + radius)

        lyr.ResetReading()
        feat = lyr.GetNextFeature()

        results = []

        while feat is not None:
            geom = feat.GetGeometryRef()
            if geom:
                item = loads(geom.ExportToWkt())
                distance = query_point.distance(item)
                feat_items = feat.items()

                if not radius or (radius is not None and distance < radius):
                    # Add stripped keys, because column names can contain
                    # spaces after the 'real' name.
                    for key in feat_items.keys():
                        feat_items[key.strip()] = feat_items[key]

                    # Found an item.
                    if self.search_property_name not in feat_items:
                        # This means that the search_property_name is not a
                        # valid field in the shapefile dbf.
                        logger.error(
                            ('Search: The field "%s" cannot be found in '
                             'shapefile "%s". Available fields: %r'
                             'Check your settings in '
                             'lizard_shape.models.Shape.') %
                            (self.search_property_name, self.layer_name,
                             feat_items.keys()))
                        break  # You don't have to search other rows.
                    name = str(feat_items[self.search_property_name])

                    if self.display_fields:
                        if self.display_fields[0]['field'] not in feat_items:
                            # This means that the value_field is not a
                            # valid field in the shapefile dbf.
                            logger.error(
                                ('Search: The field "%s" cannot be found in '
                                 'shapefile "%s". Check display_fields. '
                                 'Options are: %s') %
                                (self.display_fields[0]['field'],
                                 self.layer_name,
                                 feat_items.keys()))
                            break  # You don't have to search other rows.
                        name += ' - %s=%s' % (
                            self.display_fields[0]['name'],
                            str(float_to_string(feat_items[
                                        self.display_fields[0]['field']])))

                    result = {'distance': distance,
                              'name': name,
                              'workspace_item': self.workspace_item}
                    try:
                        result.update(
                            {'google_coords':
                                 transform(Proj(detect_prj(self.prj)),
                                           google_projection,
                                           *item.coords[0])})
                    except NotImplementedError:
                        logger.warning(
                            "Got a NotImplementedError while transforming "
                            "coordinates from %s to google with pyproj "
                            "for shapefile %s. Not returning google "
                            "coordinates.",
                            self.prj, self.shape)

                    if (self.search_property_id and
                        self.search_property_id in feat_items):
                        result.update(
                            {'identifier':
                                 {'id': feat_items[self.search_property_id]}})
                    else:
                        logger.error("Problem with search_property_id: %s. "
                                     "List of available properties: %r" %
                                     (self.search_property_id,
                                      feat_items.keys()))
                    results.append(result)
            feat = lyr.GetNextFeature()
        results = sorted(results, key=lambda a: a['distance'])
        if len(results) > MAX_SEARCH_RESULTS:
            logger.info('A lot of results found (%d), just taking top %s.',
                        len(results), MAX_SEARCH_RESULTS)
        return results[:MAX_SEARCH_RESULTS]

    def symbol_url(self, identifier=None, start_date=None,
                   end_date=None, icon_style=None):
        """
        Returns symbol.
        """
        if icon_style is None and self.legend_id is not None:
            if self.legend_type == LEGEND_TYPE_SHAPELEGENDPOINT:
                legend_object = ShapeLegendPoint.objects.get(
                    pk=self.legend_id)
                icon_style = legend_object.icon_style()
            elif self.legend_type == LEGEND_TYPE_SHAPELEGENDCLASS:
                legend_object = ShapeLegendClass.objects.get(
                    pk=self.legend_id)
                icon_style = legend_object.icon_style()

        return super(AdapterShapefile, self).symbol_url(
            identifier=identifier,
            start_date=start_date,
            end_date=end_date,
            icon_style=icon_style)

    def location(self, id, ids=None, force_list=False):
        """Find id in shape. If 1 id given, return dict. If multiple
        ids given, return list of dicts.

        Optional: force_list forces the output in list format
        """

        ds = osgeo.ogr.Open(self.layer_filename)
        lyr = ds.GetLayer()
        lyr.ResetReading()
        feat = lyr.GetNextFeature()

        item, google_x, google_y, feat_items = None, None, None, None
        id_list = []
        if id is not None:
            id_list.append(id)
        if ids is not None:
            id_list.extend([identifier['id'] for identifier in ids])
        if len(id_list) == 0:
            logger.warning('No id given in call to location. '
                           'Should never happen.')
            return {}

        logger.debug("Location(s): %r" % id_list)
        logger.debug("Fields to display: %r" % self.display_fields)

        result = []

        # Find one features.
        while feat is not None:
            geom = feat.GetGeometryRef()
            feat_items = feat.items()
            # Add stripped keys. Sometimes columnnames contain spaces
            # at the end.
            for key in feat_items.keys():
                feat_items[key.strip()] = feat_items[key]
            if self.search_property_id not in feat_items:
                logger.error("Search property id '%s' not available. "
                             "Options are: %r" % (self.search_property_id,
                                                  feat_items.keys()))
            if (geom and
                self.search_property_id in feat_items and
                id_list.count(feat_items[self.search_property_id]) > 0):

                # item = loads(geom.ExportToWkt())

                # Polygons get an error when getting coords. Coords
                # are not needed any more, so leave them out.

                # google_x, google_y = coordinates.rd_to_google(
                #     *item.coords[0])

                # contains {'name': <name>, 'value': <value>,
                # 'value_type: 1/2/3'}
                values = []

                for field in self.display_fields:
                    if str(field['field']) not in feat_items:
                        # Trying to show a field that's not in feat_items
                        values.append({'name': field['name'],
                                       'value': 'Not present in data',
                                       'value_type': 1})
                    else:
                        values.append({'name': field['name'],
                                       'value':
                                           feat_items[str(field['field'])],
                                       'value_type': field['field_type']})

                name = feat_items[self.search_property_name]
                result.append({
                        'name': name,
                        'shortname': name,
                        'value_name': self.value_name,
                        'value': feat_items[self.value_field],
                        'values': values,
                        'object': feat_items,
                        'workspace_item': self.workspace_item,
                        'identifier': {'id': feat_items[
                                self.search_property_id]}})

            feat = lyr.GetNextFeature()

        logger.debug("%d result(s) found" % len(result))

        if len(result) == 1 and not force_list:
            return result[0]
        else:
            return result

    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        """
        Renders table with shape attributes.
        """

        logger.debug("Generating html popup...")

        if snippet_group:
            snippets = snippet_group.snippets.all()
            identifiers = [snippet.identifier for snippet in snippets]

        display_group = self.location(None, identifiers, force_list=True)
        add_snippet = False
        if layout_options and 'add_snippet' in layout_options:
            add_snippet = layout_options['add_snippet']

        # Images for timeseries

        image_graph_url = None
        his_file_dtstart = None
        if self.shape_id is not None:
            # ^^^ is also done in __init__. TODO: refactor this out.
            shape = Shape.objects.get(pk=self.shape_id)
            if shape.his:
                image_graph_url = reverse(
                    "lizard_map.workspace_item_image",
                    kwargs={'workspace_item_id': self.workspace_item.id},
                    )
                identifiers_escaped = [
                    json.dumps(identifier).replace('"', '%22')
                    for identifier in identifiers]
                image_graph_url = image_graph_url + '?' + '&'.join(
                    ['identifier=%s' % i for i in identifiers_escaped])
                try:
                    his_file_dtstart = shape.his.hisfile().dtstart
                except AttributeError:
                    # The file probably does not exist
                    # self.bin = input.read()
                    pass

        return render_to_string(
            'lizard_shape/popup_shape.html',
            {'display_group': display_group,
             'add_snippet': add_snippet,
             'symbol_url': self.symbol_url(),
             'image_graph_url': image_graph_url,
             'adapter_class': self.adapter_class,
             'adapter_layer_json': json.dumps(self.layer_arguments),
             'his_file_dtstart': his_file_dtstart})

    def image(self, identifiers, start_date, end_date,
              width=380.0, height=250.0, layout_extra=None):
        """
        Displays timeseries graph.
        """

        line_styles = self.line_styles(identifiers)

        today = datetime.datetime.now()
        graph = Graph(start_date, end_date,
                      width=width, height=height, today=today)
        graph.axes.grid(True)

        # his = His.objects.all()[0]  # Test: take first object.
        if self.shape_id is not None:
            shape = Shape.objects.get(pk=self.shape_id)
        if self.shape_id is None or shape.his is None:
            logger.debug(
                'Shapefile %s does not have associated his file.'
                % shape)
            graph.suptitle('No data.')
            graph.add_today()
            return graph.http_png()

        hf = shape.his.hisfile()
        # parameter = hf.parameters()[2]  # Test: take first parameter.
        parameters = hf.parameters()
        locations = hf.locations()
        parameter = shape.his_parameter

        # We want the unit. The parameter often has the unit in it and
        # it is the closest we can get to unit.
        graph.axes.set_ylabel(parameter)

        # Convert dates to datetimes
        start_datetime = datetime.datetime.combine(start_date, datetime.time())
        end_datetime = datetime.datetime.combine(end_date, datetime.time())
        location_count = 0
        for identifier in identifiers:
            location = identifier['id']

            if location not in locations:
                # Skip location if not available in his file.
                logger.debug('Location "%s" not in his file "%s".' % (
                        location, shape.his))
                continue
            location_count += 1

            # parameter = parameters[index % len(parameters)]
            try:
                # u'Discharge max (m\xb3/s)' -> 'Discharge max (m\xb3/s)'
                # TODO: make better.
                weird_repr = ('%r' % parameter)[2:-1].replace("\\xb3", "\xb3")
                timeseries = hf.get_timeseries(
                    location, weird_repr, start_datetime, end_datetime, list)
            except KeyError:
                logger.error('Parameter %r not in his file. Choices are: %r' %
                             (weird_repr, parameters))
                continue

            # Plot data.
            dates = [row[0] for row in timeseries]
            values = [row[1] for row in timeseries]
            graph.axes.plot(dates, values,
                            lw=1,
                            color=line_styles[str(identifier)]['color'],
                            label=parameter)

        title = '%s (%d locations)' % (parameter, location_count)
        graph.suptitle(title)
        # if legend:
        #     graph.legend()

        graph.add_today()
        return graph.http_png()

    def collage_detail_data_description(self, identifier, *args, **kwargs):
        return 'Gegevens'

    def collage_detail_edit_action(self, identifier, *args, **kwargs):
        return None

    def collage_detail_show_edit_block(self, identifier, *args, **kwargs):
        return False

    def collage_detail_show_statistics_block(self, identifier, *args, **kwargs):
        return False
