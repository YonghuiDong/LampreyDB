from django.contrib import admin
from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',

    )
    list_display_links = ('username', )


admin.site.site_header = "Chemical Admin Portal"
admin.site.site_title = "Chemical Admin Portal"
admin.site.index_title = "Chemical Admin Portal"
