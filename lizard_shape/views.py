# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from lizard_map.views import AppView
from lizard_shape.models import Category


def shape_treeitems(shapes):
    """
    Make treeitems for given shapes, return them in a list.
    """

    children = []

    for shape in shapes:
        # Append shapes by legend.
        shapelegends = shape.template.shapelegend_set.all()

        # Legends for lines.
        for shapelegend in shapelegends:
            children.append(
                {'name': '%s - %s' % (
                       shape.name, str(shapelegend)),
                 'description': shape.description,
                 'type': 'shape',
                 'adapter_layer_json':
                 shapelegend.adapter_layer_json(shape)})

        # Legends for points.
        shapelegendpoints = shape.template.shapelegendpoint_set.all()
        for shapelegendpoint in shapelegendpoints:
            children.append(
                {'name': '%s - %s' % (
                        shape.name, str(shapelegendpoint)),
                 'description': shape.description,
                 'type': 'shape',
                 'adapter_layer_json':
                 shapelegendpoint.adapter_layer_json(shape)})

        # Legends for points, lines, areas in classes.
        shapelegendclasses = shape.template.shapelegendclass_set.all()
        for shapelegendclass in shapelegendclasses:
            children.append(
                {'name': '%s - %s' % (
                        shape.name, str(shapelegendclass)),
                 'description': shape.description,
                 'type': 'shape',
                 'adapter_layer_json':
                 shapelegendclass.adapter_layer_json(shape)})

    return children


def get_tree(parent=None):
    """
    Make tree for homepage using Category and Shape.
    """
    result = []

    categories = Category.objects.filter(parent=parent)

    for category in categories:
        # Append sub categories.
        children = get_tree(parent=category)
        # Find shapes.
        # shapes = category.shapes.all()
        row = {'name': category.name,
               'type': 'category',
               'children': children}
        result.append(row)

    if parent is not None:
        result += shape_treeitems(parent.shapes.all())

    return result


class HomepageView(AppView):
    """
    Class based main page for Shape.
    """

    template_name = 'lizard_shape/homepage.html'
    transparancy_slider = True
    edit_link = '/admin/lizard_shape/'

    def get(self, request, *args, **kwargs):
        """Get parameters from kwargs and GET parameters. TODO: better way"""

        self.root_slug = kwargs.get('root_slug', None)

        return super(HomepageView, self).get(request, *args, **kwargs)

    def parent_category(self):
        if self.root_slug is not None:
            return get_object_or_404(Category, slug=self.root_slug)

    def shapes_tree(self):
        return get_tree(self.parent_category())
