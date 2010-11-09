# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_map.daterange import DateRangeForm
from lizard_map.daterange import current_start_end_dates
from lizard_map.workspace import WorkspaceManager

from lizard_shape.models import Category
from lizard_shape.models import ShapeLegend
from lizard_shape.models import ShapeLegendPoint


def homepage(request,
             javascript_click_handler='popup_click_handler',
             javascript_hover_handler='popup_hover_handler',
             template="lizard_shape/homepage.html"):
    """
    Main page for Shape.
    """

    def get_tree(parent=None):
        """
        Make tree for homepage using Category and Shape.
        """
        result = []
        categories = Category.objects.filter(parent=parent)
        for category in categories:
            # Append sub categories.
            children = get_tree(parent=category)
            # Append shapes by legend.
            shapelegends = ShapeLegend.objects.filter(shape__category=category)
            # Legends for lines.
            for shapelegend in shapelegends:
                id_field = (shapelegend.shape.id_field
                            if shapelegend.shape.id_field else "")
                name_field = (shapelegend.shape.name_field
                              if shapelegend.shape.name_field else "")
                children.append({
                        'name': str(shapelegend),
                        'type': 'shape',
                        'adapter_layer_json': (
                            '{"layer_name": "%s", '
                            '"legend_id": "%d", '
                            '"value_field": "%s", '
                            '"value_name": "%s", '
                            '"layer_filename": "%s", '
                            '"search_property_id": "%s", '
                            '"search_property_name": "%s"}') % (
                            str(shapelegend),
                            shapelegend.legend.id,
                            shapelegend.value_field,
                            shapelegend.name,
                            shapelegend.shape.shp_file.path,
                            id_field,
                            name_field)})
            # Legends for points.
            shapelegendpoints = ShapeLegendPoint.objects.filter(
                shape__category=category)
            for shapelegendpoint in shapelegendpoints:
                id_field = (shapelegendpoint.shape.id_field
                            if shapelegendpoint.shape.id_field else "")
                name_field = (shapelegendpoint.shape.name_field
                              if shapelegendpoint.shape.name_field else "")
                children.append({
                        'name': str(shapelegendpoint),
                        'type': 'shape',
                        'adapter_layer_json': (
                            '{"layer_name": "%s", '
                            '"legend_point_id": "%d", '
                            '"value_field": "%s", '
                            '"value_name": "%s", '
                            '"layer_filename": "%s", '
                            '"search_property_id": "%s", '
                            '"search_property_name": "%s"}') % (
                            str(shapelegendpoint),
                            shapelegendpoint.legend_point.id,
                            shapelegendpoint.value_field,
                            shapelegendpoint.name,
                            shapelegendpoint.shape.shp_file.path,
                            id_field,
                            name_field)})
            row = {'name': category.name,
                   'type': 'category',
                   'children': children}
            result.append(row)
        return result

    shapes_tree = get_tree()

    workspace_manager = WorkspaceManager(request)
    workspaces = workspace_manager.load_or_create()
    date_range_form = DateRangeForm(
        current_start_end_dates(request, for_form=True))

    return render_to_response(
        template,
        {'javascript_hover_handler': javascript_hover_handler,
         'javascript_click_handler': javascript_click_handler,
         'date_range_form': date_range_form,
         'workspaces': workspaces,
         'shapes_tree': shapes_tree},
        context_instance=RequestContext(request))
