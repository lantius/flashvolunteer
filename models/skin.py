
from google.appengine.ext import db
from models.application import Application




################################################################################
# Neighborhood
class Skin(db.Model):
    application = db.ReferenceProperty(Application,
                                       collection_name = 'skin',
                                       default = None)

    misc_css = db.TextProperty(default='')

#======================================================
#>>Color
#======================================================
    header_default_text_color = db.StringProperty(default='')
    header_link_color = db.StringProperty(default='')
    header_nav_text_color = db.StringProperty(default='')
    body_default_text_color = db.StringProperty(default='')
    
    body_heavy_text_color = db.StringProperty(default='')
    body_light_text_color = db.StringProperty(default='')
    body_extra_light_text_color = db.StringProperty(default='')
    body_section1_text_color = db.StringProperty(default='')

    body_section2_text_color = db.StringProperty(default='')
    body_section_link_color = db.StringProperty(default='')
    body_section2_link_color = db.StringProperty(default='')
    body_attention_color = db.StringProperty(default='')

    body_link_color = db.StringProperty(default='')


#======================================================
#>>Background
#======================================================

    header_background_color = db.StringProperty(default='')
    header_nav_background_color = db.StringProperty(default='')
    header_nav_hover_color = db.StringProperty(default='')
    header_banner_background_color = db.StringProperty(default='')
    
    body_background_color = db.StringProperty(default='')
    body_section1_background_color = db.StringProperty(default='')
    body_section2_background_color = db.StringProperty(default='')
    body_subtle_block_background_color = db.StringProperty(default='')
    
#======================================================
#>>BORDER
#======================================================
    header_strip_color = db.StringProperty(default='')
    body_subtle_block_border_color = db.StringProperty(default='')
    body_subtle_block_border_color = db.StringProperty(default='')
    body_item_separator_border_color = db.StringProperty(default='')
    body_page_title_underline_color = db.StringProperty(default='')


fields = ('application', 'misc_css',
    'header_default_text_color','header_link_color','header_nav_text_color','body_default_text_color',
    'body_heavy_text_color','body_light_text_color','body_extra_light_text_color','body_section1_text_color',
    'body_section2_text_color','body_section_link_color','body_section2_link_color','body_attention_color',
    'body_link_color','header_background_color','header_nav_background_color','header_nav_hover_color',
    'header_banner_background_color','body_background_color','body_section1_background_color','body_section2_background_color',
    'body_subtle_block_background_color','header_strip_color','body_subtle_block_border_color','body_subtle_block_border_color',
    'body_item_separator_border_color','body_page_title_underline_color')
    
    
from components.appengine_admin.model_register import register, ModelAdmin
## Admin views ##
class AdminSkin(ModelAdmin):
    model = Skin
    listFields = fields
    editFields = fields
    readonlyFields = ()

register(AdminSkin)
