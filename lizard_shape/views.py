# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_map.daterange import DateRangeForm
from lizard_map.daterange import current_start_end_dates
from lizard_map.workspace import WorkspaceManager

from lizard_shape.models import Category
from lizard_shape.models import Shape
from lizard_shape.models import ShapeLegend


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
            # Append shapes.
            for shapelegend in ShapeLegend.objects.filter(shape__category=category):
                children.append({
                        'name': str(shapelegend),
                        'type': 'shape',
                        'adapter_layer_json': (
                            '{"layer_name": "Waterlichamen", '
                            '"legend_id": "%d", '
                            '"value_field": "%s", '
                            '"layer_filename": "%s", '
                            '"search_property_name": "WGBNAAM"}') % (
                            shapelegend.legend.id,
                            shapelegend.value_field,
                            shapelegend.shape.shp_file.path) })
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
