from django.urls import path

from . import views

app_name = "labels"

urlpatterns = [
    # Main printing screen
    path("", views.print_page, name="print"),
    path("api/search/", views.api_search_products, name="api_search"),
    path("api/product/<int:product_id>/", views.api_product_detail, name="api_product_detail"),
    path("print/tracking/", views.print_tracking, name="print_tracking"),
    path("print/ingredients/", views.print_ingredients, name="print_ingredients"),
    path("print/reprint/", views.reprint_tracking, name="reprint_tracking"),

    # Product & batch management
    path("products/", views.products_page, name="products"),
    path("products/<int:product_id>/batches/add/", views.product_add_batch, name="product_add_batch"),
    path(
        "products/<int:product_id>/batches/<int:batch_id>/activate/",
        views.product_set_active_batch,
        name="product_set_active_batch",
    ),
    # path("products/<int:product_id>/toggle/", views.product_toggle_active, name="product_toggle_active"),
    path("products/<int:product_id>/delete/", views.product_delete, name="product_delete" ),

    # Ingredients management
    path("ingredients/", views.ingredients_page, name="ingredients"),

    # Reports
    path("reports/", views.reports_page, name="reports"),
    path("reports/export.xlsx", views.export_xlsx, name="export_xlsx"),
    path("reports/export-counter.xlsx", views.export_xlsx_with_counter, name="export_xlsx_counter"),
    path("reports/clear/", views.clear_tracking_records, name="clear_records"),
]
