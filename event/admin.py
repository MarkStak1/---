from django.contrib import admin
from .models import Category, Event, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'price', 'has_preview')
    list_filter = ('category', 'date')
    search_fields = ('title', 'location')

    @admin.display(boolean=True, description='Превью')
    def has_preview(self, obj):
        return bool(obj.preview)


admin.site.register(Category)
admin.site.register(Registration)
