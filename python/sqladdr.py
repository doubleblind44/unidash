import parse_addr
import sqlalchemy

def create_table(db: sqlalchemy.engine.Engine):
    """
    Creates a table mapping the addresses in UnivIS to the new addresses parsed with the modul "parse_addr"
    :param db: sql connection
    """
    con = db.connect()
    sql = "CREATE TABLE IF NOT EXISTS new_addresses (old_address TEXT, new_address TEXT)"
    table = con.execute(sql)


def create_address(db: sqlalchemy.engine.Engine):
    """
    Creates an entry for each address in UnivIS mapping the old address to the new one
    :param db: sql connection
    """
    con = db.connect()
    # get the addresses
    old_addresses = "SELECT address FROM Room GROUP BY address"
    old_addresses = list(con.execute(old_addresses))

    entry = "INSERT OR REPLACE INTO new_addresses VALUES (:old, :new)"
    # go through the addresses
    for old_addr in old_addresses:
        # parse the addresses
        new_addr = parse_addr.new_addr(old_addr[0])
        # add the new entry
        con.execute(entry, old=old_addr[0], new=new_addr)


def drop_addr(db: sqlalchemy.engine.Engine):
    """
    Deletes the table for the new addresses
    :param db: sql connection
    """
    con = db.connect()
    sql = "DROP TABLE new_addresses"
    con.execute(sql)
