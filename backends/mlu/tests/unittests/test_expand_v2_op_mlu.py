# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
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

from __future__ import print_function

import unittest
import numpy as np
from tests.op_test import OpTest
import paddle.base as base
from paddle.framework import in_pir_mode
import paddle

paddle.enable_static()


# Situation 1: shape is a list(without tensor)
class TestExpandV2OpRank1(OpTest):
    def setUp(self):
        self.op_type = "expand_v2"
        self.place = paddle.CustomPlace("mlu", 0)
        self.__class__.use_custom_device = True
        self.init_data()
        self.python_api = paddle.expand

        self.inputs = {"X": np.random.random(self.ori_shape).astype("float32")}
        self.attrs = {"shape": self.shape}
        output = np.tile(self.inputs["X"], self.expand_times)
        self.outputs = {"Out": output}

    def init_data(self):
        self.ori_shape = [100]
        self.shape = [100]
        self.expand_times = [1]

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad(self):
        self.check_grad(["X"], "Out")


class TestExpandV2OpRank2_DimExpanding(TestExpandV2OpRank1):
    def init_data(self):
        self.ori_shape = [120]
        self.shape = [2, 120]
        self.expand_times = [2, 1]


class TestExpandV2OpRank2(TestExpandV2OpRank1):
    def init_data(self):
        self.ori_shape = [1, 140]
        self.shape = [12, 140]
        self.expand_times = [12, 1]


class TestExpandV2OpRank3_Corner(TestExpandV2OpRank1):
    def init_data(self):
        self.ori_shape = (2, 10, 5)
        self.shape = (2, 10, 5)
        self.expand_times = (1, 1, 1)


class TestExpandV2OpRank4(TestExpandV2OpRank1):
    def init_data(self):
        self.ori_shape = (2, 4, 5, 7)
        self.shape = (-1, -1, -1, -1)
        self.expand_times = (1, 1, 1, 1)


class TestExpandV2OpRank5(TestExpandV2OpRank1):
    def init_data(self):
        self.ori_shape = (2, 4, 1, 15)
        self.shape = (2, -1, 4, -1)
        self.expand_times = (1, 1, 4, 1)


class TestExpandV2OpRank6(TestExpandV2OpRank1):
    def init_data(self):
        self.ori_shape = (4, 1, 30)
        self.shape = (2, -1, 4, 30)
        self.expand_times = (2, 1, 4, 1)


# Situation 2: shape is a list(with tensor)
class TestExpandV2OpRank1_tensor_attr(OpTest):
    def setUp(self):
        self.op_type = "expand_v2"
        self.place = paddle.CustomPlace("mlu", 0)
        self.__class__.use_custom_device = True
        self.init_data()
        expand_shapes_tensor = []
        for index, ele in enumerate(self.expand_shape):
            expand_shapes_tensor.append(
                ("x" + str(index), np.ones((1)).astype("int32") * ele)
            )

        self.inputs = {
            "X": np.random.random(self.ori_shape).astype("float32"),
            "expand_shapes_tensor": expand_shapes_tensor,
        }
        self.attrs = {"shape": self.infer_expand_shape}
        output = np.tile(self.inputs["X"], self.expand_times)
        self.outputs = {"Out": output}

    def init_data(self):
        self.ori_shape = [100]
        self.expand_times = [1]
        self.expand_shape = [100]
        self.infer_expand_shape = [-1]

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad(self):
        self.check_grad(["X"], "Out")


class TestExpandV2OpRank2_Corner_tensor_attr(TestExpandV2OpRank1_tensor_attr):
    def init_data(self):
        self.ori_shape = [12, 14]
        self.expand_times = [1, 1]
        self.expand_shape = [12, 14]
        self.infer_expand_shape = [12, -1]


