from copy import copy
from sys import maxsize


class Implicant:
    def __init__(self, minterm):
        self.terms = 1 << minterm
        self.value = minterm
        self.mask = 0

    def __str__(self):
        # funny hacky debugging solution
        terms = ",".join([str(i) for i in range(0, 16) if self.terms & (1 << i) != 0])
        return "Impl {:04b} ({:d}), Mask {:04b}, Terms {:s}".format(
            self.value, self.value, self.mask, terms
        )

    # for dealing w sets ugh
    def __eq__(self, other):
        return (
            self.terms == other.terms
            and self.value == other.value
            and self.mask == other.mask
        )

    def __hash__(self):
        return self.terms + self.value + self.mask


def calculate_minimum_operations(minterms: list[int], dont_cares: list[int]):
    # ill document this code on the day that python becomes a good language (never)
    implicants = [Implicant(minterm) for minterm in minterms]
    implicants += [Implicant(dont_care) for dont_care in dont_cares]

    all_implicants: list[Implicant] = []

    minterms_bitfield = 0
    for minterm in minterms:
        minterms_bitfield |= 1 << minterm

    # Find implicants by combining minterms
    while True:
        if len(implicants) == 0:
            break

        for impl in implicants:
            all_implicants.append(impl)

        combinations = set()

        for i in range(0, len(implicants)):
            for j in range(i + 1, len(implicants)):
                impl_i = implicants[i]
                impl_j = implicants[j]
                if impl_i.mask != impl_j.mask:
                    continue

                mask_ij = impl_i.value ^ impl_j.value
                if mask_ij.bit_count() != 1:
                    continue

                combined = copy(impl_i)
                combined.terms |= impl_j.terms
                combined.value |= mask_ij
                combined.mask |= mask_ij
                combinations.add(combined)

        implicants = list(combinations)

    # Find prime implicants by reducing subimplicants
    def is_contained_by_implicant(implicant):
        for impl in all_implicants:
            if impl != implicant and impl.terms & implicant.terms == implicant.terms:
                return True
        return False

    # who cares about O(n^2) when ur solution is already O(2^n) amirite
    prime_implicants = [
        impl for impl in all_implicants if not is_contained_by_implicant(impl)
    ]

    # Find essential prime implicants by brute force (petricks method is too tedious for 4 vars)
    # Calculate the amount of AOI operations required to build the expression
    # This does NOT output the simplified expression (i could, but i just need the min ops)
    minimum_operations = maxsize
    # minimum_inclusion = 0

    for inclusion_bitfield in range(1, 2 ** len(prime_implicants)):
        included_terms = 0
        required_operations = inclusion_bitfield.bit_count() - 1

        for i in range(0, len(prime_implicants)):
            # bitwise operators my one true love
            if inclusion_bitfield & (1 << i) != 0:
                impl = prime_implicants[i]
                included_terms |= impl.terms
                required_operations += 3 - impl.mask.bit_count()

        if included_terms & minterms_bitfield == minterms_bitfield:
            if required_operations < minimum_operations:
                minimum_operations = required_operations
                # minimum_inclusion = inclusion_bitfield

    return minimum_operations


print(calculate_minimum_operations([4, 8, 10, 11, 12, 15], [9, 14]))  # 6
