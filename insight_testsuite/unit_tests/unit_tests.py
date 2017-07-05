import sys
import unittest
from anomaly_detection import AnomalyDetection
from purchase_history import PurchaseHistory
from friends_network import FriendsNetwork

''' Runs series of unit tests for the friends network, purchase history, and anomaly detection '''


class TestCases(unittest.TestCase):

    def setUp(self):

        # load a new session by building a social network
        # and purchase history from a batch log file
        batch_file = 'unit_test_data/batch_log.json'
        self.session = AnomalyDetection(batch_file, '', '')
        self.session.batch_data()

    def test_batch_data_loaded(self):
        ''' Assert that the batch data loaded properly '''
        self.assertEqual(self.session.friendsNetwork.D, 3)
        self.assertEqual(self.session.purchasesList.T, 5)
        self.assertEqual(self.session.friendsNetwork.get_number_users(), 5)
        self.assertEqual(self.session.purchasesList.get_number_purchases(), 7)

    def test_Dth_degree_network_generated(self):
        """ Assert that the 3nd degree network was generated properly"""
        # test that uid '1' exists
        self.assertIn('1', self.session.friendsNetwork.friends)
        self.assertIn('1', self.session.friendsNetwork.friends)

        # uid 2 is friends with uid 1
        self.assertIn('2', self.session.friendsNetwork.friends['1'])

        # uids 2,3,4 should be in 1's 3rd degree network; check each level as well
        self.assertIn('2', self.session.friendsNetwork.friendsNetwork['1'])
        self.assertEqual(1, self.session.friendsNetwork.friendsNetwork['1']['2'])
        self.assertIn('3', self.session.friendsNetwork.friendsNetwork['1'])
        self.assertEqual(2, self.session.friendsNetwork.friendsNetwork['1']['3'])
        self.assertIn('4', self.session.friendsNetwork.friendsNetwork['1'])
        self.assertEqual(3, self.session.friendsNetwork.friendsNetwork['1']['4'])

        # uid 5 should not be in uid 1's 3rd degre network
        self.assertNotIn('5', self.session.friendsNetwork.friendsNetwork['1'])

    def test_add_friend(self):
        ''' Assert that a friend is properly added to the network '''
        event = {'id1': '5', 'id2': '6'}
        self.friendsNetwork.add_friend(event, update_status=True)

        # id 5 and 6 should be friends
        self.assertIn('6', self.session.friendsNetwork.friends['5'])

        # id 3 should be in id 6's 3rd degree network
        self.assertIn('3', self.session.friendsNetwork.friendsNetwork['6'])

    def test_remove_friend(self):
        ''' Assert that a friendship is properly removed from the network '''
        event = {'id1': '5', 'id2': '6'}
        self.friendsNetwork.delete_friend(event, update_status=True)

        # id 5 and 6 should not be friends
        self.assertNotIn('6', self.session.friendsNetwork.friends['5'])

        # id 3 should not be in id 6's 3rd degree network
        self.assertNotIn('3', self.session.friendsNetwork.friendsNetwork['6'])

    def test_add_purchase(self):
        ''' Assert that a purchase was properly added to the network '''
        event = {'timestamp': '2017-06-13 11:33:12', 'id': '1', 'amount': '13.24'}
        self.purchasesList.add_purchase(event)

        # there should be 8 purchases now
        self.assertEqual(8, self.session.purchasesList.get_number_purchases())

        # 0 based indexing, so purchase #7 is the 8th purchase
        self.assertTupleEqual(('1', '2017-06-13 11:33:12', 13.24), self.session.purchasesList.purchasesList[7])

    def test_transaction_history_ordered_by_timestamp(self):
        ''' Assert that the purchases are ordered by the timestamp '''
        purchasesList = self.session.purchasesList.purchasesList
        for i in range(self.session.purchasesList.get_number_purchases() - 1):
            # test that the next timestamp is >= the current
            timestamp1 = purchasesList[i][1]
            timestamp2 = purchasesList[i + 1][1]
            self.assertGreaterEqual(timestamp2, timestamp1)

    def test_D_lte_1_returns_no_network(self):
        ''' Assert that D=0 does not generate a network '''
        self.session.friendsNetwork.set_network_degree(0)

        # changing the network degree should not affect the friendships
        self.assertEqual(1, len(self.session.friendsNetwork.friends['1']))

        # getting the Dth degree user list should return an empty set
        self.assertEqual(0, len(self.session.friendsNetwork.get_user_list('1')))

        # set the network degree back to 3
        self.session.friendsNetwork.set_network_degree(3)

    def test_T_lte_2_returns_no_stats(self):
        ''' Assert that T<=2 does not give any purchase stats '''
        self.session.purchasesList.set_purchase_cutoff(1)

        # even though uid has 3 purchases, it should return (0,0,0)
        self.assertTupleEqual((0, 0, 0), self.session.purchasesList.get_purchase_stats(set(['3'])))

        # set the cutoff back to 5
        self.session.purchasesList.set_purchase_cutoff(5)

    def test_Npurchases_gte_2_and_lte_T(self):
        ''' Assert that 2 <= N consecutive purchases considered <= T '''
        # set the network degree D=1; uid '1' will only have 1 purchase
        # in the network, so the purchase stats should return (0,0,0)
        self.session.friendsNetwork.set_network_degree(1)
        users = self.session.friendsNetwork.get_user_list('1')
        self.assertTupleEqual((0, 0, 0), self.session.purchasesList.get_purchase_stats[users])

        # set the network degree to D=2, uid '1' will have 4 purchases
        # in the network, so the purchase stats should return the stats for all 4
        self.session.friendsNetwork.set_network_degree(2)
        users = self.session.friendsNetwork.get_user_list('1')
        mean, sd, numPurchases = self.session.purchasesList.get_purchase_stats(users)
        self.assertAlmostEqual(mean, 32.14750)
        self.assertAlmostEqual(sd, 18.72964678)
        self.assertEqual(numPurchases, 4)

        # set the network degree to D=3, uid '1' will have 6 purchases
        # in the network, so the purchase stats should only return the last 5
        # self.session.friendsNetwork.set_friendsNetwork_degree(3)
        users = self.session.friendsNetwork.get_user('1')
        mean, sd, numPurchases = self.session.purchasesList.get_purchase_stats(users)
        self.assertAlmostEqual(mean, 25.542000)
        self.assertAlmostEqual(sd, 13.53690127)
        self.assertEqual(numPurchases, 5)

    def test_self_purchases_not_included(self):
        ''' Assert that a given user's purchases are not considered
            when analyzing their network's purchases '''
        # the purchases are based on the user list generated from each user
        # it's sufficient to check that a user is not in their own
        # network list that will be analyzed
        self.assertNotIn('1', self.session.friendsNetwork.get_user('1'))

    def test_anomaly_detection(self):
        ''' Assert that an anomlous purchase is detected '''

        purchase = {'timestamp': '2017-06-13 11:33:13', 'id': '2', 'amount': 2000}
        is_anomalous = self.session.anomaly_check(purchase)
        self.assertTrue(is_anomalous)

if __name__ == '__main__':
    unittest.main()
