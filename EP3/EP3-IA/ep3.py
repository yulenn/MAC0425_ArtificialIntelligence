"""
  AO PREENCHER ESSE CABECALHO COM O MEU NOME E O MEU NUMERO USP,
  DECLARO QUE SOU A UNICA PESSOA AUTORA E RESPONSAVEL POR ESSE PROGRAMA.
  TODAS AS PARTES ORIGINAIS DESSE EXERCICIO PROGRAMA (EP) FORAM
  DESENVOLVIDAS E IMPLEMENTADAS POR MIM SEGUINDO AS INSTRUCOES
  DESSE EP E, PORTANTO, NAO CONSTITUEM ATO DE DESONESTIDADE ACADEMICA,
  FALTA DE ETICA OU PLAGIO.
  DECLARO TAMBEM QUE SOU A PESSOA RESPONSAVEL POR TODAS AS COPIAS
  DESSE PROGRAMA E QUE NAO DISTRIBUI OU FACILITEI A
  SUA DISTRIBUICAO. ESTOU CIENTE QUE OS CASOS DE PLAGIO E
  DESONESTIDADE ACADEMICA SERAO TRATADOS SEGUNDO OS CRITERIOS
  DIVULGADOS NA PAGINA DA DISCIPLINA.
  ENTENDO QUE EPS SEM ASSINATURA NAO SERAO CORRIGIDOS E,
  AINDA ASSIM, PODERAO SER PUNIDOS POR DESONESTIDADE ACADEMICA.

  Nome : Nury Yuleny Arosquipa Yanque
  NUSP : 9871836

  Referencias: Com excecao das rotinas fornecidas no enunciado
  e em sala de aula, caso voce tenha utilizado alguma referencia,
  liste-as abaixo para que o seu programa nao seja considerado
  plagio ou irregular.

  Exemplo:
  - O algoritmo Quicksort foi baseado em:
  https://pt.wikipedia.org/wiki/Quicksort
  http://www.ime.usp.br/~pf/algoritmos/aulas/quick.html
"""

import math
import random
from collections import defaultdict
import util
from util import simulate


# **********************************************************
# **            PART 01 Modeling BlackJack                **
# **********************************************************


class BlackjackMDP(util.MDP):
    """
    The BlackjackMDP class is a subclass of MDP that models the BlackJack game as a MDP
    """
    def __init__(self, valores_cartas, multiplicidade, limiar, custo_espiada):
        """
        valores_cartas: list of integers (face values for each card included in the deck)
        multiplicidade: single integer representing the number of cards with each face value
        limiar: maximum number of points (i.e. sum of card values in hand) before going bust
        custo_espiada: how much it costs to peek at the next card
        """
        self.valores_cartas = valores_cartas
        self.multiplicidade = multiplicidade
        self.limiar = limiar
        self.custo_espiada = custo_espiada

    def startState(self):
        """
         Return the start state.
         Each state is a tuple with 3 elements:
           -- The first element of the tuple is the sum of the cards in the player's hand.
           -- If the player's last action was to peek, the second element is the index
              (not the face value) of the next card that will be drawn; otherwise, the
              second element is None.
           -- The third element is a tuple giving counts for each of the cards remaining
              in the deck, or None if the deck is empty or the game is over (e.g. when
              the user quits or goes bust).
        """
        return (0, None, (self.multiplicidade,) * len(self.valores_cartas))

    def actions(self, state):
        """
        Return set of actions possible from |state|.
        You do not must to modify this function.
        """
        return ['Pegar', 'Espiar', 'Sair']

    def succAndProbReward(self, state, action):
        """
        Given a |state| and |action|, return a list of (newState, prob, reward) tuples
        corresponding to the states reachable from |state| when taking |action|.
        A few reminders:
         * Indicate a terminal state (after quitting, busting, or running out of cards)
           by setting the deck to None.
         * If |state| is an end state, you should return an empty list [].
         * When the probability is 0 for a transition to a particular new state,
           don't include that state in the list returned by succAndProbReward.
        """
        # BEGIN_YOUR_CODE
        # print("succAndProbReward method")
        total, spied_card_index, deck = state
        if deck is None:
            return []
        succ_prob_reward = []
        new_deck = list(deck)
        if action == 'Espiar':
            if spied_card_index is not None:
                return [] 
            sum_cards_deck = sum(deck)
            for index in range(0, len(self.valores_cartas)):
                if deck[index] > 0:
                    new_state = (total, index, deck)
                    prob = float(deck[index]) / sum_cards_deck
                    reward = -self.custo_espiada
                    succ_prob_reward.append((new_state, prob, reward))

        if action == 'Pegar':
            if spied_card_index is not None:
                new_total = total + self.valores_cartas[spied_card_index]
                if new_total > self.limiar:
                    new_state = (new_total, None, None)
                    return [((new_state), 1.0, 0)]
                new_deck[spied_card_index] -= 1
                if sum(new_deck) == 0:
                    new_state = (new_total, None, None)
                    reward = new_total
                else: 
                    new_state = (new_total, None, tuple(new_deck))
                    reward = 0
                return [(new_state, 1.0, reward)]
                
        
            for index in range(0, len(self.valores_cartas)):
                if deck[index] > 0:
                    new_total = total + self.valores_cartas[index]
                    reward = 0
                    if new_total > self.limiar:
                        new_state = (new_total, None, None)
                        reward = 0
                        prob = float(deck[index]) / sum(deck)
                        succ_prob_reward.append((new_state, prob, reward))
                    else: #new_total <= self.limiar:
                        new_deck[index] -= 1
                        if sum(new_deck) == 0:
                            new_state = (new_total, None, None)
                            prob = float(deck[index]) / sum(deck)
                            reward = new_total
                            succ_prob_reward.append((new_state, prob, reward))
                        
                        else: #sum(new_deck) > 0:
                            new_state = (new_total, None, tuple(new_deck))
                            prob = float(deck[index]) / sum(deck)
                            reward = 0
                            succ_prob_reward.append((new_state, 
                            prob, reward))
            # return succ_prob_reward

        if action == 'Sair':
            new_state = (total, None, None)
            prob = 1.0
            reward = total
            
            return [(new_state, prob, reward)]
            
        return succ_prob_reward
            
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

    def discount(self):
        """
        Return the descount  that is 1
        """
        return 1