# Situation 3: shape is a tensor
class TestExpandV2OpRank1_tensor(OpTest):
    def setUp(self):
        self.op_type = "expand_v2"
        self.place = paddle.CustomPlace("mlu", 0)
        self.__class__.use_custom_device = True
        self.init_data()

        self.inputs = {
            "X": np.random.random(self.ori_shape).astype("float32"),
            "Shape": np.array(self.expand_shape).astype("int32"),
        }
        self.attrs = {}
        output = np.tile(self.inputs["X"], self.expand_times)
        self.outputs = {"Out": output}

    def init_data(self):
        self.ori_shape = [100]
        self.expand_times = [2, 1]
        self.expand_shape = [2, 100]

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad(self):
        self.check_grad(["X"], "Out")


# Situation 4: input x is Integer
class TestExpandV2OpInteger(OpTest):
    def setUp(self):
        self.op_type = "expand_v2"
        self.place = paddle.CustomPlace("mlu", 0)
        self.__class__.use_custom_device = True
        self.inputs = {"X": np.random.randint(10, size=(2, 4, 5)).astype("int32")}
        self.attrs = {"shape": [2, 4, 5]}
        output = np.tile(self.inputs["X"], (1, 1, 1))
        self.outputs = {"Out": output}

    def test_check_output(self):
        self.check_output_with_place(self.place)


# Situation 5: input x is Bool
class TestExpandV2OpBoolean(OpTest):
    def setUp(self):
        self.op_type = "expand_v2"
        self.place = paddle.CustomPlace("mlu", 0)
        self.__class__.use_custom_device = True
        self.inputs = {"X": np.random.randint(2, size=(2, 4, 5)).astype("bool")}
        self.attrs = {"shape": [2, 4, 5]}
        output = np.tile(self.inputs["X"], (1, 1, 1))
        self.outputs = {"Out": output}

    def test_check_output(self):
        self.check_output_with_place(self.place)


# Situation 56: input x is Integer
class TestExpandV2OpInt64_t(OpTest):
    def setUp(self):
        self.op_type = "expand_v2"
        self.place = paddle.CustomPlace("mlu", 0)
        self.__class__.use_custom_device = True
        self.inputs = {"X": np.random.randint(10, size=(2, 4, 5)).astype("int64")}
        self.attrs = {"shape": [2, 4, 5]}
        output = np.tile(self.inputs["X"], (1, 1, 1))
        self.outputs = {"Out": output}

    def test_check_output(self):
        self.check_output_with_place(self.place)


class TestExpandV2Error(unittest.TestCase):
    def test_errors(self):
        with paddle.static.program_guard(
            paddle.static.Program(), paddle.static.Program()
        ):
            shape = [2, 2]
            if not in_pir_mode():
                x1 = base.create_lod_tensor(
                    np.array([[-1]]), [[1]], paddle.CustomPlace("mlu", 0)
                )
                self.assertRaises(TypeError, paddle.tensor.expand, x1, shape)
            x2 = paddle.static.data(name="x2", shape=[-1, 4], dtype="bool")
            x2.stop_gradient = False
            self.assertRaises(ValueError, paddle.tensor.expand, x2, shape)
            x2.stop_gradient = True
            self.assertRaises(TypeError, paddle.tensor.expand, x2, 1)


# Test python API
class TestExpandAsV2API(unittest.TestCase):
    def test_api(self):
        input1 = np.random.random([12, 14]).astype("float32")
        input2 = np.random.random([2, 12, 14]).astype("float32")
        x = paddle.static.data(name="x", shape=[12, 14], dtype="float32")

        y = paddle.static.data(name="target_tensor", shape=[2, 12, 14], dtype="float32")

        out_1 = paddle.expand_as(x, y=y)

        exe = base.Executor(place=base.CustomPlace("mlu", 0))
        res_1 = exe.run(
            base.default_main_program(),
            feed={"x": input1, "target_tensor": input2},
            fetch_list=[out_1],
        )
        assert np.array_equal(res_1[0], np.tile(input1, (2, 1, 1)))


if __name__ == "__main__":
    unittest.main()
