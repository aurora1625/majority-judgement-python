from majority_judgement import MajorityJudgement
import pytest

class TestMajorityJudgementSoundness:
    example_votes = [
      [1,1,1,1,1,1,1,1],
      [1,2,3],
      [13],
      [1, 13, 12, 11, 1],
      [1, 1, 1, 1],
      [2,3],
      [2,1,3],
      [10,1,10],
      [1,3,2],
      [10], 
      [9],
      [10], 
      [9, 1]
    ]

    on_all_examples = pytest.mark.parametrize("x", example_votes)

    @on_all_examples
    def test_tallies(self, x):
      tallies = [0 for _ in x]
      for i in MajorityJudgement(x): tallies[i] = tallies[i] + 1
      assert x == tallies

    @on_all_examples
    def test_not_less_than_self(self, x):
      assert MajorityJudgement(x) >= MajorityJudgement(x)

    @on_all_examples
    def test_front_loading_moves_earlier(self, x):
      for i in xrange(1, len(x)):
        y = list(x)
        y[i] = y[i] - 1
        y[i-1] = y[i-1] + 1
        assert MajorityJudgement(y) < MajorityJudgement(x)

    @on_all_examples
    def test_equality_of_same_input(self, x):
      x = MajorityJudgement(x)
      assert x == x

    @on_all_examples
    def test_calling_list_twice_produces_same_result(self, x):
      x = MajorityJudgement(x)
      assert list(x) == list(x)


    @on_all_examples
    def test_equality_of_identical_inputs(self, x):
      assert MajorityJudgement(x) == MajorityJudgement(x)

    @pytest.mark.parametrize(("x", "y"), [
      (x, y) for x in example_votes for y in example_votes if x != y 
    ])
    def test_inequality_of_different_inputs(self, x, y):
      assert MajorityJudgement(x) != MajorityJudgement(y)

    @on_all_examples
    def test_length_agrees_with_list(self, x):
      assert len(MajorityJudgement(x)) == len(list(MajorityJudgement(x)))
    
    @on_all_examples
    def test_length_agrees_with_list_when_evaluated(self, x):
      x = MajorityJudgement(x)
      y = list(x)
      assert len(x) == len(y)

    @on_all_examples
    def test_correct_number(self, x):
      total = sum(x)
      assert len(list(MajorityJudgement(x))) == total
     
    @on_all_examples 
    def test_index_matches_list_index(self, x):
      def index_test(x):
        index_result = []
        for i in xrange(0, sum(x)): index_result.append(MajorityJudgement(x)[i])

        list_result = list(MajorityJudgement(x))
        assert index_result == list_result

      index_test([10])
      index_test([1, 2, 3])
      index_test([1,6,1])

    @pytest.mark.parametrize(("x", "m"), [
      ([1,1,1,1], 1),
      ([5,1,1,5], 1),
      ([5,1,1,6], 2),
      ([1,1,1,1,20], 4)
    ])
    def test_starts_with_median(self, x, m):
      assert MajorityJudgement(x)[0] == m

    @pytest.mark.parametrize(("x", "y", "k"), [(x, y,k) 
      for x in example_votes 
      for y in example_votes 
      if sum(x) == sum(y) and x != y
      for k in xrange(sum(x) / 2)
    ])
    def test_can_drop_outliers(self, x, y, k):
      assert sum(x) == sum(y)
      x1 = MajorityJudgement(x)
      y1 = MajorityJudgement(y)

      def drop_outliers(l, k):
        l = list(l)
        for r in [xrange(len(l)), reversed(xrange(len(l)))]:
          k2 = k
          for i in r:
            if l[i] >= k2:
              l[i] = l[i] - k2
              break
            else:
              k2 = k2 - l[i]
              l[i] = 0
        return l

      x2 = MajorityJudgement(drop_outliers(x, k))
      y2 = MajorityJudgement(drop_outliers(y, k))

      if x1 <= y1: assert x2 <= y2
      else: assert y2 <= x2
