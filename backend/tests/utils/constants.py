"""Shared test constants."""

import uuid

TEST_SECRET = 'secret-key-for-dev-and-tests-long-enough-for-hs256'

VALID_EMAIL = 'user@example.com'
VALID_PASSWORD = 'Secret@123'

SUFFIX = uuid.uuid4().hex[:8]
MAIN_EMAIL = f'main-{SUFFIX}@example.com'
MAIN_PASSWORD = VALID_PASSWORD
MAIN_NAME = 'Main User'
