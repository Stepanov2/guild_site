from django_filters import FilterSet
from .models import Post, Reply


class ReplyFilter(FilterSet):
    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.filters['post'].queryset = Post.objects.filter(user=self.user, reply__isnull=False)

    class Meta:
        model = Reply
        fields = {
            'post': ['exact'],
        }