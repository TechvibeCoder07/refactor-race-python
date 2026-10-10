import pytest

from src.legacy_checkout import ORDERS_PROCESSED


@pytest.fixture(autouse=True)
def isolate_order_history():
    previous_orders = ORDERS_PROCESSED[:]
    ORDERS_PROCESSED.clear()
    yield
    ORDERS_PROCESSED[:] = previous_orders
