"""
Models for the perfume label printing system.

Design notes
------------
- Product: one row per perfume. Ingredients text lives directly on the
  product (the system only ever prints the *current* ingredients — no
  history is required for that per the spec).
- Batch: oil-batch numbers. A product can have many batches over
  time, but only one is "active" at a time. We keep old batches so that
  tracking labels printed under an old batch still resolve correctly.
- TrackingLabel: one row PER PHYSICAL BOTTLE. This is the permanent,
  searchable record (by tracking number, product name, or batch number).
  Reprinting an existing tracking label must NOT create a new row / new
  number — see views.reprint_tracking.
- IngredientLabel: one row per ingredient label print. This tracks the
  history of ingredient label prints with the EZLOT oil batch number.
"""
import random
from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(_("perfume name"), max_length=200, unique=True)
    ingredients_text = models.TextField(_("ingredients"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    oil_batch_number = models.CharField(
        _("oil batch number"), max_length=50, blank=True, default=""
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def active_batch(self):
        return self.batches.filter(is_active=True).first()


class Batch(models.Model):
    product = models.ForeignKey(
        Product, related_name="batches", on_delete=models.CASCADE,
        verbose_name=_("product"),
    )
    batch_number = models.CharField(_("batch number"), max_length=50)
    is_active = models.BooleanField(_("active batch"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("batch")
        verbose_name_plural = _("batches")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "batch_number"], name="unique_batch_per_product"
            )
        ]

    def __str__(self):
        return f"{self.product.name} · {self.batch_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            # Only one active batch per product.
            Batch.objects.filter(product=self.product).exclude(pk=self.pk).update(
                is_active=False
            )

    @staticmethod
    def generate_unique_number():
        """Auto-generates a unique batch number: DDMMYY-XXX, where
        XXX won't repeat among batches created that same day."""
        # Get today's date in DDMMYY format
        today = timezone.localdate()
        date_code = today.strftime("%d%m%y")
        
        # Try up to 999 times to find a unique serial
        used_serials = set(
            Batch.objects.filter(
                batch_number__startswith=date_code
            ).values_list('batch_number', flat=True)
        )
        
        for _attempt in range(999):
            serial = f"{random.randint(1, 999):03d}"
            candidate = f"{date_code}-{serial}"
            if candidate not in used_serials:
                return candidate
        raise RuntimeError("All 999 batch numbers for today are already used.")


def _random_serial():
    return f"{random.randint(1, 999):03d}"


class TrackingLabel(models.Model):
    """One permanent record per physical bottle labelled."""

    product = models.ForeignKey(
        Product, related_name="tracking_labels", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_("product"),
    )
    batch = models.ForeignKey(
        Batch, related_name="tracking_labels", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_("batch"),
    )
    product_name_snapshot = models.CharField(_("perfume name (snapshot)"), max_length=200, default="", blank=True)
    batch_number_snapshot = models.CharField(_("batch number (snapshot)"), max_length=50, default="", blank=True)
    print_date = models.DateField(_("print date"), default=timezone.localdate)
    print_time = models.TimeField(_("print time"),auto_now_add=True, null=True, blank=True)
    serial = models.CharField(_("serial"), max_length=20)
    tracking_number = models.CharField(
        _("tracking number"), max_length=40, unique=True, db_index=True
    )
    printed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_("printed by"),
    )
    reprint_count = models.PositiveIntegerField(_("times reprinted"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("tracking label")
        verbose_name_plural = _("tracking labels")
        ordering = ["-created_at"]

    def __str__(self):
        return self.tracking_number

    @staticmethod
    def generate_unique(product, batch, user=None):
        date_code = timezone.localdate().strftime("%d%m%y")
        for _attempt in range(999):
            serial = _random_serial()
            tracking_number = f"{date_code}-{serial}"
            if not TrackingLabel.objects.filter(tracking_number=tracking_number).exists():
                return TrackingLabel.objects.create(
                    product=product,
                    batch=batch,
                    product_name_snapshot=product.name,
                    batch_number_snapshot=batch.batch_number,
                    print_date=timezone.localdate(),
                    serial=serial,
                    tracking_number=tracking_number,
                    printed_by=user,
                )
        raise RuntimeError("All 999 tracking numbers for today are already used.")    
    @property
    def display_product_name(self):
        return self.product.name if self.product_id else self.product_name_snapshot

    @property
    def display_batch_number(self):
        return self.batch.batch_number if self.batch_id else self.batch_number_snapshot


class IngredientLabel(models.Model):
    """One record per ingredient label print."""
    
    product = models.ForeignKey(
        Product, related_name="ingredient_labels", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_("product"),
    )
    product_name_snapshot = models.CharField(_("perfume name (snapshot)"), max_length=200, default="", blank=True)
    oil_batch_snapshot = models.CharField(_("oil batch snapshot"), max_length=50, default="", blank=True)
    print_date = models.DateField(_("print date"), default=timezone.localdate)
    print_time = models.TimeField(_("print time"), null=True, blank=True,auto_now_add=True)
    quantity = models.PositiveIntegerField(_("quantity printed"), default=1)
    note = models.TextField(_("note"), blank=True, default="")
    printed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_("printed by"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("ingredient label")
        verbose_name_plural = _("ingredient labels")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_name_snapshot} - Ingredients"