# SPDX-FileCopyrightText: 2022 Paul Brown <pbrown@mykolab.com>
# SPDX-License-Identifier: LGPL-2.1-or-later
import sys # added!
sys.path.append("..")

from dataclasses import dataclass
from mastodon import Mastodon

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
    (in that order)

    To add extra fields (and their type) you need to inherit
    BasicPlatformAccount into a new class and then add your own variables.

    For example, Mastodon needs to now what instance you are gooing to post to, hence...
    """
    instance: str

class MastodonPlugin(PlatformPluginBase):
    def __init__(self):
        self.id = "mastodon_plugin"
        self.name = "Mastodon Plugin"
        self.author = "Paul Brown"
        self.author_url = "https://quickfix.es"
        self.description = "A plugin to post to Mastodon :)"

        # Mastodon user table fields
        self.name_field = "name"
        self.username_field = "username"
        self.password_field = "password"
        self.instance_field = "instance"

        # Mastodon instance table fields
        self.url_field = "url" # URL WUTHOUT "https://"
        self.client_id_field = "client_id"
        self.client_secret_field = "client_secret"

        # Mastodon post table fields
        self.post_url_field = "link"
        self.uid_field = "user_id"


    def init_database_data(self):
        # Get user table ready or create it if it doesn't exist
        self.plugin_table_name = "mastodon_users_table"
        self.table_data_fields = (
            database.DatabaseFieldDefinition ((self.name_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.username_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.password_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.instance_field, "TEXT", "")),
        )
        database.create_plugin_table(self.plugin_table_name, self.table_data_fields)

        # Get mastodon instance table ready or create it if it doesn't exist
        self.instance_table_name = "mastodon_instances_table"
        self.table_instance_data_fields = (
            database.DatabaseFieldDefinition ((self.url_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.client_id_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.client_secret_field, "TEXT", ""))
        )
        database.create_plugin_table(self.instance_table_name, self.table_instance_data_fields)

        # Get mastodon posts table ready or create it if it doesn't exist
        self.posts_table_name = "mastodon_links_table"
        self.table_links_data_fields = (
            database.DatabaseFieldDefinition ((self.uid_field, "INTEGER", "")),
            database.DatabaseFieldDefinition ((self.post_url_field, "TEXT", ""))
        )
        database.create_plugin_table(self.posts_table_name, self.table_links_data_fields)

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
        # Check to see if the user's instance is already registered
        # and, if not, add it to the instance table
        if not database.plugin_data_value(self.instance_table_name, self.url_field, account_details[self.instance_field]):
            self.add_instance(account_details[self.instance_field])

        return database.add_plugin_data(self.plugin_table_name, account_details)


    def update_account(self, account_id: int, account_details: dict):
        database.update_plugin_data(self.plugin_table_name, account_id, account_details)


    def delete_account(self, account_id: int):
        database.delete_plugin_data(self.plugin_table_name, account_id)

    def add_instance(self, instance):
        # Grab secrets from mastodon instance
        secrets = (Mastodon.create_app(client_name = "PostBlendTest", api_base_url = instance))

        # Create a new entry for the instance in the instance table
        instance_details = {
                self.url_field : instance,
                self.client_id_field : secrets[0],
                self.client_secret_field : secrets[1]
                }

        database.add_plugin_data(self.instance_table_name, instance_details)

    def publish_post(self, post: PostBase, account_ids: tuple):
        for acc_id in account_ids:
            account_details = self.account(acc_id)
            instance_details = database.plugin_data_value(self.instance_table_name, self.url_field, account_details.instance)

            if account_details:
                mastodon = Mastodon (
                            instance_details[self.client_id_field],
                            instance_details[self.client_secret_field],
                            api_base_url = "https://" + instance_details[self.url_field]
                            )
                mastodon.access_token = mastodon.log_in (
                            username = account_details.username,
                            password = account_details.password
                            )

                # Store post location for later reference
                post_data = mastodon.status_post(post.body)
                post_details = {
                    self.uid_field : acc_id,
                    self.post_url_field : post_data["uri"]
                    }
                database.add_plugin_data(self.posts_table_name, post_details)

            else:
                print(f"Account with id '{acc_id}' does not exist for this plugin.")


"""
TODO

* Be able to attach media
"""
