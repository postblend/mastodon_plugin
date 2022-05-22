# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass

import core.definitions
from core.coredatabase import CoreDatabase
from core.pluginmanager import PluginManager
from core.api.v1.post import PostBase
from core.api.v1.plugin import PlatformPluginBase, BasicPlatformAccount
import core.api.v1.database as database

@dataclass
class MastodonAccount(BasicPlatformAccount):
    """
    BasicPlatformAccount provides 4 generic fields

        * id = identification number of th account (calculated automatically)
        * name = name of the account, i.e. something the user can remembr the account
    by (e.g. "Work Account", "Jokes & Politics", etc.)
        * username = user name used to log in to the account
        * password = the password used to log in to the account

    (In that order)

    To add extra fields (and their type) you need to inherit
    BasicPlatformAccount into a new class and then add your own variables.

    For example, Mastodon needs to now what instance you are gooing to post to, hence...
    """
    instance: str

class MastodonPlugin(PlatformPluginBase):
    def __init__(self):
        self.id = "mastodon_plugin"
        self.name = "Mastodon Plugin"
        self.author = "Meh"
        self.author_url = ""
        self.description = "A plugin to post to Mastodon :)"

        self.name_field = "name"
        self.username_field = "username"
        self.password_field = "password"
        self.instance_field = "instance"


    def init_database_data(self):
        self.plugin_table_name = "mastodon_users_table"
        self.table_data_fields = (
            database.DatabaseFieldDefinition ((self.name_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.username_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.password_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.instance_field, "TEXT", "")),
        )

        database.create_plugin_table(self.plugin_table_name, self.table_data_fields)

        # Add user to table
        #   Fields: user, password, instance
        # Check to see if there is another user with the same instance
        # if not register app with the instance and download secrets to file
        # create a new entry for the instance in the instance table
        #   Fields: instance, secret 1, secret 2 <- Read from File
        # remove the file

        pass



    def cleanup_database_data(self):
        account_ids = self.account_ids()

        for id in account_ids:
            self.delete_account(id)

        print("AFTER DELETE OF ACCOUNTS: ", self.accounts())

        database.delete_plugin_table(self.plugin_table_name)


    def accounts(self) -> tuple:
        accounts_data = database.plugin_data(self.plugin_table_name)
        accounts_tuple = []

        for account in accounts_data:
            basic_plat_acc = MastodonAccount(
                account["id"],
                account[self.name_field],
                account[self.username_field],
                account[self.password_field],
                account[self.instance_field],
            )

            accounts_tuple.append(basic_plat_acc)

        return tuple(accounts_tuple)


    def account_ids(self) -> tuple:
        accounts = self.accounts()
        acc_ids = [account.id for account in accounts]
        return tuple(acc_ids)


    def account(self, account_id: int) -> MastodonAccount:
        account = database.plugin_data_row(self.plugin_table_name, account_id)

        if not account:
            return None

        return MastodonAccount(
            account["id"],
            account[self.name_field],
            account[self.username_field],
            account[self.password_field],
            account[self.instance_field],
        )


    def add_account(self, account_details: dict) -> int:
        return database.add_plugin_data(self.plugin_table_name, account_details)


    def update_account(self, account_id: int, account_details: dict):
        database.update_plugin_data(self.plugin_table_name, account_id, account_details)


    def delete_account(self, account_id: int):
        database.delete_plugin_data(self.plugin_table_name, account_id)


    def publish_post(self, post: PostBase, account_ids: tuple):
        pass
        #for acc_id in account_ids:
            #account_details = self.account(acc_id)

            #if account_details:
                #print(f"""
                    #Post for account '{account_details.name}'

                    #Post title: {post.title}
                    #Post body: {post.body}
                #""")
            #else:
                #print(f"Account with id '{acc_id}' does not exist for this plugin.")

        # publish post
        # grab post id from Mastodon
        # record into post table

