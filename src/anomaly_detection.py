import sys
import os
import json
import time
from purchase_history import PurchaseHistory
from friends_network import FriendsNetwork

'''
loads and process both batch data and batch data to determine if user's anaomlous in the Dth degree network

'''


class AnomalyDetection:

    def __init__(self, batchFile, streamFile, flaggedFile):
        # set files and attributes of friendsNetwork and purchase history
        self.batchFile = batchFile
        self.streamFile = streamFile
        self.flaggedFile = flaggedFile
        self.friendsNetwork = {}
        self.purchasesList = {}

    # load and process both batch data and stream data
    def process_log(self):
        print('Loading Data from Batch Log...')
        t0 = time.time()
        self.batch_data()
        print ('Batch Data Loaded (%s users and %d purchases) in %.4f seconds.' % (self.friendsNetwork.get_number_users(),
                                                                                   self.purchasesList.get_number_purchases(),
                                                                                   time.time() - t0))

        # load and process stream data
        print('\nLoading data from stream log...')
        print('\nFlagged Purchases: \n')
        self.stream_data()

    # load and process batch data
    def batch_data(self):
        file = open(self.batchFile)

        # read first line of T and D as params
        params = json.loads(file.readline().strip())
        self.final_objects(params)

        # process events from batch log
        file = self.process_events(file, 'batch')
        file.close()

        # when users are loaded, generate Dth degree network
        self.friendsNetwork.update_friendsNetwork()

    # load and process stream data
    def stream_data(self):
        file = open(self.streamFile)
        file = self.process_events(file, 'stream')
        file.close()

    # process events
    # batch data - update_status is False
    # stream data - update_status is True
    def process_events(self, file, data_type):
        # list to compare event types
        event_type = ['purchase', 'befriend', 'unfriend']

        # process each event
        while True:
            line = file.readline().strip()
            if line:
                event = json.loads(line)

                # if event type is Purchase
                if event['event_type'] == event_type[0]:
                    if data_type == 'stream':
                        self.anomaly_check(event)
                    # add both batch and steam data to purchasesList as user's history
                    self.purchasesList.add_purchase(event)

                # if event type is befriend
                elif event['event_type'] == event_type[1]:
                    if data_type == 'stream':
                        # update stream data immediately
                        self.friendsNetwork.add_friend(event, update_status=True)
                    else:
                        # add friends but doesnt update immediately
                        self.friendsNetwork.add_friend(event)

                # if event type is unfriend
                elif event['event_type'] == event_type[2]:
                    if data_type == 'stream':
                        self.friendsNetwork.delete_friend(event, update_status=True)
                    else:
                        # batch data
                        self.friendsNetwork.delete_friend(event)
            else:
                break
        return file

    # make sure D and T object is set properly for friends network and purchase history
    def final_objects(self, params):
        if 'D' and 'T' in params:
            D = params['D']
            T = params['T']
        else:
            print('D and T were input incorrectly ')
            D = input('Input Degree (D): ')
            T = input('Input Tracked Purchases (T): ')

        self.friendsNetwork = FriendsNetwork(D)
        self.purchasesList = PurchaseHistory(T)

    # check whether a purchase is anomalous
    def anomaly_check(self, purchase):
        userId = purchase.get('id')
        amount = purchase.get('amount')

        if userId and amount:
            # get the T purchases of user's network
            users = self.friendsNetwork.get_user(userId)
            mean, sd, numPurchases = self.purchasesList.get_purchase_stats(users)

            if mean and sd:
                amount = float(amount)
                # if purchase amount if greater than sd, it's anomalous
                if amount > mean + (3 * sd):

                    # write anomaly to the flagged purchases
                    file = open(self.flaggedFile, 'a')
                    file.write('{"event_type": "%s", "timestamp": "%s", "id": "%s", "amount": "%.2f", "mean": "%.2f", "sd": "%.2f"}\n' % (purchase['event_type'], purchase['timestamp'], purchase['id'], amount, mean, sd))
                    print('{"event_type": "%s", "timestamp": "%s", "id": "%s", "amount": "%.2f", "mean": "%.2f", "sd": "%.2f"}' % (purchase['event_type'], purchase['timestamp'], purchase['id'], amount, mean, sd))

                    print('The friends network of %d user(s) and %d purchase(s) is anomalous: $%.2f\n' % (len(users), numPurchases, amount))

                    file.close()
                    return True

        else:
            print('Purchase Event is Incomplete')
        return False


def main():
    batchFile = sys.argv[1]
    streamFile = sys.argv[2]
    flaggedFile = sys.argv[3]
    t0 = time.time()

    AnomalyDetection(batchFile, streamFile, flaggedFile).process_log()
    print ('\nProcessed both batch log and stream log in %.4f seconds.' % (time.time() - t0))


if __name__ == '__main__':
    main()
