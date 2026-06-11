from decimal import Decimal


def calculate_commission(subtotal: Decimal, commission_percent: Decimal) -> tuple[Decimal, Decimal]:
    platform_fee = (subtotal * commission_percent) / Decimal("100")
    seller_net = subtotal - platform_fee
    return platform_fee.quantize(Decimal("0.01")), seller_net.quantize(Decimal("0.01"))
