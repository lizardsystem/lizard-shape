from django.contrib import admin

from lizard_shape.models import Category
from lizard_shape.models import Shape
from lizard_shape.models import ShapeLegend


admin.site.register(Category)
admin.site.register(Shape)
admin.site.register(ShapeLegend)
