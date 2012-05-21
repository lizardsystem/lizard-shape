# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("lizard_map", "0001_initial"),
        )

    def forwards(self, orm):

        # Adding model 'Shape'
        db.create_table('lizard_shape_shape', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('shp_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('dbf_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('shx_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('prj_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('his', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_shape.His'], null=True, blank=True)),
            ('his_parameter', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_shape.ShapeTemplate'])),
        ))
        db.send_create_signal('lizard_shape', ['Shape'])

        # Adding model 'ShapeTemplate'
        db.create_table('lizard_shape_shapetemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('id_field', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('name_field', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('lizard_shape', ['ShapeTemplate'])

        # Adding model 'ShapeField'
        db.create_table('lizard_shape_shapefield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('field_type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('shape_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_shape.ShapeTemplate'])),
        ))
        db.send_create_signal('lizard_shape', ['ShapeField'])

        # Adding model 'Category'
        db.create_table('lizard_shape_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_shape.Category'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_shape', ['Category'])

        # Adding M2M table for field shapes on 'Category'
        db.create_table('lizard_shape_category_shapes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm['lizard_shape.category'], null=False)),
            ('shape', models.ForeignKey(orm['lizard_shape.shape'], null=False))
        ))
        db.create_unique('lizard_shape_category_shapes', ['category_id', 'shape_id'])

        # Adding model 'ShapeLegend'
        db.create_table('lizard_shape_shapelegend', (
            ('legend_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['lizard_map.Legend'], unique=True, primary_key=True)),
            ('shape_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_shape.ShapeTemplate'])),
            ('value_field', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('lizard_shape', ['ShapeLegend'])

        # Adding model 'ShapeLegendPoint'
        db.create_table('lizard_shape_shapelegendpoint', (
            ('legendpoint_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['lizard_map.LegendPoint'], unique=True, primary_key=True)),
            ('shape_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_shape.ShapeTemplate'])),
            ('value_field', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('lizard_shape', ['ShapeLegendPoint'])

        # Adding model 'ShapeLegendClass'
        db.create_table('lizard_shape_shapelegendclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descriptor', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('shape_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_shape.ShapeTemplate'])),
            ('value_field', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('lizard_shape', ['ShapeLegendClass'])

        # Adding model 'ShapeLegendSingleClass'
        db.create_table('lizard_shape_shapelegendsingleclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shape_legend_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_shape.ShapeLegendClass'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('min_value', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('max_value', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('is_exact', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('color', self.gf('lizard_map.fields.ColorField')(max_length=8, null=True, blank=True)),
            ('color_inside', self.gf('lizard_map.fields.ColorField')(max_length=8, null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('mask', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
        ))
        db.send_create_signal('lizard_shape', ['ShapeLegendSingleClass'])

        # Adding model 'His'
        db.create_table('lizard_shape_his', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('filename', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('lizard_shape', ['His'])


    def backwards(self, orm):

        # Deleting model 'Shape'
        db.delete_table('lizard_shape_shape')

        # Deleting model 'ShapeTemplate'
        db.delete_table('lizard_shape_shapetemplate')

        # Deleting model 'ShapeField'
        db.delete_table('lizard_shape_shapefield')

        # Deleting model 'Category'
        db.delete_table('lizard_shape_category')

        # Removing M2M table for field shapes on 'Category'
        db.delete_table('lizard_shape_category_shapes')

        # Deleting model 'ShapeLegend'
        db.delete_table('lizard_shape_shapelegend')

        # Deleting model 'ShapeLegendPoint'
        db.delete_table('lizard_shape_shapelegendpoint')

        # Deleting model 'ShapeLegendClass'
        db.delete_table('lizard_shape_shapelegendclass')

        # Deleting model 'ShapeLegendSingleClass'
        db.delete_table('lizard_shape_shapelegendsingleclass')

        # Deleting model 'His'
        db.delete_table('lizard_shape_his')


    models = {
        'lizard_map.legend': {
            'Meta': {'object_name': 'Legend'},
            'default_color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'descriptor': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'max_value': ('django.db.models.fields.FloatField', [], {'default': '100'}),
            'min_color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'min_value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'steps': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'too_high_color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'too_low_color': ('lizard_map.fields.ColorField', [], {'max_length': '8'})
        },
        'lizard_map.legendpoint': {
            'Meta': {'object_name': 'LegendPoint', '_ormbases': ['lizard_map.Legend']},
            'icon': ('django.db.models.fields.CharField', [], {'default': "'empty.png'", 'max_length': '80'}),
            'legend_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['lizard_map.Legend']", 'unique': 'True', 'primary_key': 'True'}),
            'mask': ('django.db.models.fields.CharField', [], {'default': "'empty_mask.png'", 'max_length': '80', 'null': 'True', 'blank': 'True'})
        },
        'lizard_shape.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.Category']", 'null': 'True', 'blank': 'True'}),
            'shapes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_shape.Shape']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20', 'db_index': 'True'})
        },
        'lizard_shape.his': {
            'Meta': {'object_name': 'His'},
            'filename': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'lizard_shape.shape': {
            'Meta': {'object_name': 'Shape'},
            'dbf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'his': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.His']", 'null': 'True', 'blank': 'True'}),
            'his_parameter': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'prj_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'shp_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'shx_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20', 'db_index': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.ShapeTemplate']"})
        },
        'lizard_shape.shapefield': {
            'Meta': {'ordering': "('index',)", 'object_name': 'ShapeField'},
            'field': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'field_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'shape_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.ShapeTemplate']"})
        },
        'lizard_shape.shapelegend': {
            'Meta': {'object_name': 'ShapeLegend', '_ormbases': ['lizard_map.Legend']},
            'legend_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['lizard_map.Legend']", 'unique': 'True', 'primary_key': 'True'}),
            'shape_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.ShapeTemplate']"}),
            'value_field': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'lizard_shape.shapelegendclass': {
            'Meta': {'object_name': 'ShapeLegendClass'},
            'descriptor': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shape_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.ShapeTemplate']"}),
            'value_field': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'lizard_shape.shapelegendpoint': {
            'Meta': {'object_name': 'ShapeLegendPoint', '_ormbases': ['lizard_map.LegendPoint']},
            'legendpoint_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['lizard_map.LegendPoint']", 'unique': 'True', 'primary_key': 'True'}),
            'shape_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.ShapeTemplate']"}),
            'value_field': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'lizard_shape.shapelegendsingleclass': {
            'Meta': {'object_name': 'ShapeLegendSingleClass'},
            'color': ('lizard_map.fields.ColorField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'color_inside': ('lizard_map.fields.ColorField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_exact': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'mask': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'shape_legend_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.ShapeLegendClass']"}),
            'size': ('django.db.models.fields.FloatField', [], {'default': '1.0'})
        },
        'lizard_shape.shapetemplate': {
            'Meta': {'object_name': 'ShapeTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_field': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'name_field': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['lizard_shape']
