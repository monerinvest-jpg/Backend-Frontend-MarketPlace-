from decimal import Decimal


def buyer_reward_eligible(first_order_total: Decimal, min_amount: Decimal) -> bool:
    return first_order_total >= min_amount


def allowed_bonus_writeoff(total: Decimal, max_percent: Decimal) -> Decimal:
    return (total * max_percent / Decimal("100")).quantize(Decimal("0.01"))
