from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta: #특정한 변수의 값을 바꾸기 위해, 미리 지정해둔 예약어를 바꾸기 위해 값을 지정해줄 수 있음
        model = Comment
        fields = ('content',)