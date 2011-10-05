# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_shape.models import Category


def homepage(request,
             root_slug=None,
             template="lizard_shape/homepage.html",
             crumbs_prepend=None):
    """
    Main page for Shape.
    """

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

    parent_category = None
    if root_slug is not None:
        parent_category = get_object_or_404(Category, slug=root_slug)
    shapes_tree = get_tree(parent_category)

    if crumbs_prepend is not None:
        crumbs = list(crumbs_prepend)
    else:
        crumbs = [{'name': 'home', 'url': '/'}]
    crumbs.append({'name': 'kaarten',
                   'title': 'kaarten',
                   'url': reverse('lizard_shape.homepage')})

    return render_to_response(
        template,
        {'shapes_tree': shapes_tree,
         'parent_category': parent_category,
         'crumbs': crumbs,
         'transparency_slider': True,
         },
        context_instance=RequestContext(request))
