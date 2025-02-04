import datetime
import sqlite3


def add_death(all_money: int, all_damage: int) -> None:
    con = sqlite3.connect('deaths.sql')
    cur = con.cursor()

    cur.execute(
        '''INSERT INTO death(time, all_money, all_damage) VALUES (?, ?, ?)''',
        (datetime.datetime.now(),
         all_money,
         all_damage))

    con.commit()
