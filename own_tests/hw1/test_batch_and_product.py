from datetime import date
from datetime import date, timedelta
from own_model import Product, OrderLine, Batch, OutOfStock, AllocationError, DeallocationError
import pytest


today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

#product tests
def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    product = Product(sku="RETRO-CLOCK", batches=[in_stock_batch, shipment_batch])
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    product.allocate(line)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    product = Product(sku="MINIMALIST-SPOON", batches=[medium, earliest, latest])
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    product.allocate(line)

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)
    product = Product(sku="HIGHBROW-POSTER", batches=[in_stock_batch, shipment_batch])
    allocation = product.allocate(line)
    assert allocation == in_stock_batch.reference

# batch tests
def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET",20, 2)
    batch.deallocate(unallocated_line) 
    assert batch.available_quantity == 20

def test_deallocation_reduces_available_quantity():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == 20

def test_allocation_after_deallocation():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_cannot_deallocate_if_not_allocated():
    batch, unallocated_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20

def test_cannot_allocate_if_batch_expired():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    batch.eta = date.today() - timedelta(days=1)  # batch expired yesterday
    assert batch.can_allocate(line) is False

def test_allocation_raises_out_of_stock_exception_if_cannot_allocate():
    product = Product(sku="ELEGANT-LAMP", batches=[])
    line = OrderLine("order-123", "ELEGANT-LAMP", 10)
    with pytest.raises(OutOfStock, match="Out of stock for sku ELEGANT-LAMP"):
        product.allocate(line)

def test_allocation_raises_allocation_error_if_cannot_allocate():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    batch._purchased_quantity = 0  # batch has no available quantity
    with pytest.raises(AllocationError, match=f"Cannot allocate line {line.reference} to batch {batch.reference}"):
        batch.allocate(line)

def test_deallocation_raises_deallocation_error_if_not_allocated():
    batch, unallocated_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    with pytest.raises(DeallocationError, match=f"Cannot deallocate line {unallocated_line.reference} from batch {batch.reference}"):
        batch.deallocate(unallocated_line)