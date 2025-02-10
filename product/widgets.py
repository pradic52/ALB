from django.forms.widgets import ClearableFileInput

class CustomImageWidget(ClearableFileInput):
    template_name = 'custom_image_widget.html'

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'custom-image-input'
