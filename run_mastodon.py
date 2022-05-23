# import mastodon_plugin
from .mastodon_plugin import *

import core.api.v1.database as database
import core.definitions


# Init singleton instances
core_db = database.CoreDatabase.instance(core.definitions.DATABASE_PATH)
assert core_db

plugin_manager = PluginManager.instance()
assert plugin_manager

mastodon_plugin = MastodonPlugin()
mastodon_plugin.init_database_data()

plugin_manager._available_plugins.append (mastodon_plugin)

# Add user

"""
mastodon_user = {
        mastodon_plugin.name_field: "Work",
        mastodon_plugin.username_field: "some@email.com",
        mastodon_plugin.password_field: "somepassword",
        mastodon_plugin.instance_field: "some.mastodon.instance",
        }

row_id = mastodon_plugin.add_account (mastodon_user)
"""

mastodon_test_post = PostBase
mastodon_test_post.title = "TITLE"
mastodon_test_post.body = "PB test post"

# Post to accounts 1 and 4
plugin_manager.publish_post(mastodon_test_post, {"mastodon_plugin": (1,4)})
