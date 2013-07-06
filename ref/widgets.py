from django.forms.widgets import ClearableFileInput, CheckboxInput
from django.utils.html import conditional_escape, format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
import os

class ClearableFileInputPretty(ClearableFileInput):
    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs) # we totally bypass ClearableFileInput's render

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html('<a href="{0}">{1}</a>',
                                                   value.url,
                                                   force_text(os.path.basename(value.url)))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)