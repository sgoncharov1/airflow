# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from airflow.models import Connection
from airflow.providers.microsoft.azure.hooks.base_azure import AzureBaseHook

pytestmark = pytest.mark.db_test


class TestBaseAzureHook:
    @pytest.mark.parametrize(
        "mocked_connection",
        [Connection(conn_id="azure_default", extra={"key_path": "key_file.json"})],
        indirect=True,
    )
    @patch("airflow.providers.microsoft.azure.hooks.base_azure.get_client_from_auth_file")
    def test_get_conn_with_key_path(self, mock_get_client_from_auth_file, mocked_connection):
        mock_get_client_from_auth_file.return_value = "foo-bar"
        mock_sdk_client = Mock()

        auth_sdk_client = AzureBaseHook(mock_sdk_client).get_conn()

        mock_get_client_from_auth_file.assert_called_once_with(
            client_class=mock_sdk_client, auth_path=mocked_connection.extra_dejson["key_path"]
        )
        assert auth_sdk_client == "foo-bar"

    @pytest.mark.parametrize(
        "mocked_connection",
        [Connection(conn_id="azure_default", extra={"key_json": {"test": "test"}})],
        indirect=True,
    )
    @patch("airflow.providers.microsoft.azure.hooks.base_azure.get_client_from_json_dict")
    def test_get_conn_with_key_json(self, mock_get_client_from_json_dict, mocked_connection):
        mock_sdk_client = Mock()
        mock_get_client_from_json_dict.return_value = "foo-bar"
        auth_sdk_client = AzureBaseHook(mock_sdk_client).get_conn()

        mock_get_client_from_json_dict.assert_called_once_with(
            client_class=mock_sdk_client, config_dict=mocked_connection.extra_dejson["key_json"]
        )
        assert auth_sdk_client == "foo-bar"

    @patch("airflow.providers.microsoft.azure.hooks.base_azure.ServicePrincipalCredentials")
    @pytest.mark.parametrize(
        "mocked_connection",
        [
            Connection(
                conn_id="azure_default",
                login="my_login",
                password="my_password",
                extra={"tenantId": "my_tenant", "subscriptionId": "my_subscription"},
            )
        ],
        indirect=True,
    )
    def test_get_conn_with_credentials(self, mock_spc, mocked_connection):
        mock_sdk_client = Mock(return_value="spam-egg")
        mock_spc.return_value = "foo-bar"
        auth_sdk_client = AzureBaseHook(mock_sdk_client).get_conn()

        mock_spc.assert_called_once_with(
            client_id=mocked_connection.login,
            secret=mocked_connection.password,
            tenant=mocked_connection.extra_dejson["tenantId"],
        )
        mock_sdk_client.assert_called_once_with(
            credentials="foo-bar",
            subscription_id=mocked_connection.extra_dejson["subscriptionId"],
        )
        assert auth_sdk_client == "spam-egg"