# **********************************************************
# **                    PART 02 Value Iteration           **
# **********************************************************

class ValueIteration(util.MDPAlgorithm):
    """ Asynchronous Value iteration algorithm """
    def __init__(self):
        self.pi = {}
        self.V = {}

    def solve(self, mdp, epsilon=0.001):
        """
        Solve the MDP using value iteration.  Your solve() method must set
        - self.V to the dictionary mapping states to optimal values
        - self.pi to the dictionary mapping states to an optimal action
        Note: epsilon is the error tolerance: you should stop value iteration when
        all of the values change by less than epsilon.
        The ValueIteration class is a subclass of util.MDPAlgorithm (see util.py).
        """
        mdp.computeStates()
        def computeQ(mdp, V, state, action):
            # Return Q(state, action) based on V(state).
            return sum(prob * (reward + mdp.discount() * V[newState]) \
                            for newState, prob, reward in mdp.succAndProbReward(state, action))

        def computeOptimalPolicy(mdp, V):
            # Return the optimal policy given the values V.
            pi = {}
            for state in mdp.states:
                pi[state] = max((computeQ(mdp, V, state, action), action) for action in mdp.actions(state))[1]
            return pi
            
        V = defaultdict(float)  # state -> value of state
        # Implement the main loop of Asynchronous Value Iteration Here:
        # BEGIN_YOUR_CODE
        for s in mdp.states:
            V[s] = 0.0
        
        delta = 1000000
        
        while delta > epsilon:
            delta = 0
            for s in mdp.states:
                v = V[s]
                V[s] = max([computeQ(mdp, V, s, a) for a in mdp.actions(s)])
                delta = max(delta, abs(v-V[s]))             
        
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

        # Extract the optimal policy now
        pi = computeOptimalPolicy(mdp, V)

        # print("ValueIteration: %d iterations" % numIters)
        self.pi = pi
        self.V = V

print("Politica ótimo para o MDP1 com Value Iteration: ")
MDP1 = BlackjackMDP(valores_cartas=[1, 5], multiplicidade=2, limiar=10, custo_espiada=1)
viMDP1 = ValueIteration()
viMDP1.solve(MDP1)
for s, a in viMDP1.pi.items():
    print(s, a)

print()

print("Politica ótimo para o MDP2 com Value Iteration: ")
MDP2 = BlackjackMDP(valores_cartas=[1, 5], multiplicidade=2, limiar=15, custo_espiada=1)
viMDP2 = ValueIteration()
viMDP2.solve(MDP2)
for s, a in viMDP2.pi.items():
    print(s, a)

def geraMDPxereta():
    """
    Return an instance of BlackjackMDP where peeking is the
    optimal action for at least 10% of the states.
    """
    # BEGIN_YOUR_CODE
    return BlackjackMDP(valores_cartas=[1, 2, 3, 18], multiplicidade=3, limiar=20, custo_espiada=1)
    # END_YOUR_CODE


