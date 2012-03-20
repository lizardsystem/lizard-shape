# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Shape.prj'
        db.add_column('lizard_shape_shape', 'prj', self.gf('django.db.models.fields.TextField')(default='dummy'), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Shape.prj'
        db.delete_column('lizard_shape_shape', 'prj')


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
            'Meta': {'ordering': "('name',)", 'object_name': 'Category'},
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
            'Meta': {'ordering': "('name',)", 'object_name': 'Shape'},
            'dbf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'his': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_shape.His']", 'null': 'True', 'blank': 'True'}),
            'his_parameter': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'prj': ('django.db.models.fields.TextField', [], {}),
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
            'Meta': {'ordering': "('name',)", 'object_name': 'ShapeTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_field': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'name_field': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['lizard_shape']
