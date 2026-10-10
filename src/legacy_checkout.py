"""Regras do checkout legado, com cálculos separados dos efeitos colaterais."""

from collections import Counter


ORDERS_PROCESSED = []

VIP_DISCOUNT_THRESHOLD = 1000
VIP_DISCOUNT_RATE = 0.10
VIP_HIGH_DISCOUNT_RATE = 0.15
EMPLOYEE_DISCOUNT_RATE = 0.20
REGULAR_DISCOUNT_THRESHOLD = 800
REGULAR_DISCOUNT_RATE = 0.05
MAX_DISCOUNT_RATE = 0.25
COUPON_RATES = {"PROMO10": 0.10, "PROMO20": 0.20}
PROMO20_THRESHOLD = 500
VIP_COUPON_AMOUNT = 50

FREE_SHIPPING_THRESHOLD = 500
REGIONAL_SHIPPING_BASE = 20
REGIONAL_SHIPPING_WEIGHT_RATE = 0.4
DEFAULT_SHIPPING_BASE = 35
DEFAULT_SHIPPING_WEIGHT_RATE = 0.6
EXPRESS_SHIPPING_MULTIPLIER = 1.8
REGIONAL_STATES = {"MG", "SP", "RJ", "ES"}
TAX_RATES = {"MG": 0.07, "SP": 0.09, "RJ": 0.08, "ES": 0.07}
DEFAULT_TAX_RATE = 0.12
VIP_POINTS_DIVISOR = 5
DEFAULT_POINTS_DIVISOR = 10


def calc_subtotal(items):
    """Some apenas os itens com quantidade positiva, como no legado."""
    return sum(item["price"] * item["qty"] for item in items if item["qty"] > 0)


def calc_desconto(customer_type, subtotal):
    """Calcule o desconto do cliente, ainda sem aplicar cupom ou limite."""
    if customer_type == "vip":
        taxa = (
            VIP_HIGH_DISCOUNT_RATE
            if subtotal >= VIP_DISCOUNT_THRESHOLD
            else VIP_DISCOUNT_RATE
        )
        return subtotal * taxa
    if customer_type == "employee":
        return subtotal * EMPLOYEE_DISCOUNT_RATE
    if customer_type == "regular" and subtotal >= REGULAR_DISCOUNT_THRESHOLD:
        return subtotal * REGULAR_DISCOUNT_RATE
    return 0


def calc_desconto_total(desconto, subtotal, coupon, customer_type):
    """Acumule o cupom e limite o desconto total a 25% do subtotal."""
    if coupon == "PROMO20" and subtotal < PROMO20_THRESHOLD:
        desconto_cupom = 0
    else:
        taxa_cupom = COUPON_RATES.get(coupon, 0)
        desconto_cupom = subtotal * taxa_cupom if taxa_cupom else 0
    if coupon == "VIP50" and customer_type == "vip":
        desconto_cupom = VIP_COUPON_AMOUNT
    return min(desconto + desconto_cupom, subtotal * MAX_DISCOUNT_RATE)


def calc_valor_com_desconto(desconto, subtotal, coupon, customer_type):
    """Mantenha a interface da função existente para outros chamadores."""
    return subtotal - calc_desconto_total(desconto, subtotal, coupon, customer_type)


def calc_peso_total(items):
    """Peso ausente vale zero; quantidades seguem o comportamento legado."""
    return sum(item.get("weight", 0) * item["qty"] for item in items)


def calc_frete(state, peso, subtotal, express):
    """O frete grátis usa o subtotal original e exclui entregas expressas."""
    if subtotal >= FREE_SHIPPING_THRESHOLD and not express:
        return 0
    if state in REGIONAL_STATES:
        frete = REGIONAL_SHIPPING_BASE + peso * REGIONAL_SHIPPING_WEIGHT_RATE
    else:
        frete = DEFAULT_SHIPPING_BASE + peso * DEFAULT_SHIPPING_WEIGHT_RATE
    if express:
        frete *= EXPRESS_SHIPPING_MULTIPLIER
    return frete


def calc_imposto(state, valor_com_desconto):
    """Incida o imposto somente sobre os produtos após o desconto."""
    return valor_com_desconto * TAX_RATES.get(state, DEFAULT_TAX_RATE)


def calc_pontos(customer_type, valor_com_desconto, frete, imposto):
    """Trunque os pontos usando os valores antes do arredondamento."""
    divisor = VIP_POINTS_DIVISOR if customer_type == "vip" else DEFAULT_POINTS_DIVISOR
    return int((valor_com_desconto + frete + imposto) / divisor)


def busca_duplicados(items):
    """Conte em O(n), preservando a ordem da primeira ocorrência dos nomes."""
    contagens = Counter(item["name"] for item in items)
    return [nome for nome, quantidade in contagens.items() if quantidade > 1]


def _calcula_valores(customer, items, coupon, state, express):
    """Calcule os valores sem arredondamento e sem efeitos colaterais."""
    customer_type = customer["type"]
    subtotal = calc_subtotal(items)
    desconto_cliente = calc_desconto(customer_type, subtotal)
    desconto = calc_desconto_total(desconto_cliente, subtotal, coupon, customer_type)
    valor_com_desconto = subtotal - desconto
    frete = calc_frete(state, calc_peso_total(items), subtotal, express)
    imposto = calc_imposto(state, valor_com_desconto)
    return {
        "customer": customer["name"],
        "subtotal": subtotal,
        "discount": desconto,
        "shipping": frete,
        "tax": imposto,
        "total": valor_com_desconto + frete + imposto,
        "points": calc_pontos(customer_type, valor_com_desconto, frete, imposto),
        "duplicate_products": busca_duplicados(items),
    }


def _formata_resultado(valores):
    """Arredonde somente os campos monetários na saída pública."""
    resultado = valores.copy()
    for campo in ("subtotal", "discount", "shipping", "tax", "total"):
        resultado[campo] = round(resultado[campo], 2)
    return resultado


def calcula_pedido(customer, items, coupon="", state="MG", express=False):
    """Calcule o resultado sem imprimir, armazenar ou alterar as entradas."""
    return _formata_resultado(_calcula_valores(customer, items, coupon, state, express))


def _imprime_resumo(valores, resultado):
    """Preserve as mensagens e os valores não arredondados do legado."""
    print("Pedido processado para " + valores["customer"])
    print("Subtotal:", valores["subtotal"])
    print("Desconto:", valores["discount"])
    print("Frete:", valores["shipping"])
    print("Imposto:", valores["tax"])
    print("TOTAL:", resultado["total"])


def process_order(customer, items, coupon="", state="MG", express=False):
    """Preserve a API, o histórico global e as mensagens do checkout."""
    valores = _calcula_valores(customer, items, coupon, state, express)
    resultado = _formata_resultado(valores)
    ORDERS_PROCESSED.append(resultado)
    _imprime_resumo(valores, resultado)
    return resultado
