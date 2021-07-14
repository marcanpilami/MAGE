# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Django imports
from django.forms.widgets import ClearableFileInput, CheckboxInput
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

class ClearableFileInputPretty(ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
            'initial_url': value.url if value and hasattr(value, 'url') else None,
        }
        template = '%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs, renderer)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html('<a href="{0}">click here</a>',
                                                   value.url,)
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)
    