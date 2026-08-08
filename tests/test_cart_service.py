"""Tests for cart variant resolution."""
from app.services.cart_service import resolve_variant_id, cart_add_error_message


class TestResolveVariantId:

    def test_by_variant_id(self, db, sample_product):
        variant = sample_product.variants.first()
        assert resolve_variant_id(variant_id=variant.id) == variant.id

    def test_by_size_and_color(self, db, sample_product):
        variant = sample_product.variants.filter_by(size='0-3M', color='White').first()
        vid = resolve_variant_id(
            product_id=sample_product.id,
            size='0-3M',
            color='White',
        )
        assert vid == variant.id

    def test_single_in_stock_variant(self, db, sample_product):
        keep = sample_product.variants.first()
        for v in sample_product.variants.all():
            if v.id != keep.id:
                v.stock_quantity = 0
        db.session.commit()
        vid = resolve_variant_id(product_id=sample_product.id)
        assert vid == keep.id

    def test_size_only_when_unique(self, db, sample_product):
        variant = sample_product.variants.filter_by(size='0-3M', color='White').first()
        for v in sample_product.variants.filter_by(size='0-3M').all():
            if v.id != variant.id:
                v.stock_quantity = 0
        db.session.commit()
        vid = resolve_variant_id(product_id=sample_product.id, size='0-3M')
        assert vid == variant.id

    def test_missing_selection_error(self, db, sample_product):
        msg = cart_add_error_message(sample_product.id)
        assert 'size' in msg.lower() or 'color' in msg.lower()
