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
import nemo
from nemo.core.neural_types import (
    AcousticEncodedRepresentation,
    AudioSignal,
    AxisKind,
    AxisType,
    ChannelType,
    MelSpectrogramType,
    MFCCSpectrogramType,
    NeuralPortNmTensorMismatchError,
    NeuralType,
    NeuralTypeComparisonResult,
    SpectrogramType,
    VoidType,
)
from tests.common_setup import NeMoUnitTest


class NeuralTypeSystemTests(NeMoUnitTest):
    def test_short_vs_long_version(self):
        long_version = NeuralType(
            elements_type=AcousticEncodedRepresentation(),
            axes=(AxisType(AxisKind.Batch, None), AxisType(AxisKind.Dimension, None), AxisType(AxisKind.Time, None)),
        )
        short_version = NeuralType(AcousticEncodedRepresentation(), ('B', 'D', 'T'))
        self.assertEqual(long_version.compare(short_version), NeuralTypeComparisonResult.SAME)
        self.assertEqual(short_version.compare(long_version), NeuralTypeComparisonResult.SAME)

    def test_parameterized_type_audio_sampling_frequency(self):
        audio16K = NeuralType(AudioSignal(16000), axes=('B', 'T'))
        audio8K = NeuralType(AudioSignal(8000), axes=('B', 'T'))
        another16K = NeuralType(AudioSignal(16000), axes=('B', 'T'))

        self.assertEqual(audio8K.compare(audio16K), NeuralTypeComparisonResult.SAME_TYPE_INCOMPATIBLE_PARAMS)
        self.assertEqual(audio16K.compare(audio8K), NeuralTypeComparisonResult.SAME_TYPE_INCOMPATIBLE_PARAMS)
        self.assertEqual(another16K.compare(audio16K), NeuralTypeComparisonResult.SAME)
        self.assertEqual(audio16K.compare(another16K), NeuralTypeComparisonResult.SAME)

    def test_transpose_same_1(self):
        type1 = NeuralType(axes=('B', 'T', 'C'))
        type2 = NeuralType(axes=('T', 'B', 'C'))
        self.assertEqual(type1.compare(type2), NeuralTypeComparisonResult.TRANSPOSE_SAME)
        self.assertEqual(type2.compare(type1), NeuralTypeComparisonResult.TRANSPOSE_SAME)

    def test_transpose_same_2(self):
        audio16K = NeuralType(AudioSignal(16000), axes=('B', 'T'))
        audio16K_t = NeuralType(AudioSignal(16000), axes=('T', 'B'))
        self.assertEqual(audio16K.compare(audio16K_t), NeuralTypeComparisonResult.TRANSPOSE_SAME)

    def test_inheritance_spec_augment_example(self):
        input = NeuralType(SpectrogramType(), ('B', 'D', 'T'))
        out1 = NeuralType(MelSpectrogramType(), ('B', 'D', 'T'))
        out2 = NeuralType(MFCCSpectrogramType(), ('B', 'D', 'T'))
        self.assertEqual(out1.compare(out2), NeuralTypeComparisonResult.INCOMPATIBLE)
        self.assertEqual(out2.compare(out1), NeuralTypeComparisonResult.INCOMPATIBLE)
        self.assertEqual(input.compare(out1), NeuralTypeComparisonResult.GREATER)
        self.assertEqual(input.compare(out2), NeuralTypeComparisonResult.GREATER)
        self.assertEqual(out1.compare(input), NeuralTypeComparisonResult.LESS)
        self.assertEqual(out2.compare(input), NeuralTypeComparisonResult.LESS)

    def test_singletone(self):
        loss_output1 = NeuralType(axes=None)
        loss_output2 = NeuralType(axes=None)
        self.assertEqual(loss_output1.compare(loss_output2), NeuralTypeComparisonResult.SAME)
        self.assertEqual(loss_output2.compare(loss_output1), NeuralTypeComparisonResult.SAME)

    def test_list_of_lists(self):
        T1 = NeuralType(
            elements_type=ChannelType(),
            axes=(
                AxisType(kind=AxisKind.Batch, size=None, is_list=True),
                AxisType(kind=AxisKind.Time, size=None, is_list=True),
                AxisType(kind=AxisKind.Dimension, size=32, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=128, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=256, is_list=False),
            ),
        )
        T2 = NeuralType(
            elements_type=ChannelType(),
            axes=(
                AxisType(kind=AxisKind.Batch, size=None, is_list=False),
                AxisType(kind=AxisKind.Time, size=None, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=32, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=128, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=256, is_list=False),
            ),
        )
        # TODO: should this be incompatible instead???
        self.assertEqual(T1.compare(T2), NeuralTypeComparisonResult.TRANSPOSE_SAME)

    def test_void(self):
        btc_spctr = NeuralType(SpectrogramType(), ('B', 'T', 'C'))
        btc_spct_bad = NeuralType(SpectrogramType(), ('B', 'T'))
        btc_void = NeuralType(VoidType(), ('B', 'T', 'C'))
        self.assertEqual(btc_void.compare(btc_spctr), NeuralTypeComparisonResult.SAME)
        self.assertEqual(btc_spctr.compare(btc_void), NeuralTypeComparisonResult.INCOMPATIBLE)
        self.assertEqual(btc_void.compare(btc_spct_bad), NeuralTypeComparisonResult.INCOMPATIBLE)

    def test_big_void(self):
        big_void_1 = NeuralType(VoidType())
        big_void_2 = NeuralType()

        btc_spctr = NeuralType(SpectrogramType(), ('B', 'T', 'C'))
        btc_spct_bad = NeuralType(SpectrogramType(), ('B', 'T'))
        t1 = NeuralType(
            elements_type=ChannelType(),
            axes=(
                AxisType(kind=AxisKind.Batch, size=None, is_list=True),
                AxisType(kind=AxisKind.Time, size=None, is_list=True),
                AxisType(kind=AxisKind.Dimension, size=32, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=128, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=256, is_list=False),
            ),
        )
        t2 = NeuralType(
            elements_type=ChannelType(),
            axes=(
                AxisType(kind=AxisKind.Batch, size=None, is_list=False),
                AxisType(kind=AxisKind.Time, size=None, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=32, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=128, is_list=False),
                AxisType(kind=AxisKind.Dimension, size=256, is_list=False),
            ),
        )

        self.assertEqual(big_void_1.compare(btc_spctr), NeuralTypeComparisonResult.SAME)
        self.assertEqual(big_void_1.compare(btc_spct_bad), NeuralTypeComparisonResult.SAME)
        self.assertEqual(big_void_1.compare(t1), NeuralTypeComparisonResult.SAME)
        self.assertEqual(big_void_1.compare(t2), NeuralTypeComparisonResult.SAME)

        self.assertEqual(big_void_2.compare(btc_spctr), NeuralTypeComparisonResult.SAME)
        self.assertEqual(big_void_2.compare(btc_spct_bad), NeuralTypeComparisonResult.SAME)
        self.assertEqual(big_void_2.compare(t1), NeuralTypeComparisonResult.SAME)
        self.assertEqual(big_void_2.compare(t2), NeuralTypeComparisonResult.SAME)

    def test_dag(self):
        data_source = nemo.backends.pytorch.tutorials.RealFunctionDataLayer(n=10000, batch_size=128)
        trainable_module = nemo.backends.pytorch.tutorials.TaylorNet(dim=4)
        loss = nemo.backends.pytorch.tutorials.MSELoss()
        x, y = data_source()
        y_pred = trainable_module(x=x)
        _ = loss(predictions=y_pred, target=y)

        def wrong():
            data_source = nemo.backends.pytorch.tutorials.RealFunctionDataLayer(n=10000, batch_size=128)
            trainable_module = nemo.backends.pytorch.tutorials.TaylorNet(dim=4)
            loss = nemo.backends.pytorch.tutorials.MSELoss()
            x, y = data_source()
            loss_tensor = loss(predictions=x, target=x)
            _ = trainable_module(x=loss_tensor)

        self.assertRaises(NeuralPortNmTensorMismatchError, wrong)
