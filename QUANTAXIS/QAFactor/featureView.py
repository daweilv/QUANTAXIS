import clickhouse_driver
import datetime
import pandas as pd
import QUANTAXIS as QA

from qaenv import clickhouse_ip, clickhouse_password, clickhouse_port, clickhouse_user


class QAFeatureView():
    def __init__(self, host=clickhouse_ip, port=clickhouse_port, user=clickhouse_user, password=clickhouse_password) -> None:
        self.client = clickhouse_driver.Client(host=host, port=port, user=user, password=password,
                                               database='factor')

    def get_all_factorname(self):
        data = self.client.query_dataframe(
            'select factorname from factormetadata').drop_duplicates().factorname.tolist()
        return data

    def get_all_tables(self):
        return self.client.query_dataframe('show tables').drop_duplicates()

    def get_single_factor(self, factorname):
        print(factorname)
        res = self.client.query_dataframe(
            'select * from {}'.format(factorname))
        if len(res) > 0:

            res.columns = ['date', 'code', factorname]
            return res.set_index(['date', 'code']).sort_index()
        else:
            return pd.DataFrame([])

    def unreg_factor(self, factorname):
        self.client.execute(
            "ALTER TABLE factormetadata DELETE WHERE factorname='{}'".format(factorname))
        self.client.execute('drop table {}'.format(factorname))

    def get_all_factor_values(self, factorlist=None):
        factorlist = self.get_all_factorname() if factorlist is None else factorlist

        res = pd.concat([self.get_single_factor(factor)
                         for factor in factorlist], axis=1)

        return res
