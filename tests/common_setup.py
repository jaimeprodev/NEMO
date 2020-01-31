# ! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2019 NVIDIA. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import unittest

import nemo

logging = nemo.logging


class NeMoUnitTest(unittest.TestCase):
    def setUp(self) -> None:
        nemo.core.neural_factory.NeuralModuleFactory.reset_default_factory()
        logging.info("---------------------------------------------------------")
        logging.info(self._testMethodName)
        logging.info("---------------------------------------------------------")
