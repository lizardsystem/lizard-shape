from django.contrib import admin
from django import forms

from lizard_shape.models import Category
from lizard_shape.models import Shape
from lizard_shape.models import ShapeLegend
from lizard_shape.models import ShapeLegendPoint


class ShapeNameError(Exception):
    pass


def check_extension_or_error(filename, extension, extension_name=None):
    """
    Checks filename for given extension. If it fails, raise
    forms.ValidationError.

    Filename is absolute or relative.
    """
    first = filename.rpartition('.')
    if extension_name is None:
        extension_name = '%s file' % extension
    if first[-1] != extension:
        raise forms.ValidationError(
            "%s doest not have extension .%s." % (extension_name, extension))


class ShapeForm(forms.ModelForm):
    """Admin form for model Shape. Adds extra checks.

    TODO: How to test this class?"""

    class Meta:
        model = Shape

    def clean(self):
        cleaned_data = super(ShapeForm, self).clean()
        shp_first = cleaned_data['shp_file'].name.rpartition('.')
        dbf_first = cleaned_data['dbf_file'].name.rpartition('.')
        shx_first = cleaned_data['shx_file'].name.rpartition('.')
        prj_first = cleaned_data['prj_file'].name.rpartition('.')
        if not(shp_first[0] == dbf_first[0] == shx_first[0] == prj_first[0]):
            raise forms.ValidationError(
                'Files do not have common filename base.')

        return cleaned_data

    def clean_shp_file(self, *args, **kwargs):
        data = self.cleaned_data['shp_file']
        check_extension_or_error(data.name, 'shp', 'Shp_file')
        return data

    def clean_dbf_file(self, *args, **kwargs):
        data = self.cleaned_data['dbf_file']
        check_extension_or_error(data.name, 'dbf', 'Dbf_file')
        return data

    def clean_shx_file(self, *args, **kwargs):
        data = self.cleaned_data['shx_file']
        check_extension_or_error(data.name, 'shx', 'Shx_file')
        return data

    def clean_prj_file(self, *args, **kwargs):
        data = self.cleaned_data['prj_file']
        check_extension_or_error(data.name, 'prj', 'Prj_file')
        return data


class ShapeLegendInline(admin.TabularInline):
    model = ShapeLegend


class ShapeLegendPointInline(admin.TabularInline):
    model = ShapeLegendPoint


class ShapeAdmin(admin.ModelAdmin):
    form = ShapeForm
    inlines = [ShapeLegendInline, ShapeLegendPointInline, ]


class ShapeInline(admin.TabularInline):
    model = Shape


admin.site.register(Category)
admin.site.register(Shape, ShapeAdmin)
admin.site.register(ShapeLegend)
admin.site.register(ShapeLegendPoint)
