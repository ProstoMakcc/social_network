from django import forms

class CreatePostForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-field'}), 
                                  required=True)
    media = forms.FileField(widget=forms.FileInput(attrs={'class': 'media-input'}), 
                            required=True)

class EditPostForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-field'}), 
                                  required=False)
    media = forms.FileField(widget=forms.FileInput(attrs={'class': 'media-input'}), 
                            required=False)

class EditCommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-field'}), 
                                  required=False)
    media = forms.FileField(widget=forms.FileInput(attrs={'class': 'media-input'}), 
                            required=False)
