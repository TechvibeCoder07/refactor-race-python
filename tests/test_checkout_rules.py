from copy import deepcopy

import pytest

from src.legacy_checkout import (
    ORDERS_PROCESSED,
    busca_duplicados,
    calc_valor_com_desconto,
    calcula_pedido,
    process_order,
)


@pytest.mark.parametrize(
    "customer_type,subtotal,coupon,discount,total,points",
    [
        ("regular", 799, "", 0, 854.93, 85),
        ("regular", 800, "", 40, 813.20, 81),
        ("vip", 999, "", 99.90, 962.04, 192),
        ("vip", 1000, "", 150, 909.50, 181),
        ("employee", 100, "", 20, 105.60, 10),
        ("unknown", 100, "", 0, 127, 12),
        ("regular", 400, "PROMO10", 40, 405.20, 40),
        ("regular", 499, "PROMO20", 0, 553.93, 55),
        ("regular", 500, "PROMO20", 100, 428, 42),
        ("employee", 500, "PROMO10", 125, 401.25, 40),
        ("vip", 1200, "PROMO20", 300, 963, 192),
        ("vip", 100, "VIP50", 25, 100.25, 20),
        ("vip", 400, "VIP50", 90, 351.70, 70),
        ("regular", 400, "VIP50", 0, 448, 44),
        ("regular", 400, "promo10", 0, 448, 44),
        ("regular", 400, "INVALID", 0, 448, 44),
        ("vip", 0, "VIP50", 0, 20, 4),
        ("vip", 1000, "PROMO10", 250, 802.50, 160),
        ("regular", 800, "PROMO20", 200, 642, 64),
    ],
)
def test_customer_and_coupon_rules(
    customer_type, subtotal, coupon, discount, total, points
):
    result = process_order(
        {"name": "Cliente", "type": customer_type},
        [{"name": "Produto", "price": subtotal, "qty": 1}],
        coupon=coupon,
    )
    assert result["subtotal"] == subtotal
    assert result["discount"] == discount
    assert result["total"] == total
    assert result["points"] == points


@pytest.mark.parametrize(
    "state,shipping,tax,total",
    [
        ("MG", 20.80, 7, 127.80),
        ("SP", 20.80, 9, 129.80),
        ("RJ", 20.80, 8, 128.80),
        ("ES", 20.80, 7, 127.80),
        ("BA", 36.20, 12, 148.20),
    ],
)
def test_shipping_and_tax_by_state(state, shipping, tax, total):
    result = process_order(
        {"name": "Ana", "type": "regular"},
        [{"name": "Produto", "price": 100, "qty": 1, "weight": 2}],
        state=state,
    )
    assert result["shipping"] == shipping
    assert result["tax"] == tax
    assert result["total"] == total
    assert result["points"] == int(total / 10)


@pytest.mark.parametrize(
    "state,price,shipping,tax,total,points",
    [
        ("MG", 500, 37.44, 35, 572.44, 57),
        ("BA", 100, 65.16, 12, 177.16, 17),
    ],
)
def test_express_shipping_is_charged(state, price, shipping, tax, total, points):
    result = process_order(
        {"name": "Ana", "type": "regular"},
        [{"name": "Produto", "price": price, "qty": 1, "weight": 2}],
        state=state,
        express=True,
    )
    assert result["shipping"] == shipping
    assert result["tax"] == tax
    assert result["total"] == total
    assert result["points"] == points


@pytest.mark.parametrize(
    "names,expected",
    [
        ([], []),
        (["A", "B", "C"], []),
        (["A", "A", "A"], ["A"]),
        (["A", "B", "B", "A"], ["A", "B"]),
        (["C", "A", "B", "B", "C", "A"], ["C", "A", "B"]),
    ],
)
def test_duplicate_names_keep_first_occurrence_order(names, expected):
    assert busca_duplicados([{"name": name} for name in names]) == expected


def test_empty_order_preserves_legacy_shipping():
    assert process_order({"name": "Ana", "type": "regular"}, []) == {
        "customer": "Ana",
        "subtotal": 0,
        "discount": 0,
        "shipping": 20,
        "tax": 0,
        "total": 20,
        "points": 2,
        "duplicate_products": [],
    }


def test_nonpositive_quantities_preserve_legacy_behavior():
    items = [
        {"name": "A", "price": 100, "qty": 1, "weight": 2},
        {"name": "B", "price": 1000, "qty": 0, "weight": 9},
        {"name": "C", "price": 1000, "qty": -1, "weight": 3},
    ]
    result = process_order({"name": "Ana", "type": "regular"}, items)
    assert result["subtotal"] == 100
    assert result["shipping"] == 19.60
    assert result["tax"] == 7
    assert result["total"] == 126.60
    assert result["points"] == 12


def test_points_use_total_before_rounding():
    result = process_order(
        {"name": "Ana", "type": "regular"},
        [{"name": "Produto", "price": 74.765, "qty": 1}],
    )
    assert result["total"] == 100
    assert result["points"] == 9


def test_fractional_subtotal_without_coupon_keeps_console_discount(capsys):
    process_order(
        {"name": "Ana", "type": "regular"},
        [{"name": "Produto", "price": 19.995, "qty": 1}],
    )
    assert "Desconto: 0\n" in capsys.readouterr().out


def test_pure_calculation_does_not_mutate_inputs_or_history(capsys):
    customer = {"name": "Ana", "type": "regular"}
    items = [{"name": "Produto", "price": 100, "qty": 1}]
    original = deepcopy((customer, items))
    result = calcula_pedido(customer, items)
    assert result["total"] == 127
    assert (customer, items) == original
    assert ORDERS_PROCESSED == []
    assert capsys.readouterr().out == ""


def test_process_order_preserves_history_and_console_output(capsys):
    customer = {"name": "Ana", "type": "regular"}
    items = [{"name": "Produto", "price": 100, "qty": 1}]
    original = deepcopy((customer, items))
    first = process_order(customer, items)
    second = process_order(customer, items)
    assert (customer, items) == original
    history = ORDERS_PROCESSED[:]
    assert history == [first, second]
    assert ORDERS_PROCESSED[0] is first
    assert ORDERS_PROCESSED[1] is second
    assert (
        capsys.readouterr().out
        == (
            "Pedido processado para Ana\n"
            "Subtotal: 100\n"
            "Desconto: 0\n"
            "Frete: 20.0\n"
            "Imposto: 7.000000000000001\n"
            "TOTAL: 127.0\n"
        )
        * 2
    )


@pytest.mark.parametrize(
    "discount,subtotal,coupon,customer_type,expected",
    [
        (0, 400, "PROMO10", "regular", 360),
        (100, 500, "PROMO20", "employee", 375),
        (10, 100, "VIP50", "vip", 75),
    ],
)
def test_existing_discounted_value_helper_remains_compatible(
    discount, subtotal, coupon, customer_type, expected
):
    assert (
        calc_valor_com_desconto(discount, subtotal, coupon, customer_type) == expected
    )
