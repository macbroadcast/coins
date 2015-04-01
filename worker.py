import db
import coinprism
import time
import transactions

def worker_cycle():
    print "BEGINNING WORK CYCLE"
    send_plain_btc()
    issue_colors()
    transfer_colors()
    scrape_asset_addresses()

def send_plain_btc():
    txs = db.unsent_btc_transfers()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fee = tx[3] #satoshi
        amount = tx[4] #satoshi
        randomid = tx[7]

        btc_value = amount*0.00000001
        try:
            txhash = transactions.send_btc(sender_public, sender_private, receiver_public, btc_value)
            print "TXHASH"
            print txhash
        except:
            print "ERROR MAKING TX"
            txhash = 'fail'

        if len(txhash)>10:
            dbstring = "update btc_tx_queue set txhash='"+str(txhash)+"', success=True where randomid='"+str(randomid)+"';"
            db.dbexecute(dbstring, False)

def issue_colors():
    txs = db.unsent_issue_txs()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fees = tx[3]
        asset_address = tx[4]
        color_amount = tx[5]
        metadata = tx[8]
        randomid = tx[9]
        name = tx[10]

        r = coinprism.issue_asset(sender_public, receiver_public, color_amount, metadata, fees, sender_private)
        if len(r) > 10:
            txhash = r
            dbstring = "update color_issue_tx_queue set txhash='"+str(r)+"', success=True where randomid = '"+str(randomid)+"';"
            db.dbexecute(dbstring, False)

            db.add_asset(name, sender_public, '', metadata)


def transfer_colors():
    txs = db.unsent_transfer_txs()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fee = tx[3]
        asset_address = tx[4]
        color_amount = tx[5]
        metadata = tx[8]
        randomid = tx[9]

        txhash = coinprism.transfer_asset(sender_public, receiver_public, color_amount, metadata, fee, sender_private, asset_address)
        try:
            if len(txhash) > 10:
                dbstring = "update color_transfer_tx_queue set txhash='"+str(txhash)+"', success=True where randomid='"+str(randomid)+"';"
                db.dbexecute(dbstring, False)
        except:
            print "No tx"

def scrape_asset_addresses():
    addrs = db.assets_without_address()
    for addr in addrs:
        address = addr[1]
        name = addr[0]
        asset_address = coinprism.get_asset_id(address)
        if asset_address == -1:
            k=0
        else:
            db.update_asset_address_on_asset(name, address, asset_address)
