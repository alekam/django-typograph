from django.forms.widgets import TextInput


__all__ = ['TypographWidget', ]


class TypographWidget(TextInput):
    
    class Media:
        js = ('lib/typograph/typograph.js', 'lib/typograph/widget.js')
    
    def render(self, *args, **kwargs):
        self.attrs.update({'class': 'typograph vTextField'})
        return super(TypographWidget, self).render(*args, **kwargs)
    
    