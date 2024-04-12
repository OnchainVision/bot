
def get_amount_out(amount_in, reserve_in, reserve_out):
    """
    Given an input amount of an asset and pair reserves, returns the maximum output amount of the other asset.
    """
    if amount_in <= 0:
        raise ValueError('INSUFFICIENT_INPUT_AMOUNT')

    if reserve_in <= 0 or reserve_out <= 0:
        raise ValueError('INSUFFICIENT_LIQUIDITY')

    amount_in_with_fee = amount_in * 997
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in * 1000 + amount_in_with_fee
    amount_out = numerator // denominator
    return amount_out

def get_amount_in(amount_out, reserve_in, reserve_out):
    """
    Given an output amount of an asset and pair reserves, returns a required input amount of the other asset.
    """
    if amount_out <= 0:
        raise ValueError('INSUFFICIENT_OUTPUT_AMOUNT')

    if reserve_in <= 0 or reserve_out <= 0:
        raise ValueError('INSUFFICIENT_LIQUIDITY')

    numerator = reserve_in * amount_out * 1000
    denominator = reserve_out - amount_out * 997
    amount_in = numerator // denominator + 1
    return amount_in

