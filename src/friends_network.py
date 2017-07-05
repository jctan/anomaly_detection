'''
The Friends Network stores relationships users and their Dth degree friends network

self.friends - { id1: set(id2, id3, ...)}
self.friendsNetwork - { id1: { id2: level, ...}, ...}

'''


class FriendsNetwork:

    def __init__(self, D):
        # stores friends network (key = user and values = their sets of their friends)
        self.friends = {}

        # stores Dth degree within friends network, including level of degree is stored
        self.friendsNetwork = {}

        # initialize D degree in nework
        self.D = int(D)

    # add relationship between 2 users
    def add_friend(self, befriend, update_status=False):
        id1 = befriend.get('id1')
        id2 = befriend.get('id2')

        # make sure id1 and id2 exists
        if id1 and id2:
            if id1 in self.friends:
                # add id2 to id1 as set() of friends
                self.friends[id1].add(id2)
            else:
                # if the user is not in the friends network, create id2 and add to id1 network
                self.friends[id1] = set([id2])

            # add relationship for id2 as well
            if id2 in self.friends:
                self.friends[id2].add(id1)
            else:
                self.friends[id2] = set([id1])

            # stream data update in real time
            # batch data doesn't update until all batch data is added
            if update_status:
                # get id1 and id2 users for D-1 relationship. Dth degree in network will not be affected
                users = self.get_user(id1, self.D - 1)
                users.update(self.get_user(id2, self.D - 1))
                users.update([id1, id2])
                self.update_friendsNetwork(users)
        else:
            print('Befriend Event is Incomplete')

    # delete relationships between 2 users
    def delete_friend(self, unfriend, update_status=False):

        # track if friends is deleted
        friend_deleted = False

        id1 = unfriend.get('id1')
        id2 = unfriend.get('id2')

        # make sure id1 and id2 exists
        if id1 and id2:
            # make sure id1 is in the network before deleting
            if id1 in self.friends:
                # make sure id1 and id2 is in relationship before deleting
                if self.friends_check(id1, id2):
                    self.friends[id1].remove(id2)
                    friend_deleted = True

            # check relationship for id2 too
            if id2 in self.friends:
                if self.friends_check(id2, id1):
                    self.friends[id2].remove(id1)
                    friend_deleted = True

            # update the Dth degree friends network if friends are deleted
            if friend_deleted and update_status:
                 # get id1 and id2 users for D-1 relationship. Dth degree in network will not be affected
                users = self.get_user(id1, self.D - 1)
                users.update(self.get_user(id2, self.D - 1))
                users.update([id1, id2])
                self.update_friendsNetwork(users)
        else:
            print('Unfriend Event is Incomplete')

    # check if id1 and id2 are friends and is in the friends network
    def friends_check(self, id1, id2):
        if id1 and id2 in self.friends:
            if id2 in self.friends[id1]:
                return True
        return False

    # update Dth degree network for each specific user
    def update_friendsNetwork(self, specific_users=set([])):
        # D must be at least 1
        if self.D < 1:
            return False

        # if there are specific users, only update their friends network
        if len(specific_users):
            for userId in specific_users:
                self.compute_nbr(userId, self.D)
        else:
            # update the entire friends network
            for userId in self.friends:
                self.compute_nbr(userId, self.D)
        return True

    # compute neighbors within the cutoff distance for a given starting node
    # neighbors are stored in self.friendsNetwork
    # self.friendsNetwork[id1] = {id2: level, ...}
    def compute_nbr(self, startV, cutoff):

        # level of search starts at D=1
        level = 1

        # create node to check next level
        nextLevel = self.friends[startV]

        # make sure the starting node/vertex is in friends network
        if startV not in self.friendsNetwork:
            self.friendsNetwork[startV] = {}

        # continue going to the next level of vertices
        while nextLevel:
            thisLevel = nextLevel
            nextLevel = set([])

            for node in thisLevel:
                if (node != startV) and (node not in self.friendsNetwork[startV]):
                    self.friendsNetwork[startV][node] = level

                    # keep on adding the node of friends to traverse to next level in the network
                    nextLevel.update(self.friends[node])

                    # traverse the network on opposite direction of the relationship
                    if node not in self.friendsNetwork:
                        self.friendsNetwork[node] = {startV: level}
                    else:
                        self.friendsNetwork[node][startV] = level

            # break out if level D is greater than cutoff distance
            if cutoff <= level:
                break
            level += 1

    # returns list of users in the user's Dth degree friends network.
    # If there's a cutoff, then return only within the cutoff's degree
    def get_user(self, userId, cutoff=None):
        if userId in self.friendsNetwork:
            if cutoff:
                # only return users if cutoff >= degree of [userId][id2]
                return set(id2 for id2 in self.friendsNetwork[userId] if self.friendsNetwork[userId][id2] <= cutoff)
            # else, return all users in the friends network
            return set(self.friendsNetwork[userId].keys())
        return set([])

    # return the number of users in the friends network
    def get_number_users(self):
        return len(self.friends)
