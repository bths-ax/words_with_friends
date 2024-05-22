import csv
from copy import copy
from sys import maxsize
from difflib import SequenceMatcher


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
    if len(minterms) == 0:  # stupid edge case not generating implicants
        return 0

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


ssd_letter_segments = {
    "a": [1, 1, 1, 0, 1, 1, 1],
    "b": [0, 0, 1, 1, 1, 1, 1],
    "c": [1, 0, 0, 1, 1, 1, 0],  # uppercase
    # "c": [0, 0, 0, 1, 1, 0, 1],  # lowercase
    "d": [0, 1, 1, 1, 1, 0, 1],
    "e": [1, 0, 0, 1, 1, 1, 1],
    "f": [1, 0, 0, 0, 1, 1, 1],
    "g": [1, 1, 1, 1, 0, 1, 1],
    "h": [0, 1, 1, 0, 1, 1, 1],
    "i": [0, 0, 0, 0, 1, 1, 0],
    "j": [0, 1, 1, 1, 1, 0, 0],
    "k": [0, 1, 1, 0, 1, 1, 1],
    "l": [0, 0, 0, 1, 1, 1, 0],
    "m": [1, 0, 1, 0, 1, 0, 0],
    "n": [0, 0, 1, 0, 1, 0, 1],
    "o": [1, 1, 1, 1, 1, 1, 0],  # uppercase
    # "o": [0, 0, 1, 1, 1, 0, 1],  # lowercase
    "p": [1, 1, 0, 0, 1, 1, 1],
    "q": [1, 1, 1, 0, 0, 1, 1],
    "r": [0, 0, 0, 0, 1, 0, 1],
    "s": [1, 0, 1, 1, 0, 1, 1],
    "t": [0, 0, 0, 1, 1, 1, 1],
    "u": [0, 1, 1, 1, 1, 1, 0],  # uppercase
    # "u": [0, 0, 1, 1, 1, 0, 0],  # lowercase
    "v": [0, 1, 0, 1, 0, 1, 0],
    "w": [0, 1, 0, 1, 0, 1, 0],
    "x": [0, 1, 1, 0, 1, 1, 1],
    "y": [0, 1, 1, 1, 0, 1, 1],
    "z": [1, 1, 0, 1, 1, 0, 1],
}


# nice inconsistent and confusing function names bruh
def calculate_total_operations(word1: str, word2: str):
    state_graph = []
    for i in range(16):
        # Da, Db, Dc, a, b, c, d, e, f, g
        # -1 as the don't care condition
        state_graph.append([-1] * 10)

    uniq_letters = list(set(word1 + word2))
    uniq_letters.sort()

    letter_states = {letter: state for state, letter in enumerate(uniq_letters)}

    # Da, Db, Dc for En = 0
    for i in range(0, len(word1)):
        letter = word1[i]
        next_letter = word1[(i + 1) % len(word1)]

        state = letter_states[letter]
        next_state = letter_states[next_letter]

        state_graph[state][0] = next_state & 0b001
        state_graph[state][1] = (next_state & 0b010) >> 1
        state_graph[state][2] = (next_state & 0b100) >> 2

    # Da, Db, Dc for En = 1
    for i in range(0, len(word2)):
        # dont u hate it when ur code is repetitive enough to need abstraction
        # but not abstract enough to be able to utilize it
        letter = word2[i]
        next_letter = word2[(i + 1) % len(word2)]

        state = letter_states[letter] | 0b1000
        next_state = letter_states[next_letter]

        state_graph[state][0] = next_state & 0b001
        state_graph[state][1] = (next_state & 0b010) >> 1
        state_graph[state][2] = (next_state & 0b100) >> 2

    # Da, Db, Dc for unused letter states
    # Occurs when a letter is not used in a certain En configuration, so we can reset it to the
    # first letter in the word that should be displayed
    for state, letter in enumerate(uniq_letters):
        word1_start = letter_states[word1[0]]
        word2_start = letter_states[word2[0]]

        en_state = state | 0b1000

        if state_graph[state][0] == -1:
            state_graph[state][0] = word1_start & 0b001
            state_graph[state][1] = (word1_start & 0b010) >> 1
            state_graph[state][2] = (word1_start & 0b100) >> 2

        if state_graph[en_state][0] == -1:
            # smth tells me i should just make this a function at this point
            state_graph[en_state][0] = word2_start & 0b001
            state_graph[en_state][1] = (word2_start & 0b010) >> 1
            state_graph[en_state][2] = (word2_start & 0b100) >> 2

    # a, b, c, d, e, f, g
    for state, letter in enumerate(uniq_letters):
        en_state = state | 0b1000
        ssd_segments = ssd_letter_segments[letter]
        state_graph[state][3:10] = ssd_segments
        state_graph[en_state][3:10] = ssd_segments

    """ autoformatter was having a bad day with this one
    for i in range(0, 16):
        letter_idx = i & 0b111
        print(
            "{} ({:04b})".format(
                uniq_letters[letter_idx] if letter_idx < len(uniq_letters) else "_", i
            ),
            end=" ",
        )
        for j in range(0, 10):
            print(state_graph[i][j], end=" ")
        print()
    """

    # Calculate total operations by using each column as a k-map
    total_operations = 0

    for i in range(0, 10):
        minterms = []
        dont_cares = []

        for state in range(0, 16):
            if state_graph[state][i] == 1:
                minterms.append(state)
            if state_graph[state][i] == -1:
                dont_cares.append(state)

        total_operations += calculate_minimum_operations(minterms, dont_cares)

    return total_operations


# Populate word list
dictionary = []

with open("dictionary.txt", "r") as dictionary_file:
    for word in dictionary_file:
        dictionary.append(word.strip().lower())

# Rule 1: Minimum length of 4 letters per word
dictionary = [word for word in dictionary if len(word) >= 4]

# Rule 2: No duplicate letters allowed
dictionary = [word for word in dictionary if len(word) == len(set(word))]

dictionary.sort()

# Find valid word combinations

combinations = []

for i in range(0, len(dictionary)):
    for j in range(i + 1, len(dictionary)):
        word_i = dictionary[i]
        word_j = dictionary[j]

        # Rule 3: Must have a combined length of 10 letters
        if len(word_i) + len(word_j) < 10:
            continue

        uniq_letters = list(set(word_i + word_j))

        required_states = len(uniq_letters)
        # Rule 4: Use a minimum of 6 states
        if required_states < 6:
            continue
        # Rule 5: Use a maximum of 8 states (or add a third state variable)
        if required_states > 8:
            continue

        # Rule 6: Cannot have more than 2 consecutive letters that match
        matcher = SequenceMatcher(None, word_i, word_j)
        longest_match = matcher.find_longest_match(0, len(word_i), 0, len(word_j))
        if longest_match.size > 2:
            continue

        # Test word combination
        combination = {
            "word1": word_i,
            "word2": word_j,
            "ops": calculate_total_operations(word_i, word_j),
        }
        combinations.append(combination)

        print(
            "{:10s} {:10s} -> {} operations".format(
                combination["word1"], combination["word2"], combination["ops"]
            )
        )

combinations.sort(key=lambda combo: combo["ops"])

with open("combinations.csv", "w") as combinations_file:
    combinations_writer = csv.writer(combinations_file)
    for combination in combinations:
        combinations_writer.writerow(
            [
                combination["word1"],
                combination["word2"],
                combination["ops"],
            ]
        )
