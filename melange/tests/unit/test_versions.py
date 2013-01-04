# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import webtest

from melange.common import config
from melange import tests


class TestVersionsController(tests.BaseTest):

    def setUp(self):
        conf, melange_app = config.Config.load_paste_app(
            'melange',
            {"config_file": tests.test_config_file()}, None)
        self.test_app = webtest.TestApp(melange_app)
        super(TestVersionsController, self).setUp()

    def test_versions_index(self):
        response = self.test_app.get("/")
        v01link = [{'href': "http://localhost/v0.1", 'rel': 'self'}]
        v10link = [{'href': "http://localhost/v1.0", 'rel': 'self'}]
        self.assertEqual(response.json, {'versions':
                                         [{'status': 'DEPRECATED',
                                           'name': 'v0.1',
                                           'links': v01link,
                                           },
                                          {'status': 'CURRENT',
                                           'name': 'v1.0',
                                           'links': v10link,
                                           }]
                                         })

    def test_versions_index_for_xml(self):
        response = self.test_app.get("/",
                                     headers={'Accept': "application/xml"})

        self.assertEqual(response.content_type, "application/xml")
        self.assertEqual(response.xml.tag, 'versions')
        self.assertEqual(
            response.body,
            ("<versions>\n"
             "    <version name=\"v0.1\" status=\"DEPRECATED\">\n"
             "        <links>\n"
             "            <link href=\"http://localhost/v0.1\""
             " rel=\"self\"/>\n"
             "        </links>\n"
             "    </version>\n"
             "    <version name=\"v1.0\" status=\"CURRENT\">\n"
             "        <links>\n"
             "            <link href=\"http://localhost/v1.0\""
             " rel=\"self\"/>\n"
             "        </links>\n"
             "    </version>\n"
             "</versions>\n"
             ))
