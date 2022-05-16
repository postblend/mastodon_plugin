# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from core.api.v1.plugin import PlatformPluginBase
from core.api.v1.post import PostBase
import core.api.v1.database as database

class MastodonPlugin(PlatformPluginBase):
    def __init__(self):
        self.id = "mastodon_plugin"
        self.name = "Mastodon Plugin"
        self.author = "Meh"
        self.author_url = ""
        self.description = "A plugin to post to Mastodon :)"

        self.username_field = "username"
        self.password_field = "password"
        self.instance_field = "instance"


    def init_database_data(self):
        self.plugin_table_name = "mastodon_users_table"
        self.table_data_fields = (
            database.DatabaseFieldDefinition ((self.username_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.password_field, "TEXT", "")),
            database.DatabaseFieldDefinition ((self.instance_field, "TEXT", ""))
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
            basic_plat_acc = BasicPlatformAccount(
                account["id"],
                account[self.username_field],
                account[self.username_field],
                account[self.password_field]
            )

            accounts_tuple.append(basic_plat_acc)

        return tuple(accounts_tuple)


    def account_ids(self) -> tuple:
        accounts = self.accounts()
        acc_ids = [account.id for account in accounts]
        return tuple(acc_ids)


    def account(self, account_id: int) -> BasicPlatformAccount:
        account = database.plugin_data_row(self.plugin_table_name, account_id)

        if not account:
            return None

        return BasicPlatformAccount(
            account["id"],
            account[self.username_field],
            account[self.password_field],
            account[self.instance_field]
        )


    def add_account(self, account_details: dict) -> int:
        return database.add_plugin_data(self.plugin_table_name, account_details)


    def update_account(self, account_id: int, account_details: dict):
        database.update_plugin_data(self.plugin_table_name, account_id, account_details)


    def delete_account(self, account_id: int):
        database.delete_plugin_data(self.plugin_table_name, account_id)


    def publish_post(self, post: PostBase, account_ids: tuple):
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



# Init singleton instances
core_db = CoreDatabase.instance(core.definitions.DATABASE_PATH)
assert core_db

plugin_manager = PluginManager.instance()
assert plugin_manager

mastodon_plugin = MastodonPlugin()
mastodon_plugin.init_database_data()

plugin_manager.available_plugins.append(mastodon_plugin)

# Add user

mastodon_user = {mastodon_plugin.username_field: "paul", mastodon_plugin.password_field: "TFWTWTWFTWF", mastodon_plugin.instance_field: "some.instance.social" }
row_id = mastodon_plugin.add_account (mastodon_user)
row_data = mastodon_plugin.account (row_id)

print (row_data [0], row_data [1], row_data [2], row_data [3])

#mastodon_test_post = PostBase
#mastodon_test_post.body = "PB post body!"

#plugin_manager.publish_post(mastodon_test_post, {"mastodon_plugin": (0,1)})
