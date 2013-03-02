"""
Majority Judgement is a method of voting proposed by Michel Balinski
and Rida Laraki in "A theory of measuring, electing, and ranking"
(http://www.pnas.org/content/104/21/8720.full)

Members of the electorate vote by assigning grades to candidates. These grades
can be any ordinal values (numbers, "A,B,C", "Good, Bad,Terrible", etc.
All that matters is the relative ordinal positions of the grades.

In this module we assume that grades are consecutive integer values starting
from 0 as the lowest. Because all that matters is the ordering, any other
grading scheme can be trivially converted to this form.

The essential idea of majority judgement is that we sort the grades assigned to
the candidate in order of most significant to least significant. At any given
point the most significant grade of those left is the lower median of the set
(i.e. the highest grade which at least 50% of the population supports).

So for example given the grading Bad, OK, OK, Good we would convert this to the
sequence

OK, Bad, OK, Good

Another candidate might have the grading

OK, Good, OK, Good

This candidate would win because their second grading is better than the first
candidate's.

This module provides a type which wraps a tally of grades and is then ordered
in terms of the majority judgement. It may then be used to implement a voting
procedure by assigning each candidate their tally and taking the maximum.
"""

import collections
import copy

def _how_many_to_pop(preceding, votes, total):
    return 1 + min(total - 2 * preceding - 1,
                   2 * preceding + 2 * votes - total)

def _calculate_judgement_trail(tallies):
    judgement_trail = []
    tallies = list(tallies)
    tallies_remaining = sum(tallies)
    while len(tallies) > 0:
        tot = 0
        for i in xrange(len(tallies)):  # pragma: no branch
            preceding = tot
            v = tallies[i]
            tot += v
            if 2 * tot >= tallies_remaining:
                if 2 * tot == tallies_remaining:
                    next_index = i+1
                    while not tallies[next_index]:
                        next_index += 1

                    relevant_indices = [i, next_index]
                    votes_to_pop = _how_many_to_pop(preceding,
                                                    v + tallies[next_index],
                                                    tallies_remaining)
                    k = votes_to_pop / 2
                    votes_to_pop = k * 2
                else:
                    relevant_indices = [i]
                    votes_to_pop = _how_many_to_pop(preceding,
                                                    v,
                                                    tallies_remaining)
                    k = votes_to_pop

                tallies_remaining -= votes_to_pop
                for i in relevant_indices:
                    tallies[i] -= k

                while len(tallies) > 0 and tallies[-1] <= 0:
                    tallies.pop()
                r = [relevant_indices, k]
                judgement_trail.append(r)
                break
    return judgement_trail

def retupleize_list(l):
    print l
    hangover = -1

    result = []
    
    for xs, n in l:
        if hangover < 0:
            if len(xs) == 2:
                result.append((tuple(xs), n))
            else:
                x = xs[0]
                if n > 1: result.append(((x, x), n / 2))
                if n % 2 != 0: hangover = x
        else:
            # I actually haven't reasoned through this bit yet.
            # I think we can never have len(xs) == 2 here when the original
            # total passed in is even. Certainly this seems to be true 
            # empirically
            assert len(xs) == 1
            x = xs[0]
            result.append(((hangover, x), 1))
            n -= 1 
            if n > 1: result.append(((x, x), n / 2))
            if n % 2 != 0: hangover = x
            else: hangover = -1

    # We always feed an even total into here so there should never be a hangover
    assert hangover < 0
    print result
    return result 
    

class MajorityJudgement():
    """
    Objects of type MajorityJudgement behave like a lazily evaluated frozen
    list. They may be indexed, iterated over and _compared exactly as if they
    were their list of majority judgement grades.
    """
    def __init__(self, tally):
        """
        Create a MajorityJudgement object from a tally of grades. Note that
        the votes are taken as tallies, not as a list of grades. i.e.
        [1,2,1] means that there is one vote each of grades 0 and 2 and 2 votes
        of grade 1, not that there 2 votes of grade 1 and 1 of grade 2.
        """

        for x in tally:
            if type(x) is not int:
                raise ValueError("Tally counts must be integers: %s" % tally)
            if x < 0:
                raise ValueError("Tally counts may not be negative: %s" % tally)

        tally = [2 * x for x in tally]
        self._judgement_trail = retupleize_list(_calculate_judgement_trail(tally))

    def __repr__(self):
        return "MajorityJudgement(%s)" % (self._judgement_trail)

    def __eq__(self, other):
        return self._compare(other) == 0

    def __ne__(self, other):
        return self._compare(other) != 0

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def _compare(self, other):
        """
            Return an integer expressing the order relation between self and
            other. -1 if self < other, 0 if self == other, 1 if self > other.

            Ordering is defined to be equivalent to lexicographical ordering of
            list(self) and list(other), but may not fully evaluate the sequence
            and may require less iteration due to long stretches of common
            values.
        """
        if self is other:
            return 0
        if not self._judgement_trail and not other._judgement_trail:
            return 0
        if not self._judgement_trail:
            return -1
        if not other._judgement_trail:
            return 1

        self_stack = list(reversed(self._judgement_trail))
        other_stack = list(reversed(other._judgement_trail))

        while self_stack and other_stack:
            x, xn = self_stack.pop()
            y, yn = other_stack.pop()

            m = min(xn, yn)

            assert len(x) == len(y) == 2

            if x < y: return -1
            elif x > y: return 1

            if xn > yn:
                self_stack.append((x, xn - yn))
            elif yn > xn:
                other_stack.append((y, yn - xn))

        if self_stack: return 1
        if other_stack: return -1

        return 0
