# Anomaly Detection in Social Network of Users

Find problem set here - https://github.com/InsightDataScience/anomaly_detection

## Summary

Implement of a friends(social) network where users can add/delete friends and as well as making purchases on an e-commerce platform. It takes two logs of the entire network events - 1. batch_log for building the state of the network and 2. stream_log to simulate and determine whether a purchase is anamalous. If caluclation in real-time that purchases are anomalous, it should be flagged and logged into the flagged_purchase.json file. As events from both files process through, the friends (socail) network and the purchase history of users should be updated.

A purchase is anomalous when the purchase amount is more than 3 standard deviation from the mean of the last `T` purchases in user's `D`th degree network. `D` should not be hardcoded and be flexible, and will be at least `1` and `T` shouldn't be hardcoded as well, and will be at least `2`.

`D`: The number of degrees that defines a user's friends(social) network
`T`: The number of consecutive purchases made by user's friends network (not including the user's own purchases)

### Detect Anamolous

Keep track of all events from users. When new events process in, update information correlated to the users. If user doesn't exist, create new user.

### Level

- Keep track of user's friends (D=1)
- Keep track of user's last T purchases and last T purchases of uer's Dth degree network
- calculate `mean` and `std` of purchases made in user's friends network

## Run Code:

Clone the repo and run `./run.sh` in the anomaly_detection directory. The code will process `batch_log.json` and `stream_log.json` in the input_log directory and it will write the output to the `flagged_purchases.json` file into the output_log directory as anomalous detected.

You can also run the command `python ./src/anomaly_detection.py ./log_input/batch_log.json ./log_input/stream_log.json ./log_output/flagged_purchases.json` inside the anomaly_detection directory.

## Environment & Dependencies
- Code run on python 2.7.10

uses the the following Python libraries & packages
- sys
- os
- json
- time
- numpy

