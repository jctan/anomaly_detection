import numpy as np

'''
purchase history stores the purchases of each specific users in self.purchasesList
# { numPurchase: (id, timestamp, amount), ...}

'''


class PurchaseHistory:

    def __init__(self, T):
        # returns the last T purchases for specific users
        self.purchasesList = {}

        # intialize number of continuous purchases
        self.T = int(T)

        # track the number of purchases
        self.numPurchase = 0

    # add purchase to user's history to purchasesList
    # first timestamp call is the earliest one
    def add_purchase(self, purchase):
        timestamp = purchase.get('timestamp')
        userId = purchase.get('id')
        amount = purchase.get('amount')

        # make sure timestamp, userId, and amount exists
        if timestamp and userId and amount:
            self.purchasesList[self.numPurchase] = (userId, timestamp, float(amount))

            # increment the number of purchases
            self.numPurchase += 1

        else:
            print('Purchase Event is Incomplete')

    # return the mean and standard deviation of a list of purchases for each individual users
    def get_purchase_stats(self, users):
        # the friends network must have at least 2 purchass
        if self.T < 2:
            return (0, 0, 0)

        purchasesList = []
        num = 0

        # Purchases comes in from the batch/stream log in the order as they are called by timestamp
        # Get the last T purchases for each specific group of users (start with recent purchases)
        # num = number of purcahses
        # T = cutoff of T purchases
        for i in range(self.numPurchase):
            # only need T purchases
            # if number of purchases is greater than the last T purchases, exit
            if num > self.T - 1:
                break

            # when numPurchases are larger, they are newer purchases
            # desc order: (numPurchase - 1) - i
            userId, timestamp, amount = self.purchasesList[self.numPurchase - 1 - i]

            # we only want purchases from given each individual users
            if userId in users:
                purchasesList.append(amount)
                num += 1

        # calcualte mean and standard deviation
        mean = np.mean(np.array(purchasesList))
        sd = np.std(np.array(purchasesList))

        return (mean, sd, len(purchasesList))

    # return number of purchases
    def get_number_purchases(self):
        return self.numPurchase
