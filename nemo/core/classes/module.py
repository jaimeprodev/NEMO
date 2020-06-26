# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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


__all__ = ['NeuralModule']

from torch.nn import Module

from nemo.core.classes.common import FileIO, Serialization, Typing


class NeuralModule(Module, Typing, Serialization, FileIO):
    """
    Abstract class offering interface shared between all PyTorch Neural Modules.
    """

    def typed_forward(self, **kwargs):
        # TODO: Consider if this can be turned into decorator for __call__ or forward
        self.validate_input_types(in_objects=kwargs)
        result = self.forward(**kwargs)
        self.attach_and_validate_output_types(out_objects=result)
        return result
