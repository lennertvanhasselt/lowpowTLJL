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
from swagger_client.apis.widget_type_controller_api import WidgetTypeControllerApi


class TestWidgetTypeControllerApi(unittest.TestCase):
    """ WidgetTypeControllerApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.widget_type_controller_api.WidgetTypeControllerApi()

    def tearDown(self):
        pass

    def test_delete_widget_type_using_delete(self):
        """
        Test case for delete_widget_type_using_delete

        deleteWidgetType
        """
        pass

    def test_get_bundle_widget_types_using_get(self):
        """
        Test case for get_bundle_widget_types_using_get

        getBundleWidgetTypes
        """
        pass

    def test_get_widget_type_by_id_using_get(self):
        """
        Test case for get_widget_type_by_id_using_get

        getWidgetTypeById
        """
        pass

    def test_get_widget_type_using_get(self):
        """
        Test case for get_widget_type_using_get

        getWidgetType
        """
        pass

    def test_save_widget_type_using_post(self):
        """
        Test case for save_widget_type_using_post

        saveWidgetType
        """
        pass


if __name__ == '__main__':
    unittest.main()
