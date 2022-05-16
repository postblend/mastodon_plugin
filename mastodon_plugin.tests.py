# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

import core.definitions
from core.coredatabase import CoreDatabase

core_db = CoreDatabase.instance(core.definitions.DATABASE_PATH)
assert core_db

core_db.add_user_account("user", "password", "Test User Account")
print("Checking test user credentials")
assert core_db.valid_login("user", "pass")