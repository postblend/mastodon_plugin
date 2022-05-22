# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

import core.definitions
from core.coredatabase import CoreDatabase

core_db = CoreDatabase.instance(core.definitions.DATABASE_PATH)
assert core_db

plugin_manager = PluginManager.instance()
assert plugin_manager

mastodon_plugin = MastodonPlugin()
mastodon_plugin.init_database_data()

plugin_manager.available_plugins.append(mastodon_plugin)

row_data = mastodon_plugin.account (1)

print (row_data [0], row_data [1], row_data [2], row_data [3])
