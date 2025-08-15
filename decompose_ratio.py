from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import argparse
from typing import Tuple


_MAX = 32
_MAX_PRODUCT = _MAX * _MAX


@lru_cache(maxsize=None)
def _factor_pairs_le_32(x: int) -> Tuple[Tuple[int, int], ...]:
    """
    All (a, b) with 1 ≤ a, b ≤ 32 and a * b == x.
    """
    pairs = []
    upper = min(_MAX, x)
    for a in range(1, upper + 1):
        if x % a == 0:
            b = x // a
            if b <= _MAX:
                pairs.append((a, b))
    return tuple(pairs)


def decompose_ratio(M: int, N: int) -> tuple[int, int, int, int]:
    """
    Return M1, M2, N1, N2 such that:
      - (M1 * M2) / (N1 * N2) == M / N   (exactly)
      - max(|M1|, |M2|, |N1|, |N2|) ≤ 32
      - N1 and N2 are strictly positive (no division by zero)

    Raises:
      - ZeroDivisionError if N == 0
      - ValueError if no such decomposition exists

    Notes:
      - If M/N < 0, the sign is placed on M1 (negative allowed for numerators).
      - If M == 0, returns (0, 1, 1, 1).
    """
    if N == 0:
        raise ZeroDivisionError("N must be non-zero")

    f = Fraction(M, N)
    if f == 0:
        return (0, 1, 1, 1)

    sign = -1 if f < 0 else 1
    a = abs(f.numerator)
    b = f.denominator

    # Quick win if already within bounds
    if a <= _MAX and b <= _MAX:
        return (sign * a, 1, b, 1)

    # Find k such that a*k and b*k each factor into two numbers ≤ 32
    max_k = _MAX_PRODUCT // max(a, b)
    for k in range(1, max_k + 1):
        num = a * k
        den = b * k
        num_pairs = _factor_pairs_le_32(num)
        if not num_pairs:
            continue
        den_pairs = _factor_pairs_le_32(den)
        if not den_pairs:
            continue

        # Prefer balanced pairs (closer factors)
        def score(pair: tuple[int, int]) -> int:
            x, y = pair
            return abs(x - y)

        m1, m2 = min(num_pairs, key=score)
        n1, n2 = min(den_pairs, key=score)
        return (sign * m1, m2, n1, n2)

    raise ValueError(f"No decomposition with each value ≤ {_MAX} exists for ratio {M}/{N}")


def _main() -> None:
    parser = argparse.ArgumentParser(description="Decompose ratio M/N into M1*M2/(N1*N2) with each ≤ 32")
    parser.add_argument("--M", type=int, required=True, help="Numerator M")
    parser.add_argument("--N", type=int, required=True, help="Denominator N")
    args = parser.parse_args()

    m1, m2, n1, n2 = decompose_ratio(args.M, args.N)
    print(f"M1={m1} M2={m2} N1={n1} N2={n2}")


if __name__ == "__main__":
    _main()