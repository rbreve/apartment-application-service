import os

import environ

test_env = environ.Env(
    TEST_APARTMENT_INDEX_NAME=(str, "test-apartment"),
    TEST_ELASTICSEARCH_URL=(str, "http://127.0.0.1"),
    TEST_ELASTICSEARCH_PORT=(int, 9200),
    TEST_ELASTICSEARCH_USERNAME=(str, ""),
    TEST_ELASTICSEARCH_PASSWORD=(str, ""),
    TEST_LOG_LEVEL=(str, "INFO"),
)

# Set LOG_LEVEL environment variable before importing real settings
os.environ.setdefault("LOG_LEVEL", test_env("TEST_LOG_LEVEL"))

from ..settings import *  # noqa: E402, F401, F403

TEST_APARTMENT_INDEX_NAME = test_env("TEST_APARTMENT_INDEX_NAME")
APARTMENT_INDEX_NAME = TEST_APARTMENT_INDEX_NAME

ELASTICSEARCH_URL = test_env("TEST_ELASTICSEARCH_URL")
ELASTICSEARCH_PORT = test_env("TEST_ELASTICSEARCH_PORT")
ELASTICSEARCH_USERNAME = test_env("TEST_ELASTICSEARCH_USERNAME")
ELASTICSEARCH_PASSWORD = test_env("TEST_ELASTICSEARCH_PASSWORD")