# **********************************************************
# **                    PART 03 Q-Learning                **
# **********************************************************

class QLearningAlgorithm(util.RLAlgorithm):
    """
    Performs Q-learning.  Read util.RLAlgorithm for more information.
    actions: a function that takes a state and returns a list of actions.
    discount: a number between 0 and 1, which determines the discount factor
    featureExtractor: a function that takes a state and action and returns a
    list of (feature name, feature value) pairs.
    explorationProb: the epsilon value indicating how frequently the policy
    returns a random action
    """
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    def getQ(self, state, action):
        """
         Return the Q function associated with the weights and features
        """
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    def getAction(self, state):
        """
        Produce an action given a state, using the epsilon-greedy algorithm: with probability
        |explorationProb|, take a random action.
        """
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        return max((self.getQ(state, action), action) for action in self.actions(state))[1]

    def getStepSize(self):
        """
        Return the step size to update the weights.
        """
        return 1.0 / math.sqrt(self.numIters)

    def incorporateFeedback(self, state, action, reward, newState):
        """
         We will call this function with (s, a, r, s'), which you should use to update |weights|.
         You should update the weights using self.getStepSize(); use
         self.getQ() to compute the current estimate of the parameters.

         HINT: Remember to check if s is a terminal state and s' None.
        """
        # BEGIN_YOUR_CODE
        # approximate Q-Learning
        if newState is None:
            return
        maxQ = max([self.getQ(newState, newAction) for newAction in self.actions(newState)])
        adjust = self.getStepSize() * (reward + self.discount * maxQ - self.getQ(state, action))
        for f, v in self.featureExtractor(state, action):
            self.weights[f] += adjust * v        
        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

def identityFeatureExtractor(state, action):
    """
    Return a single-element list containing a binary (indicator) feature
    for the existence of the (state, action) pair.  Provides no generalization.
    """
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

# Large test case
largeMDP = BlackjackMDP(valores_cartas=[1, 3, 5, 8, 10], multiplicidade=3, limiar=40, custo_espiada=1)

# Comparar Q-learning com Value Iteration
def simulate_compare_QL_VI(mdp, featureExtractor):

    valIter = ValueIteration()
    valIter.solve(mdp)
    pi_valIter = valIter.pi

    RL = QLearningAlgorithm(mdp.actions, mdp.discount(), featureExtractor)
    # 30 mil eposidios
    simulate(mdp, RL, numTrials=30000)
    RL.explorationProb = 0
    pi_RL = {}
    count_coincidences = 0
    for state in mdp.states:
        pi_RL[state] = RL.getAction(state)
        if pi_RL[state]  == pi_valIter[state]:
            count_coincidences += 1
    ratio = 100 * count_coincidences/len(mdp.states)
    print("Porcentagem de estados para as quais as ações coindicem: ", ratio)

# Comparação com o MDP1
simulate_compare_QL_VI(MDP1, identityFeatureExtractor)
# RESULTADO
# Porcentagem de estados para as quais as ações coindicem:  
# 73.53

# Comparação com o MDP2
simulate_compare_QL_VI(MDP2, identityFeatureExtractor)
# RESULTADO
# Porcentagem de estados para as quais as ações coindicem:  
# 44.44

# **********************************************************
# **        PART 03-01 Features for Q-Learning             **
# **********************************************************

def blackjackFeatureExtractor(state, action):
    """
    You should return a list of (feature key, feature value) pairs.
    (See identityFeatureExtractor() above for a simple example.)
    """
    # BEGIN_YOUR_CODE
    total, spied_card_index, deck = state

    # total atual de cartas no jogador
    results = [((action, total), 1)]
    if deck is not None:
        # presença / ausencia de cada valor da carta no baralho
        cardPresentIndicator = tuple([1 if x > 0 else 0 for x in deck])
        # adicionado a nossas features
        results.append(((action, cardPresentIndicator), 1))
        
        # quantidade de cartas restantes no baralho para cada valor
        for card_idx, count in enumerate(deck):
            results.append(((action, card_idx, count), 1))
    
    # indicadores da ação e as respeitivas features do estado
    return results
    # END_YOUR_CODE

# Comparação do largeMDP utilizando o blackjackFeatureExtractor
simulate_compare_QL_VI(largeMDP, blackjackFeatureExtractor)
# RESULTADO
# Porcentagem de estados para as quais as ações coindicem:  
# 67.71