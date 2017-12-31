# coding: utf-8

"""
    Thingsboard REST API

    For instructions how to authorize requests please visit <a href='http://thingsboard.io/docs/reference/rest-api/'>REST API documentation page</a>.

    OpenAPI spec version: 2.0
    Contact: info@thingsboard.io
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import os
import sys
import unittest

import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis.rule_controller_api import RuleControllerApi


class TestRuleControllerApi(unittest.TestCase):
    """ RuleControllerApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.rule_controller_api.RuleControllerApi()

    def tearDown(self):
        pass

    def test_activate_rule_by_id_using_post(self):
        """
        Test case for activate_rule_by_id_using_post

        activateRuleById
        """
        pass

    def test_delete_rule_using_delete(self):
        """
        Test case for delete_rule_using_delete

        deleteRule
        """
        pass

    def test_get_rule_by_id_using_get(self):
        """
        Test case for get_rule_by_id_using_get

        getRuleById
        """
        pass

    def test_get_rules_by_plugin_token_using_get(self):
        """
        Test case for get_rules_by_plugin_token_using_get

        getRulesByPluginToken
        """
        pass

    def test_get_rules_using_get(self):
        """
        Test case for get_rules_using_get

        getRules
        """
        pass

    def test_get_system_rules_using_get(self):
        """
        Test case for get_system_rules_using_get

        getSystemRules
        """
        pass

    def test_get_tenant_rules_using_get(self):
        """
        Test case for get_tenant_rules_using_get

        getTenantRules
        """
        pass

    def test_get_tenant_rules_using_get1(self):
        """
        Test case for get_tenant_rules_using_get1

        getTenantRules
        """
        pass

    def test_save_rule_using_post(self):
        """
        Test case for save_rule_using_post

        saveRule
        """
        pass

    def test_suspend_rule_by_id_using_post(self):
        """
        Test case for suspend_rule_by_id_using_post

        suspendRuleById
        """
        pass


if __name__ == '__main__':
    unittest.main()