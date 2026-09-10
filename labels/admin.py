from django.contrib import admin

from .models import Batch, Product, TrackingLabel, IngredientLabel


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "oil_batch_number", "active_batch", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "oil_batch_number")
    inlines = [BatchInline]


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("product", "batch_number", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("batch_number", "product__name")


@admin.register(TrackingLabel)
class TrackingLabelAdmin(admin.ModelAdmin):
    list_display = ("tracking_number", "product", "batch", "print_date", "reprint_count")
    search_fields = ("tracking_number", "product__name", "batch__batch_number")
    list_filter = ("print_date",)
    readonly_fields = [f.name for f in TrackingLabel._meta.fields]

    def has_add_permission(self, request):
        return False  # tracking labels are only ever created via the print flow


@admin.register(IngredientLabel)
class IngredientLabelAdmin(admin.ModelAdmin):
    list_display = ("product_name_snapshot", "oil_batch_snapshot", "print_date", "quantity", "note")
    search_fields = ("product_name_snapshot", "oil_batch_snapshot")
    list_filter = ("print_date",)
    readonly_fields = [f.name for f in IngredientLabel._meta.fields]

    def has_add_permission(self, request):
        return False  # ingredient labels are only ever created via the print flow