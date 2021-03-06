import util, math, random
from collections import defaultdict
from util import ValueIteration
from util import simulate, RLAlgorithm, FixedRLAlgorithm


############################################################
# Problem 2a

# If you decide 2a is true, prove it in blackjack.pdf and put "return None" for
# the code blocks below.  If you decide that 2a is false, construct a counterexample.
class CounterexampleMDP(util.MDP):
    def startState(self):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return 0
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

    # Return set of actions possible from |state|.
    def actions(self, state):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return [-1, 1] if state == 0 else [state]
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return [(-1, 0.9, 0), (1, 0.1, 100)] if state == 0 else [(state, 1, 0)]
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

    def discount(self):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return 1
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

############################################################
# Problem 3a

class BlackjackMDP(util.MDP):
    def __init__(self, cardValues, multiplicity, threshold, peekCost):
        """
        cardValues: array of card values for each card type
        multiplicity: number of each card type
        threshold: maximum total before going bust
        peekCost: how much it costs to peek at the next card
        """
        self.cardValues = cardValues
        self.multiplicity = multiplicity
        self.threshold = threshold
        self.peekCost = peekCost

    # Return the start state.
    # Look at this function to learn about the state representation.
    # The first element of the tuple is the sum of the cards in the player's
    # hand.
    # The second element is the index (not the value) of the next card, if the player peeked in the
    # last action.  If they didn't peek, this will be None.
    # The final element is the current deck.
    def startState(self):
        return (0, None, (self.multiplicity,) * len(self.cardValues))  # total, next card (if any), multiplicity for each card

    # Return set of actions possible from |state|.
    # You do not need to modify this function.
    # All logic for dealing with end states should be done in succAndProbReward
    def actions(self, state):
        return ['Take', 'Peek', 'Quit']

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.  Indicate a terminal state (after quitting or
    # busting) by setting the deck to None.
    # When the probability is 0 for a particular transition, don't include that
    # in the list returned by succAndProbReward.
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE (our solution is 53 lines of code, but don't worry if you deviate from this)

        # (totalCardValueInHand, nextCardIndexIfPeeked, deckCardCounts)
        totalValue, peekedIndex, deckCardNum = state

        # Setting the deck to None signifies the end of the game
        if deckCardNum == None:
            return []

        allStates = []
        if action == 'Quit':   # If she quits, then the resulting state will be (x, None, None)
            return [((totalValue, None, None), 1, totalValue)]

        if action == 'Peek':
            if peekedIndex:
                return []
            for i in range(len(deckCardNum)):
                if deckCardNum[i]:   # index of cards which are still on the deck, starts from 0
                    peekProb = float(deckCardNum[i]) / sum(deckCardNum)
                    allStates.append(((totalValue, i, deckCardNum), peekProb, -self.peekCost))
            return allStates

        if action == 'Take':
            # If it is to be peeked
            if peekedIndex:
                totalValue += self.cardValues[peekedIndex]
                if totalValue > self.threshold:
                    # the deck is set to None to signify the game ended with a bust
                    return [((totalValue, None, None), 1, 0)]
                else:
                    # Notice: tuple is unchangeable
                    listDeckCardNum = list(deckCardNum)
                    listDeckCardNum[peekedIndex] -= 1
                    if sum(listDeckCardNum) == 0:
                        return [((totalValue, None, None), 1, totalValue)]
                    else:
                        return [((totalValue, None, tuple(listDeckCardNum)), 1, 0)]
            else:
                for i in range(0, len(deckCardNum)):
                    if deckCardNum[i]:
                        takeProb = float(deckCardNum[i]) / sum(deckCardNum)
                        newTotalValue = totalValue + self.cardValues[i]
                        if newTotalValue > self.threshold:
                            allStates.append(((newTotalValue, None, None), takeProb, 0))
                        else:
                            listDeckCardNum = list(deckCardNum)
                            listDeckCardNum[i] -= 1
                            if sum(listDeckCardNum) == 0:
                                allStates.append(((newTotalValue, None, None), takeProb, newTotalValue))
                            else:
                                allStates.append(((newTotalValue, None, tuple(listDeckCardNum)), takeProb, 0))
                return allStates
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

    def discount(self):
        return 1

############################################################
# Problem 3b

def peekingMDP():
    """
    Return an instance of BlackjackMDP where peeking is the optimal action at
    least 10% of the time.
    """
    # BEGIN_YOUR_CODE (our solution is 2 lines of code, but don't worry if you deviate from this)
    return BlackjackMDP(cardValues=[1, 2, 3, 4, 5, 100], multiplicity=1, threshold=20, peekCost=1)
    # raise Exception("Not implemented yet")
    # END_YOUR_CODE

############################################################
# Problem 4a: Q learning

# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action
class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):   # (feature name, feature value) pairs
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            return max((self.getQ(state, action), action) for action in self.actions(state))[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        # BEGIN_YOUR_CODE (our solution is 12 lines of code, but don't worry if you deviate from this)
        Vopt = 0
        if newState != None:   # Note that if s is a terminal state, then s' will be None.
            Vopt = max((self.getQ(newState, nextAction), nextAction) for nextAction in self.actions(newState))[0]
        prediction = self.getQ(state, action)
        target = reward + self.discount * Vopt
        alpha = self.getStepSize()
        scale = alpha * (target - prediction)
        for f, v in self.featureExtractor(state, action):
            self.weights[f] += scale * v
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

# Return a singleton list containing indicator feature for the (state, action)
# pair.  Provides no generalization.
def identityFeatureExtractor(state, action):
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

############################################################
# Problem 4b: convergence of Q-learning
# Small test case
smallMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=10, peekCost=1)

# rl = QLearningAlgorithm(smallMDP.actions, smallMDP.discount(), identityFeatureExtractor, explorationProb=0)
# util.simulate(smallMDP, rl, numTrials=30000, maxIterations=1000, verbose=False, sort=False)
# smallMDP.computeStates()
# policy_rl={}
# for s in smallMDP.states:
#     policy_rl[s]=rl.getAction(s)
#
# val = util.ValueIteration()
# val.solve(smallMDP)
# policy_val=val.pi
#
# intersection = [1 if policy_rl[k] == policy_val[k] else 0 for k in policy_rl ]
# print float(sum(intersection))/len(policy_rl)

# Large test case
largeMDP = BlackjackMDP(cardValues=[1, 3, 5, 8, 10], multiplicity=3, threshold=40, peekCost=1)
largeMDP.computeStates()

# rl = QLearningAlgorithm(largeMDP.actions, largeMDP.discount(), identityFeatureExtractor, explorationProb=0)
# util.simulate(largeMDP, rl, numTrials=30000, maxIterations=1000, verbose=False, sort=False)
# largeMDP.computeStates()
# policy_rl={}
# for s in largeMDP.states:
#     policy_rl[s]=rl.getAction(s)
#
# val = util.ValueIteration()
# val.solve(largeMDP)
# policy_val=val.pi
#
# intersection = [1 if policy_rl[k] == policy_val[k] else 0 for k in policy_rl ]
# print float(sum(intersection))/len(policy_rl)


############################################################
# Problem 4c: features for Q-learning.

# You should return a list of (feature key, feature value) pairs (see
# identityFeatureExtractor()).
# Implement the following features:
# - indicator on the total and the action (1 feature).
# - indicator on the presence/absence of each card and the action (1 feature).
#       Example: if the deck is (3, 4, 0, 2), then your indicator on the presence of each card is (1,1,0,1)
#       Only add this feature if the deck != None
# - indicator on the number of cards for each card type and the action (len(counts) features).  Only add these features if the deck != None
def blackjackFeatureExtractor(state, action):
    # total, nextCard, counts = state
    # BEGIN_YOUR_CODE (our solution is 9 lines of code, but don't worry if you deviate from this)
    totalValue, peekedIndex, deckCardNum = state

    features = []
    features.append(((totalValue, action), 1))
    if deckCardNum != None:
        features.append(((tuple([1 if x else 0 for x in deckCardNum]), action), 1))
    if deckCardNum != None:
        for i in range(len(deckCardNum)):
            features.append(((i, deckCardNum[i], action), 1))
    return features
    # raise Exception("Not implemented yet")
    # END_YOUR_CODE

############################################################
# Problem 4d: What happens when the MDP changes underneath you?!

# Original mdp
originalMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=10, peekCost=1)

# New threshold
newThresholdMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=15, peekCost=1)

# # Run value iteration on originalMDP to compute an optimal policy.
# val = util.ValueIteration()
# val.solve(originalMDP)
# policy_val=val.pi
#
# # Then apply your policy to newThresholdMDP by calling simulate with FixedRLAlgorithm,
# # instantiated using your computed policy.
# rl = FixedRLAlgorithm(policy_val)
# print(sum(util.simulate(newThresholdMDP, rl, numTrials=30000, maxIterations=1000, verbose=False, sort=False)))
#
# # What happens if you run Q learning on newThresholdMDP instead?
# rl = QLearningAlgorithm(newThresholdMDP.actions, newThresholdMDP.discount(), identityFeatureExtractor, explorationProb=0)
# print(sum(util.simulate(newThresholdMDP, rl, numTrials=30000, maxIterations=1000, verbose=False, sort=False)))
