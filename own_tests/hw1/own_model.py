from dataclasses import dataclass
from datetime import date
from typing import List


class OutOfStock(Exception):
    pass

class AllocationError(Exception):
    pass

class DeallocationError(Exception):
    pass


@dataclass(frozen=True)
class OrderLine:
    reference: str
    sku: str
    quantity: int

class Batch:
    def __init__(self, reference: str, sku: str, qty: int, eta: date):
        if reference is None or len(reference) > 25:
            raise ValueError("Reference cannot be null and must be no more than 25 characters")
        if sku is None or sku == "":
            raise ValueError("SKU cannot be null or an empty string")
        if qty < 0:
            raise ValueError("Quantity cannot be negative")
        if eta is not None and eta < date.today():
            raise ValueError("ETA cannot be in the past")
        self.reference = reference
        self.sku = sku
        self._purchased_quantity = qty
        self.eta = eta
        self._allocations = set()

    @property
    def available_quantity(self):
        return self._purchased_quantity - sum(line.quantity for line in self._allocations)

    def allocate(self, line: OrderLine):
        if not self.can_allocate(line): # this check is added to satisfy the test: test_allocation_is_idempotent
            raise AllocationError(f'Cannot allocate line {line.reference} to batch {self.reference}')
        self._allocations.add(line)
    
    def deallocate(self, line: OrderLine):
        if line not in self._allocations:
            raise DeallocationError(f'Cannot deallocate line {line.reference} from batch {self.reference}')
        self._allocations.remove(line)

    # when could it make sense to set as expired? - food or medicine, promotions, old version of a product etc.
    def is_expired(self):
        return self.eta is not None and self.eta < date.today()

    def can_allocate(self, line: OrderLine):
        return self.sku == line.sku and self.available_quantity >= line.quantity and not self.is_expired()
    
class Product:
    def __init__(self, sku: str, batches: List[Batch]):
        if batches is None:  # should be an empty list, not None
            raise ValueError("Batches cannot be null")
        self.sku = sku
        self.batches = batches

    def allocate(self, line: OrderLine):
        in_stock_batches = sorted([b for b in self.batches if b.eta is None or b.eta >= date.today()],
                                  key=lambda b: b.eta or date.min)  # sorted method is added to satisfy test_prefers_earlier_batches
        if not in_stock_batches:
            raise OutOfStock(f'Out of stock for sku {line.sku}')
        in_stock_batches[0].allocate(line)
        return in_stock_batches[0].reference
    


