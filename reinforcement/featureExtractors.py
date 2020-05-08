# featureExtractors.py
# --------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"Feature extractors for Pacman game states"

from game import Directions, Actions
import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features



class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """
    def getFeatures(self, state, action):
        "*** YOUR CODE HERE ***"
        # check closest food
        food = state.getFood()
        walls = state.getWalls()
        features = util.Counter()
        # capsules = state.getCapsules()

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        # features["bias"] = 1.0
        features["number-of-active-ghosts-1-step-away"] = self.getNumberOfGhostsWithinOneStep((next_x, next_y), state, walls)[0]
        # features["number-of-capsule-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(c, walls) for c in capsules)

        # if there is no danger of ghosts then add the food feature
        if not features["number-of-active-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        invertedClosestGhost = self.getInvertedDistanceOfScaredGhost((next_x, next_y), state, walls)
        if invertedClosestGhost is not None:
            features["inverted-closest-scared-ghosts-distance"] = invertedClosestGhost
        # features["number-of-scared-ghosts-1-step-away"] = self.getNumberOfGhosts((next_x, next_y), state, walls)[1]
        # features["number-of-scared-ghosts-2-step-away"] = self.getNumOfScaredGhostTwoStep((next_x, next_y), state, walls)
        # features["getClosestScaredGhostDistance"] = self.getClosestScaredGhostDistance((next_x, next_y), state, walls)/10
        # capsuleDist = self.getClosestCapsuleDistance((next_x, next_y), state, walls)
        # if capsuleDist is not None:
        #     features["closest-capsule-distance"] = float(capsuleDist)

        features.divideAll(10.0)
        return features

    def getNumberOfGhostsWithinOneStep(self, pos, state, walls):
        numberOfActiveGhosts = 0
        numberOfScaredGhosts = 0
        for index in range(1, len(state.data.agentStates)):
            ghost_x, ghost_y = state.data.agentStates[index].getPosition()
            if (ghost_x, ghost_y) in Actions.getLegalNeighbors(pos, walls):
                if state.data.agentStates[index].scaredTimer <= 0:
                    numberOfActiveGhosts += 1
                else:
                    numberOfScaredGhosts += 1
        return numberOfActiveGhosts, numberOfScaredGhosts

    # def getNumberOfGhostsWithinTwoStep(self, pos, state, walls):
    #     numberOfActiveGhosts = 0
    #     numberOfScaredGhosts = 0
    #     expanded = set()
    #     for index in range(1, len(state.data.agentStates)):
    #         ghost_x, ghost_y = state.data.agentStates[index].getPosition()
    #         for location in Actions.getLegalNeighbors(pos, walls):
    #             if (ghost_x, ghost_y) in Actions.getLegalNeighbors(location, walls) and (ghost_x, ghost_y) not in expanded:
    #                 expanded.add((ghost_x, ghost_y))
    #                 if state.data.agentStates[index].scaredTimer <= 0:
    #                     numberOfActiveGhosts += 1
    #                 else:
    #                     numberOfScaredGhosts += 1
    #         return numberOfActiveGhosts, numberOfScaredGhosts

    # this distance function is inverted
    def getInvertedDistanceOfScaredGhost(self, pos, state, walls):
        fringe = [(pos[0], pos[1], 0)]
        ghostPositions = []
        for index in range(1, len(state.data.agentStates)):
            if state.data.agentStates[index].scaredTimer > 0:
                ghostPositions.append(state.data.agentStates[index].getPosition())
        if len(ghostPositions) < 1:
            return None

        expanded = set()
        while fringe:
            pos_x, pos_y, dist = fringe.pop(0)
            if (pos_x, pos_y) in expanded:
                continue
            expanded.add((pos_x, pos_y))
            if (pos_x, pos_y) in ghostPositions:
                return 10/(dist * dist + 1)
            # otherwise spread out from the location to its neighbours
            nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
            for nbr_x, nbr_y in nbrs:
                fringe.append((nbr_x, nbr_y, dist + 1))
        return None

    # def getNumOfScaredGhostTwoStep(self, pos, state, walls):
    #     fringe = [(pos[0], pos[1], 0)]
    #     ghostPositions = []
    #     for index in range(1, len(state.data.agentStates)):
    #         if state.data.agentStates[index].scaredTimer > 0:
    #             ghostPositions.append(state.data.agentStates[index].getPosition())
    #     if len(ghostPositions) < 1:
    #         return 0
    #
    #     expanded = set()
    #     ghost = 0
    #     while fringe:
    #         pos_x, pos_y, dist = fringe.pop(0)
    #         if dist > 2:
    #             return ghost
    #         if (pos_x, pos_y) in expanded:
    #             continue
    #         expanded.add((pos_x, pos_y))
    #         if (pos_x, pos_y) in ghostPositions:
    #             ghost += 1
    #         nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
    #         for nbr_x, nbr_y in nbrs:
    #             fringe.append((nbr_x, nbr_y, dist + 1))
    #     return ghost


    # def getClosestCapsuleDistance(self, pos, state, walls):
    #     fringe = [(pos[0], pos[1], 0)]
    #     capsulesPostions = state.getCapsules()
    #     if len(capsulesPostions) < 1:
    #         return None
    #
    #     expanded = set()
    #     while fringe:
    #         pos_x, pos_y, dist = fringe.pop(0)
    #         if (pos_x, pos_y) in expanded:
    #             continue
    #         expanded.add((pos_x, pos_y))
    #         if (pos_x, pos_y) in capsulesPostions:
    #             return dist
    #         # otherwise spread out from the location to its neighbours
    #         nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
    #         for nbr_x, nbr_y in nbrs:
    #             fringe.append((nbr_x, nbr_y, dist + 1))


    # this distance function is not inverted
    # def getClosestScaredGhostDistance(self, pos, state, walls):
    #     fringe = [(pos[0], pos[1], 0)]
    #     ghostPositions = []
    #     for index in range(1, len(state.data.agentStates)):
    #         if state.data.agentStates[index].scaredTimer > 0:
    #             ghostPositions.append(state.data.agentStates[index].getPosition())
    #     if len(ghostPositions) < 1:
    #         return walls.width + walls.height
    #
    #     expanded = set()
    #     while fringe:
    #         pos_x, pos_y, dist = fringe.pop(0)
    #         if (pos_x, pos_y) in expanded:
    #             continue
    #         expanded.add((pos_x, pos_y))
    #         if (pos_x, pos_y) in ghostPositions:
    #             return dist
    #         # otherwise spread out from the location to its neighbours
    #         nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
    #         for nbr_x, nbr_y in nbrs:
    #             fringe.append((nbr_x, nbr_y, dist + 1))
    #     return walls.width + walls.height

    # def getClosestCapsuleDistance(self, pos, state, walls):
    #     fringe = [(pos[0], pos[1], 0)]
    #     capsulesPostions = state.getCapsules()
    #     if len(capsulesPostions) < 1:
    #         return None
    #
    #     expanded = set()
    #     while fringe:
    #         pos_x, pos_y, dist = fringe.pop(0)
    #         if (pos_x, pos_y) in expanded:
    #             continue
    #         expanded.add((pos_x, pos_y))
    #         if (pos_x, pos_y) in capsulesPostions:
    #             return dist
    #         # otherwise spread out from the location to its neighbours
    #         nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
    #         for nbr_x, nbr_y in nbrs:
    #             fringe.append((nbr_x, nbr_y, dist + 1))


        
