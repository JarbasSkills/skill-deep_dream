# Adapted from https://github.com/ProGamerGov/Protobuf-Dreamer

from mycroft.skills.core import MycroftSkill, Message, dig_for_message
from imgurpython import ImgurClient
import urllib2
from mycroft.util.log import LOG
import json
from bs4 import BeautifulSoup
from os.path import join
import tensorflow as tf
from pypexels import PyPexels
try:
    import yagmail
except ImportError:
    yagmail = None

__author__ = 'jarbas'


class DreamSkill(MycroftSkill):
    def __init__(self):
        super(DreamSkill, self).__init__()

        # free keys for the people
        if "use_pexels" not in self.settings:
            self.settings["use_pexels"] = False
        if "pexels" not in self.settings:
            self.settings["pexels"] = "563492ad6f91700001000001c7b3c09baae746f648a8cdfceef1362c"
        if "client_id" not in self.settings:
            self.settings["client_id"] = "0357b39cbf22749"
        if "client_secret" not in self.settings:
            self.settings["client_secret"] = "15f679a7147c12407913aeb0ff893e6156fba16b"

        client_id = self.settings.get("client_id")
        client_secret = self.settings.get("client_secret")

        self.client = ImgurClient(client_id, client_secret)

        # TODO test all layers, not sure they all can be dreamed on
        self.layers = ['conv2d0_w',
                       'conv2d0_b',
                       'conv2d1_w',
                       'conv2d1_b',
                       'conv2d2_w',
                       'conv2d2_b',
                       'mixed3a_1x1_w',
                       'mixed3a_1x1_b',
                       'mixed3a_3x3_bottleneck_w',
                       'mixed3a_3x3_bottleneck_b',
                       'mixed3a_3x3_w',
                       'mixed3a_3x3_b',
                       'mixed3a_5x5_bottleneck_w',
                       'mixed3a_5x5_bottleneck_b',
                       'mixed3a_5x5_w',
                       'mixed3a_5x5_b',
                       'mixed3a_pool_reduce_w',
                       'mixed3a_pool_reduce_b',
                       'mixed3b_1x1_w',
                       'mixed3b_1x1_b',
                       'mixed3b_3x3_bottleneck_w',
                       'mixed3b_3x3_bottleneck_b',
                       'mixed3b_3x3_w',
                       'mixed3b_3x3_b',
                       'mixed3b_5x5_bottleneck_w',
                       'mixed3b_5x5_bottleneck_b',
                       'mixed3b_5x5_w',
                       'mixed3b_5x5_b',
                       'mixed3b_pool_reduce_w',
                       'mixed3b_pool_reduce_b',
                       'mixed4a_1x1_w',
                       'mixed4a_1x1_b',
                       'mixed4a_3x3_bottleneck_w',
                       'mixed4a_3x3_bottleneck_b',
                       'mixed4a_3x3_w',
                       'mixed4a_3x3_b',
                       'mixed4a_5x5_bottleneck_w',
                       'mixed4a_5x5_bottleneck_b',
                       'mixed4a_5x5_w',
                       'mixed4a_5x5_b',
                       'mixed4a_pool_reduce_w',
                       'mixed4a_pool_reduce_b',
                       'mixed4b_1x1_w',
                       'mixed4b_1x1_b',
                       'mixed4b_3x3_bottleneck_w',
                       'mixed4b_3x3_bottleneck_b',
                       'mixed4b_3x3_w',
                       'mixed4b_3x3_b',
                       'mixed4b_5x5_bottleneck_w',
                       'mixed4b_5x5_bottleneck_b',
                       'mixed4b_5x5_w',
                       'mixed4b_5x5_b',
                       'mixed4b_pool_reduce_w',
                       'mixed4b_pool_reduce_b',
                       'mixed4c_1x1_w',
                       'mixed4c_1x1_b',
                       'mixed4c_3x3_bottleneck_w',
                       'mixed4c_3x3_bottleneck_b',
                       'mixed4c_3x3_w',
                       'mixed4c_3x3_b',
                       'mixed4c_5x5_bottleneck_w',
                       'mixed4c_5x5_bottleneck_b',
                       'mixed4c_5x5_w',
                       'mixed4c_5x5_b',
                       'mixed4c_pool_reduce_w',
                       'mixed4c_pool_reduce_b',
                       'mixed4d_1x1_w',
                       'mixed4d_1x1_b',
                       'mixed4d_3x3_bottleneck_w',
                       'mixed4d_3x3_bottleneck_b',
                       'mixed4d_3x3_w',
                       'mixed4d_3x3_b',
                       'mixed4d_5x5_bottleneck_w',
                       'mixed4d_5x5_bottleneck_b',
                       'mixed4d_5x5_w',
                       'mixed4d_5x5_b',
                       'mixed4d_pool_reduce_w',
                       'mixed4d_pool_reduce_b',
                       'mixed4e_1x1_w',
                       'mixed4e_1x1_b',
                       'mixed4e_3x3_bottleneck_w',
                       'mixed4e_3x3_bottleneck_b',
                       'mixed4e_3x3_w',
                       'mixed4e_3x3_b',
                       'mixed4e_5x5_bottleneck_w',
                       'mixed4e_5x5_bottleneck_b',
                       'mixed4e_5x5_w',
                       'mixed4e_5x5_b',
                       'mixed4e_pool_reduce_w',
                       'mixed4e_pool_reduce_b',
                       'mixed5a_1x1_w',
                       'mixed5a_1x1_b',
                       'mixed5a_3x3_bottleneck_w',
                       'mixed5a_3x3_bottleneck_b',
                       'mixed5a_3x3_w',
                       'mixed5a_3x3_b',
                       'mixed5a_5x5_bottleneck_w',
                       'mixed5a_5x5_bottleneck_b',
                       'mixed5a_5x5_w',
                       'mixed5a_5x5_b',
                       'mixed5a_pool_reduce_w',
                       'mixed5a_pool_reduce_b',
                       'mixed5b_1x1_w',
                       'mixed5b_1x1_b',
                       'mixed5b_3x3_bottleneck_w',
                       'mixed5b_3x3_bottleneck_b',
                       'mixed5b_3x3_w',
                       'mixed5b_3x3_b',
                       'mixed5b_5x5_bottleneck_w',
                       'mixed5b_5x5_bottleneck_b',
                       'mixed5b_5x5_w',
                       'mixed5b_5x5_b',
                       'mixed5b_pool_reduce_w',
                       'mixed5b_pool_reduce_b',
                       'head0_bottleneck_w',
                       'head0_bottleneck_b',
                       'nn0_w',
                       'nn0_b',
                       'softmax0_w',
                       'softmax0_b',
                       'head1_bottleneck_w',
                       'head1_bottleneck_b',
                       'nn1_w',
                       'nn1_b',
                       'softmax1_w',
                       'softmax1_b',
                       'softmax2_w',
                       'softmax2_b',
                       'conv2d0_pre_relu/conv',
                       'conv2d0_pre_relu',
                       'conv2d0',
                       'maxpool0',
                       'localresponsenorm0',
                       'conv2d1_pre_relu/conv',
                       'conv2d1_pre_relu',
                       'conv2d1',
                       'conv2d2_pre_relu/conv',
                       'conv2d2_pre_relu',
                       'conv2d2',
                       'localresponsenorm1',
                       'maxpool1',
                       'mixed3a_1x1_pre_relu/conv',
                       'mixed3a_1x1_pre_relu',
                       'mixed3a_1x1',
                       'mixed3a_3x3_bottleneck_pre_relu/conv',
                       'mixed3a_3x3_bottleneck_pre_relu',
                       'mixed3a_3x3_bottleneck',
                       'mixed3a_3x3_pre_relu/conv',
                       'mixed3a_3x3_pre_relu',
                       'mixed3a_3x3',
                       'mixed3a_5x5_bottleneck_pre_relu/conv',
                       'mixed3a_5x5_bottleneck_pre_relu',
                       'mixed3a_5x5_bottleneck',
                       'mixed3a_5x5_pre_relu/conv',
                       'mixed3a_5x5_pre_relu',
                       'mixed3a_5x5',
                       'mixed3a_pool',
                       'mixed3a_pool_reduce_pre_relu/conv',
                       'mixed3a_pool_reduce_pre_relu',
                       'mixed3a_pool_reduce',
                       'mixed3a/concat_dim',
                       'mixed3a',
                       'mixed3b_1x1_pre_relu/conv',
                       'mixed3b_1x1_pre_relu',
                       'mixed3b_1x1',
                       'mixed3b_3x3_bottleneck_pre_relu/conv',
                       'mixed3b_3x3_bottleneck_pre_relu',
                       'mixed3b_3x3_bottleneck',
                       'mixed3b_3x3_pre_relu/conv',
                       'mixed3b_3x3_pre_relu',
                       'mixed3b_3x3',
                       'mixed3b_5x5_bottleneck_pre_relu/conv',
                       'mixed3b_5x5_bottleneck_pre_relu',
                       'mixed3b_5x5_bottleneck',
                       'mixed3b_5x5_pre_relu/conv',
                       'mixed3b_5x5_pre_relu',
                       'mixed3b_5x5',
                       'mixed3b_pool',
                       'mixed3b_pool_reduce_pre_relu/conv',
                       'mixed3b_pool_reduce_pre_relu',
                       'mixed3b_pool_reduce',
                       'mixed3b/concat_dim',
                       'mixed3b',
                       'maxpool4',
                       'mixed4a_1x1_pre_relu/conv',
                       'mixed4a_1x1_pre_relu',
                       'mixed4a_1x1',
                       'mixed4a_3x3_bottleneck_pre_relu/conv',
                       'mixed4a_3x3_bottleneck_pre_relu',
                       'mixed4a_3x3_bottleneck',
                       'mixed4a_3x3_pre_relu/conv',
                       'mixed4a_3x3_pre_relu',
                       'mixed4a_3x3',
                       'mixed4a_5x5_bottleneck_pre_relu/conv',
                       'mixed4a_5x5_bottleneck_pre_relu',
                       'mixed4a_5x5_bottleneck',
                       'mixed4a_5x5_pre_relu/conv',
                       'mixed4a_5x5_pre_relu',
                       'mixed4a_5x5',
                       'mixed4a_pool',
                       'mixed4a_pool_reduce_pre_relu/conv',
                       'mixed4a_pool_reduce_pre_relu',
                       'mixed4a_pool_reduce',
                       'mixed4a/concat_dim',
                       'mixed4a',
                       'mixed4b_1x1_pre_relu/conv',
                       'mixed4b_1x1_pre_relu',
                       'mixed4b_1x1',
                       'mixed4b_3x3_bottleneck_pre_relu/conv',
                       'mixed4b_3x3_bottleneck_pre_relu',
                       'mixed4b_3x3_bottleneck',
                       'mixed4b_3x3_pre_relu/conv',
                       'mixed4b_3x3_pre_relu',
                       'mixed4b_3x3',
                       'mixed4b_5x5_bottleneck_pre_relu/conv',
                       'mixed4b_5x5_bottleneck_pre_relu',
                       'mixed4b_5x5_bottleneck',
                       'mixed4b_5x5_pre_relu/conv',
                       'mixed4b_5x5_pre_relu',
                       'mixed4b_5x5',
                       'mixed4b_pool',
                       'mixed4b_pool_reduce_pre_relu/conv',
                       'mixed4b_pool_reduce_pre_relu',
                       'mixed4b_pool_reduce',
                       'mixed4b/concat_dim',
                       'mixed4b',
                       'mixed4c_1x1_pre_relu/conv',
                       'mixed4c_1x1_pre_relu',
                       'mixed4c_1x1',
                       'mixed4c_3x3_bottleneck_pre_relu/conv',
                       'mixed4c_3x3_bottleneck_pre_relu',
                       'mixed4c_3x3_bottleneck',
                       'mixed4c_3x3_pre_relu/conv',
                       'mixed4c_3x3_pre_relu',
                       'mixed4c_3x3',
                       'mixed4c_5x5_bottleneck_pre_relu/conv',
                       'mixed4c_5x5_bottleneck_pre_relu',
                       'mixed4c_5x5_bottleneck',
                       'mixed4c_5x5_pre_relu/conv',
                       'mixed4c_5x5_pre_relu',
                       'mixed4c_5x5',
                       'mixed4c_pool',
                       'mixed4c_pool_reduce_pre_relu/conv',
                       'mixed4c_pool_reduce_pre_relu',
                       'mixed4c_pool_reduce',
                       'mixed4c/concat_dim',
                       'mixed4c',
                       'mixed4d_1x1_pre_relu/conv',
                       'mixed4d_1x1_pre_relu',
                       'mixed4d_1x1',
                       'mixed4d_3x3_bottleneck_pre_relu/conv',
                       'mixed4d_3x3_bottleneck_pre_relu',
                       'mixed4d_3x3_bottleneck',
                       'mixed4d_3x3_pre_relu/conv',
                       'mixed4d_3x3_pre_relu',
                       'mixed4d_3x3',
                       'mixed4d_5x5_bottleneck_pre_relu/conv',
                       'mixed4d_5x5_bottleneck_pre_relu',
                       'mixed4d_5x5_bottleneck',
                       'mixed4d_5x5_pre_relu/conv',
                       'mixed4d_5x5_pre_relu',
                       'mixed4d_5x5',
                       'mixed4d_pool',
                       'mixed4d_pool_reduce_pre_relu/conv',
                       'mixed4d_pool_reduce_pre_relu',
                       'mixed4d_pool_reduce',
                       'mixed4d/concat_dim',
                       'mixed4d',
                       'mixed4e_1x1_pre_relu/conv',
                       'mixed4e_1x1_pre_relu',
                       'mixed4e_1x1',
                       'mixed4e_3x3_bottleneck_pre_relu/conv',
                       'mixed4e_3x3_bottleneck_pre_relu',
                       'mixed4e_3x3_bottleneck',
                       'mixed4e_3x3_pre_relu/conv',
                       'mixed4e_3x3_pre_relu',
                       'mixed4e_3x3',
                       'mixed4e_5x5_bottleneck_pre_relu/conv',
                       'mixed4e_5x5_bottleneck_pre_relu',
                       'mixed4e_5x5_bottleneck',
                       'mixed4e_5x5_pre_relu/conv',
                       'mixed4e_5x5_pre_relu',
                       'mixed4e_5x5',
                       'mixed4e_pool',
                       'mixed4e_pool_reduce_pre_relu/conv',
                       'mixed4e_pool_reduce',
                       'mixed4e/concat_dim',
                       'mixed4e',
                       'maxpool10',
                       'mixed5a_1x1_pre_relu/conv',
                       'mixed5a_1x1_pre_relu',
                       'mixed5a_1x1',
                       'mixed5a_3x3_bottleneck_pre_relu/conv',
                       'mixed5a_3x3_bottleneck_pre_relu',
                       'mixed5a_3x3_bottleneck',
                       'mixed5a_3x3_pre_relu/conv',
                       'mixed5a_3x3_pre_relu',
                       'mixed5a_3x3',
                       'mixed5a_5x5_bottleneck_pre_relu/conv',
                       'mixed5a_5x5_bottleneck_pre_relu',
                       'mixed5a_5x5_bottleneck',
                       'mixed5a_5x5_pre_relu/conv',
                       'mixed5a_5x5_pre_relu',
                       'mixed5a_5x5',
                       'mixed5a_pool',
                       'mixed5a_pool_reduce_pre_relu/conv',
                       'mixed5a_pool_reduce_pre_relu',
                       'mixed5a_pool_reduce',
                       'mixed5a/concat_dim',
                       'mixed5a',
                       'mixed5b_1x1_pre_relu/conv',
                       'mixed5b_1x1_pre_relu',
                       'mixed5b_1x1',
                       'mixed5b_3x3_bottleneck_pre_relu/conv',
                       'mixed5b_3x3_bottleneck_pre_relu',
                       'mixed5b_3x3_bottleneck',
                       'mixed5b_3x3_pre_relu/conv',
                       'mixed5b_3x3_pre_relu',
                       'mixed5b_3x3',
                       'mixed5b_5x5_bottleneck_pre_relu/conv',
                       'mixed5b_5x5_bottleneck_pre_relu',
                       'mixed5b_5x5_bottleneck',
                       'mixed5b_5x5_pre_relu/conv',
                       'mixed5b_5x5_pre_relu',
                       'mixed5b_5x5',
                       'mixed5b_pool',
                       'mixed5b_pool_reduce_pre_relu/conv',
                       'mixed5b_pool_reduce_pre_relu',
                       'mixed5b_pool_reduce',
                       'mixed5b/concat_dim',
                       'mixed5b',
                       'avgpool0',
                       'head0_pool',
                       'head0_bottleneck_pre_relu/conv',
                       'head0_bottleneck_pre_relu',
                       'head0_bottleneck',
                       'head0_bottleneck/reshape/shape',
                       'head0_bottleneck/reshape',
                       'nn0_pre_relu/matmul',
                       'nn0_pre_relu',
                       'nn0',
                       'nn0/reshape/shape',
                       'nn0/reshape',
                       'softmax0_pre_activation/matmul',
                       'softmax0_pre_activation',
                       'softmax0',
                       'head1_pool',
                       'head1_bottleneck_pre_relu/conv',
                       'head1_bottleneck_pre_relu',
                       'head1_bottleneck',
                       'head1_bottleneck/reshape/shape',
                       'head1_bottleneck/reshape',
                       'nn1_pre_relu/matmul',
                       'nn1_pre_relu',
                       'nn1',
                       'nn1/reshape/shape',
                       'nn1/reshape',
                       'softmax1_pre_activation/matmul',
                       'softmax1_pre_activation',
                       'softmax1',
                       'avgpool0/reshape/shape',
                       'avgpool0/reshape',
                       'softmax2_pre_activation/matmul',
                       'softmax2_pre_activation',
                       'softmax2']
        self.layer_nicknames = {
            "plants": ["mixed4a_3x3_bottleneck_pre_relu", 84],
            "fractals": ["mixed4a_3x3_bottleneck_pre_relu", 83],
            "snakes and lizards": ["mixed4c_pool_reduce", 7],
            "feathers": ["mixed4c_pool_reduce", 14],
            "rodents": ["mixed4c_pool_reduce", 23],
            "spirals": ["mixed4c_pool_reduce", 53],
            "3d": ["mixed4c_pool_reduce", 54],
            "shiny": ["mixed4c_pool_reduce", 56],
            "houses": ["mixed4c_pool_reduce", 61],
            "fish": ["mixed5a_1x1", 158],
            "balls": ["mixed5a_1x1", 9],
            "bark": ["mixed5a_1x1", 107],
            "clocks": ["mixed5a_1x1", 134],
            "flowers on metal": ["mixed5a_1x1", 198],
            "quadrilaterals": ["mixed4c", 56],
            "letters": ["mixed4c", 87],
            "squares": ["mixed4a_3x3_bottleneck_pre_relu", 51],
            "wool": ["mixed4e", 62],
            "arches": ["mixed4c", 477],
            "fluffy dogs": ["mixed4c", 111],
            "flowers": ["mixed4c_3x3_bottleneck", 30],
        }

        if "iter_value" not in self.settings:
            self.settings["iter_value"] = 20
        if "octave_value" not in self.settings:
            self.settings["octave_value"] = 4
        if "octave_scale_value" not in self.settings:
            self.settings["octave_scale_value"] = 1.4
        if "step_size" not in self.settings:
            self.settings["step_size"] = 1.5
        if "tile_size" not in self.settings:
            self.settings["tile_size"] = 512
        if "model_folder" not in self.settings:
            self.settings["model_folder"] = \
                expanduser("~/tensorflow_models/inception5h")
        if "model" not in self.settings:
            self.settings["model"] = join(self.settings["model_folder"], "tensorflow_inception_graph.pb")
        if "print_model" not in self.settings:
            self.settings["print_model"] = True
        if "verbose" not in self.settings:
            self.settings["verbose"] = True
        if "output_dir" not in self.settings:
            self.settings["output_dir"] = expanduser("~/dreams")

        if "layers" not in self.settings:
            self.settings["layers"] = ['conv2d2_pre_relu/conv', 'conv2d2_pre_relu',
                        'conv2d2', 'localresponsenorm1', 'maxpool1', 'mixed3a_pool', 'mixed3a', 'mixed3b_3x3_pre_relu/conv', 'mixed3b_3x3_pre_relu', 'mixed3b_3x3', 'mixed3b_5x5_bottleneck_pre_relu/conv', 'mixed3b_5x5_bottleneck_pre_relu', 'mixed3b_5x5_bottleneck', 'mixed3b_5x5_pre_relu/conv', 'mixed3b_5x5_pre_relu', 'mixed3b_5x5', 'mixed3b_pool', 'mixed3b_pool_reduce_pre_relu/conv', 'mixed3b_pool_reduce_pre_relu', 'mixed3b_pool_reduce', 'mixed3b/concat_dim', 'mixed3b', 'maxpool4', 'mixed4a_1x1_pre_relu/conv', 'mixed4a_1x1_pre_relu', 'mixed4a_1x1', 'mixed4a_3x3_bottleneck_pre_relu/conv', 'mixed4a_3x3_bottleneck_pre_relu', 'mixed4a_3x3_bottleneck', 'mixed4a_3x3_pre_relu/conv', 'mixed4a_3x3_pre_relu', 'mixed4a_3x3', 'mixed4a_5x5_bottleneck_pre_relu/conv', 'mixed4a_5x5_bottleneck_pre_relu', 'mixed4a_5x5_bottleneck', 'mixed4a_5x5_pre_relu/conv', 'mixed4a_5x5_pre_relu', 'mixed4a_5x5', 'mixed4a_pool', 'mixed4a_pool_reduce_pre_relu/conv', 'mixed4a_pool_reduce_pre_relu', 'mixed4a_pool_reduce', 'mixed4a/concat_dim', 'mixed4a', 'mixed4b_1x1_pre_relu/conv', 'mixed4b_1x1_pre_relu', 'mixed4b_1x1', 'mixed4b_3x3_bottleneck_pre_relu/conv', 'mixed4b_3x3_bottleneck_pre_relu', 'mixed4b_3x3_bottleneck', 'mixed4b_3x3_pre_relu/conv', 'mixed4b_3x3_pre_relu', 'mixed4b_3x3', 'mixed4b_5x5_bottleneck_pre_relu/conv', 'mixed4b_5x5_bottleneck_pre_relu', 'mixed4b_5x5_bottleneck', 'mixed4b_5x5_pre_relu/conv', 'mixed4b_5x5_pre_relu', 'mixed4b_5x5', 'mixed4b_pool', 'mixed4b_pool_reduce_pre_relu/conv', 'mixed4b_pool_reduce_pre_relu', 'mixed4b_pool_reduce', 'mixed4b/concat_dim', 'mixed4b', 'mixed4c_1x1_pre_relu/conv', 'mixed4c_1x1_pre_relu', 'mixed4c_1x1', 'mixed4c_3x3_bottleneck_pre_relu/conv', 'mixed4c_3x3_bottleneck_pre_relu', 'mixed4c_3x3_bottleneck', 'mixed4c_3x3_pre_relu/conv', 'mixed4c_3x3_pre_relu', 'mixed4c_3x3', 'mixed4c_5x5_bottleneck_pre_relu/conv', 'mixed4c_5x5_bottleneck_pre_relu', 'mixed4c_5x5_bottleneck', 'mixed4c_5x5_pre_relu/conv', 'mixed4c_5x5_pre_relu', 'mixed4c_5x5', 'mixed4c_pool', 'mixed4c_pool_reduce_pre_relu/conv', 'mixed4c_pool_reduce_pre_relu', 'mixed4c_pool_reduce', 'mixed4c/concat_dim', 'mixed4c', 'mixed4d_1x1_pre_relu/conv', 'mixed4d_1x1_pre_relu', 'mixed4d_1x1', 'mixed4d_3x3_bottleneck_pre_relu/conv', 'mixed4d_3x3_bottleneck_pre_relu', 'mixed4d_3x3_bottleneck', 'mixed4d_3x3_pre_relu/conv', 'mixed4d_3x3_pre_relu', 'mixed4d_3x3', 'mixed4d_5x5_bottleneck_pre_relu/conv', 'mixed4d_5x5_bottleneck_pre_relu', 'mixed4d_5x5_bottleneck', 'mixed4d_5x5_pre_relu/conv', 'mixed4d_5x5_pre_relu', 'mixed4d_5x5', 'mixed4d_pool', 'mixed4d_pool_reduce_pre_relu/conv', 'mixed4d_pool_reduce_pre_relu', 'mixed4d_pool_reduce', 'mixed4d/concat_dim', 'mixed4d', 'mixed4e_1x1_pre_relu/conv', 'mixed4e_1x1_pre_relu', 'mixed4e_1x1', 'mixed4e_3x3_bottleneck_pre_relu/conv', 'mixed4e_3x3_bottleneck_pre_relu', 'mixed4e_3x3_bottleneck', 'mixed4e_3x3_pre_relu/conv', 'mixed4e_3x3_pre_relu', 'mixed4e_3x3', 'mixed4e_5x5_bottleneck_pre_relu/conv', 'mixed4e_5x5_bottleneck_pre_relu', 'mixed4e_5x5_bottleneck', 'mixed4e_5x5_pre_relu/conv', 'mixed4e_5x5_pre_relu', 'mixed4e_5x5', 'mixed4e_pool', 'mixed4e_pool_reduce_pre_relu/conv', 'mixed4e_pool_reduce', 'mixed4e/concat_dim', 'mixed4e', 'maxpool10', 'mixed5a_1x1_pre_relu/conv', 'mixed5a_1x1_pre_relu', 'mixed5a_1x1', 'mixed5a_3x3_bottleneck_pre_relu/conv', 'mixed5a_3x3_bottleneck_pre_relu', 'mixed5a_3x3_bottleneck', 'mixed5a_3x3_pre_relu/conv', 'mixed5a_3x3_pre_relu', 'mixed5a_3x3', 'mixed5a_5x5_bottleneck_pre_relu/conv', 'mixed5a_5x5_bottleneck_pre_relu', 'mixed5a_5x5_bottleneck', 'mixed5a_5x5_pre_relu/conv', 'mixed5a_5x5_pre_relu', 'mixed5a_5x5', 'mixed5a_pool', 'mixed5a_pool_reduce_pre_relu/conv', 'mixed5a_pool_reduce_pre_relu', 'mixed5a_pool_reduce', 'mixed5a/concat_dim', 'mixed5a', 'mixed5b_1x1_pre_relu/conv', 'mixed5b_1x1_pre_relu', 'mixed5b_1x1', 'mixed5b_3x3_bottleneck_pre_relu/conv', 'mixed5b_3x3_bottleneck_pre_relu', 'mixed5b_3x3_bottleneck', 'mixed5b_3x3_pre_relu/conv', 'mixed5b_3x3_pre_relu', 'mixed5b_3x3', 'mixed5b_5x5_bottleneck_pre_relu/conv', 'mixed5b_5x5_bottleneck_pre_relu', 'mixed5b_5x5_bottleneck', 'mixed5b_5x5_pre_relu/conv', 'mixed5b_5x5_pre_relu', 'mixed5b_5x5', 'mixed5b_pool', 'mixed5b_pool_reduce_pre_relu/conv', 'mixed5b_pool_reduce_pre_relu', 'mixed5b_pool_reduce', 'mixed5b/concat_dim', 'mixed5b', 'avgpool0', 'head0_pool', 'head0_bottleneck_pre_relu/conv', 'head0_bottleneck_pre_relu', 'head0_bottleneck', 'head0_bottleneck/reshape/shape', 'head0_bottleneck/reshape', 'nn0_pre_relu/matmul', 'nn0_pre_relu', 'nn0', 'nn0/reshape/shape', 'nn0/reshape', 'softmax0_pre_activation/matmul', 'softmax0_pre_activation', 'softmax0', 'head1_pool', 'head1_bottleneck_pre_relu/conv', 'head1_bottleneck_pre_relu', 'head1_bottleneck', 'head1_bottleneck/reshape/shape', 'head1_bottleneck/reshape', 'nn1_pre_relu/matmul', 'nn1_pre_relu', 'nn1', 'nn1/reshape/shape', 'nn1/reshape', 'softmax1_pre_activation/matmul', 'softmax1_pre_activation', 'softmax1', 'avgpool0/reshape/shape', 'avgpool0/reshape', 'softmax2_pre_activation/matmul', 'softmax2_pre_activation', 'softmax2']


        # check if folders
        if not os.path.exists(self.settings["output_dir"]):
            os.makedirs(self.settings["output_dir"])

        # private email
        mail_config = self.config_core.get("email", {})
        self.email = mail_config.get("email")
        self.password = mail_config.get("password")
        self.target_mail = mail_config.get("destinatary", self.email)

    def send(self, body):
        title = "Mycroft DeepDream Skill"
        # try private sending
        if yagmail is not None and self.email and self.password:
            with yagmail.SMTP(self.email, self.password) as yag:
                yag.send(self.target_email, title, body)
        else:
            # else use mycroft home
            self.send_email(title, body)

    def speak(self, utterance, expect_response=False, metadata=None):
        """
            Speak a sentence.

                   Args:
                       utterance:          sentence mycroft should speak
                       expect_response:    set to True if Mycroft should expect
                                           a response from the user and start
                                           listening for response.
                       metadata:           Extra data to be transmitted
                                           together with speech
               """
        metadata = metadata or {}
        # registers the skill as being active
        self.enclosure.register(self.name)
        data = {'utterance': utterance,
                'expect_response': expect_response,
                "metadata": metadata}
        message = dig_for_message()
        if message:
            self.emitter.emit(message.reply("speak", data))
        else:
            self.emitter.emit(Message("speak", data))

    def initialize(self):
        # check if model exists, if not download!
        DeepDreamer.maybe_download_and_extract(self.settings["model_folder"])
        self.register_intent_file("dream.intent", self.handle_dream_intent)
        self.emitter.on("dream.request", self.handle_dream_request)

    def handle_dream_intent(self, message):
        search = message.data.get("AboutKeyword")
        data = {}
        filepath = expanduser("~/dream_seed.jpg")
        if search:
            # collect dream entropy
            self.speak("dreaming about " + search)
            pics = self.search_pic(search)
            url = random.choice(pics)
            urllib.urlretrieve(url, filepath)
            data["dream_name"] = search + "_" + time.asctime()
        elif self.settings["use_pexels"]:
            url = random.choice(self.popular_pic_urls())
            req = urllib2.Request(url, None, {
                'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'})
            resp = urllib2.urlopen(req)
            content = resp.read()
            with open(filepath, "wb") as f:
                f.write(content)
        else:
            url = "https://unsplash.it/640/480/?random"
            urllib.urlretrieve(url, filepath)
        data["dream_source"] = filepath
        self.emitter.emit(message.reply("dream.request", data))

    def handle_dream_request(self, message):
        self.speak("dream started")
        channel_value = message.data.get("channel_value")
        seed = message.data.get("dream_source")
        output_name = message.data.get("dream_name")
        layer_name = message.data.get("layer_name")
        iter_value = message.data.get("iter_value", self.settings[
            "iter_value"])
        step_size = message.data.get("step_size", self.settings["step_size"])
        octave_value = message.data.get("octave_value",
                                        self.settings["octave_value"])
        octave_scale_value = message.data.get("octave_scale_value",
                                              self.settings["octave_scale_value"])
        DD = DeepDreamer(self.settings["model"],
                              self.settings["print_model"],
                              self.settings["verbose"],
                              self.settings["tile_size"])

        filepath = DD.dream(output_name, seed, channel_value,
                                 layer_name, iter_value, step_size,
                                 octave_value, octave_scale_value)
        if filepath:
            data = self.client.upload_from_path(filepath)
            metadata = message.data
            metadata["url"] = data["link"]
            self.speak("here is what i dreamed " + data["link"], metadata=metadata)

            mail = "url: " + data["link"] + "\nlayer: " + layer_name + \
                   "\nchannel: " + str(channel_value) + "\niter_num: " + str(iter_value)
            self.send(mail)
            self.emitter.emit(message.reply("dream.response", metadata))
            self.enclosure.mouth_text(data["link"])
        else:
            if layer_name in self.settings["layers"]:
                self.settings["layers"].remove(layer_name)
            self.speak("I could not dream this time")

    ## pic search
    def popular_pic_urls(self, num_pages=1):
        # instantiate PyPexels object
        api_key = self.settings["pexels"]
        urls = []
        try:
            py_pexels = PyPexels(api_key=api_key)
            popular_photos = py_pexels.popular(per_page=10)
            i = 0
            while popular_photos.has_next and i <= num_pages:
                for photo in popular_photos.entries:
                    urls.append(photo.src["original"])
                # no need to specify per_page: will take from original object
                popular_photos = popular_photos.get_next_page()
                i += 1
        except Exception as e:
            LOG.error(e)
        return urls

    def get_soup(self, url, header):
        return BeautifulSoup(
            urllib2.urlopen(urllib2.Request(url, headers=header)),
            'html.parser')

    def search_pic(self, searchkey, dlnum=5):
        query = searchkey  # raw_input("query image")# you can change the query for the image  here
        query = query.split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        }
        soup = self.get_soup(url, header)
        i = 0
        ActualImages = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link = json.loads(a.text)["ou"]
            ActualImages.append(link)
            i += 1
            if i >= dlnum:
                break
        return ActualImages

    def shutdown(self):
        """
            Remove all registered handlers and perform skill shutdown.
        """
        self.emitter.remove("dream.request", self.handle_dream_request)
        super(DreamSkill, self).shutdown()


def create_skill():
    return DreamSkill()


from skimage.io import imread, imsave
import numpy as np
import os
import time
import urllib
import random
from PIL import Image
from os.path import expanduser


class DeepDreamer(object):
    def __init__(self, model_path, print_model=False, verbose=True,
                 tile_size=512):

        self.model_path = model_path
        self.verbose = verbose
        self.print_model = print_model
        self.model_fn = os.path.join(os.path.dirname(os.path.realpath(
            __file__)), model_path)

        self.tile_size = tile_size
        # creating TensorFlow session and loading the model
        self.graph = tf.Graph()
        self.sess = tf.InteractiveSession(graph=self.graph)
        with tf.gfile.FastGFile(self.model_fn, 'rb') as f:
            self.graph_def = tf.GraphDef()
            self.graph_def.ParseFromString(f.read())
        self.t_input = tf.placeholder(np.float32,
                                      name='input')  # define the input tensor
        imagenet_mean = 117.0
        t_preprocessed = tf.expand_dims(self.t_input - imagenet_mean, 0)
        tf.import_graph_def(self.graph_def, {'input': t_preprocessed})

        # Optionally print the inputs and layers of the specified graph.
        if self.print_model:
            LOG.debug(self.graph.get_operations())

        self.last_layer = None
        self.last_grad = None
        self.last_channel = None
        # TODO test all layers, not sure they all can be dreamed on
        self.layers = ['conv2d2_pre_relu/conv', 'conv2d2_pre_relu', 'conv2d2', 'localresponsenorm1', 'maxpool1', 'mixed3a_pool', 'mixed3a', 'mixed3b_3x3_pre_relu/conv', 'mixed3b_3x3_pre_relu', 'mixed3b_3x3', 'mixed3b_5x5_bottleneck_pre_relu/conv', 'mixed3b_5x5_bottleneck_pre_relu', 'mixed3b_5x5_bottleneck', 'mixed3b_5x5_pre_relu/conv', 'mixed3b_5x5_pre_relu', 'mixed3b_5x5', 'mixed3b_pool', 'mixed3b_pool_reduce_pre_relu/conv', 'mixed3b_pool_reduce_pre_relu', 'mixed3b_pool_reduce', 'mixed3b/concat_dim', 'mixed3b', 'maxpool4', 'mixed4a_1x1_pre_relu/conv', 'mixed4a_1x1_pre_relu', 'mixed4a_1x1', 'mixed4a_3x3_bottleneck_pre_relu/conv', 'mixed4a_3x3_bottleneck_pre_relu', 'mixed4a_3x3_bottleneck', 'mixed4a_3x3_pre_relu/conv', 'mixed4a_3x3_pre_relu', 'mixed4a_3x3', 'mixed4a_5x5_bottleneck_pre_relu/conv', 'mixed4a_5x5_bottleneck_pre_relu', 'mixed4a_5x5_bottleneck', 'mixed4a_5x5_pre_relu/conv', 'mixed4a_5x5_pre_relu', 'mixed4a_5x5', 'mixed4a_pool', 'mixed4a_pool_reduce_pre_relu/conv', 'mixed4a_pool_reduce_pre_relu', 'mixed4a_pool_reduce', 'mixed4a/concat_dim', 'mixed4a', 'mixed4b_1x1_pre_relu/conv', 'mixed4b_1x1_pre_relu', 'mixed4b_1x1', 'mixed4b_3x3_bottleneck_pre_relu/conv', 'mixed4b_3x3_bottleneck_pre_relu', 'mixed4b_3x3_bottleneck', 'mixed4b_3x3_pre_relu/conv', 'mixed4b_3x3_pre_relu', 'mixed4b_3x3', 'mixed4b_5x5_bottleneck_pre_relu/conv', 'mixed4b_5x5_bottleneck_pre_relu', 'mixed4b_5x5_bottleneck', 'mixed4b_5x5_pre_relu/conv', 'mixed4b_5x5_pre_relu', 'mixed4b_5x5', 'mixed4b_pool', 'mixed4b_pool_reduce_pre_relu/conv', 'mixed4b_pool_reduce_pre_relu', 'mixed4b_pool_reduce', 'mixed4b/concat_dim', 'mixed4b', 'mixed4c_1x1_pre_relu/conv', 'mixed4c_1x1_pre_relu', 'mixed4c_1x1', 'mixed4c_3x3_bottleneck_pre_relu/conv', 'mixed4c_3x3_bottleneck_pre_relu', 'mixed4c_3x3_bottleneck', 'mixed4c_3x3_pre_relu/conv', 'mixed4c_3x3_pre_relu', 'mixed4c_3x3', 'mixed4c_5x5_bottleneck_pre_relu/conv', 'mixed4c_5x5_bottleneck_pre_relu', 'mixed4c_5x5_bottleneck', 'mixed4c_5x5_pre_relu/conv', 'mixed4c_5x5_pre_relu', 'mixed4c_5x5', 'mixed4c_pool', 'mixed4c_pool_reduce_pre_relu/conv', 'mixed4c_pool_reduce_pre_relu', 'mixed4c_pool_reduce', 'mixed4c/concat_dim', 'mixed4c', 'mixed4d_1x1_pre_relu/conv', 'mixed4d_1x1_pre_relu', 'mixed4d_1x1', 'mixed4d_3x3_bottleneck_pre_relu/conv', 'mixed4d_3x3_bottleneck_pre_relu', 'mixed4d_3x3_bottleneck', 'mixed4d_3x3_pre_relu/conv', 'mixed4d_3x3_pre_relu', 'mixed4d_3x3', 'mixed4d_5x5_bottleneck_pre_relu/conv', 'mixed4d_5x5_bottleneck_pre_relu', 'mixed4d_5x5_bottleneck', 'mixed4d_5x5_pre_relu/conv', 'mixed4d_5x5_pre_relu', 'mixed4d_5x5', 'mixed4d_pool', 'mixed4d_pool_reduce_pre_relu/conv', 'mixed4d_pool_reduce_pre_relu', 'mixed4d_pool_reduce', 'mixed4d/concat_dim', 'mixed4d', 'mixed4e_1x1_pre_relu/conv', 'mixed4e_1x1_pre_relu', 'mixed4e_1x1', 'mixed4e_3x3_bottleneck_pre_relu/conv', 'mixed4e_3x3_bottleneck_pre_relu', 'mixed4e_3x3_bottleneck', 'mixed4e_3x3_pre_relu/conv', 'mixed4e_3x3_pre_relu', 'mixed4e_3x3', 'mixed4e_5x5_bottleneck_pre_relu/conv', 'mixed4e_5x5_bottleneck_pre_relu', 'mixed4e_5x5_bottleneck', 'mixed4e_5x5_pre_relu/conv', 'mixed4e_5x5_pre_relu', 'mixed4e_5x5', 'mixed4e_pool', 'mixed4e_pool_reduce_pre_relu/conv', 'mixed4e_pool_reduce', 'mixed4e/concat_dim', 'mixed4e', 'maxpool10', 'mixed5a_1x1_pre_relu/conv', 'mixed5a_1x1_pre_relu', 'mixed5a_1x1', 'mixed5a_3x3_bottleneck_pre_relu/conv', 'mixed5a_3x3_bottleneck_pre_relu', 'mixed5a_3x3_bottleneck', 'mixed5a_3x3_pre_relu/conv', 'mixed5a_3x3_pre_relu', 'mixed5a_3x3', 'mixed5a_5x5_bottleneck_pre_relu/conv', 'mixed5a_5x5_bottleneck_pre_relu', 'mixed5a_5x5_bottleneck', 'mixed5a_5x5_pre_relu/conv', 'mixed5a_5x5_pre_relu', 'mixed5a_5x5', 'mixed5a_pool', 'mixed5a_pool_reduce_pre_relu/conv', 'mixed5a_pool_reduce_pre_relu', 'mixed5a_pool_reduce', 'mixed5a/concat_dim', 'mixed5a', 'mixed5b_1x1_pre_relu/conv', 'mixed5b_1x1_pre_relu', 'mixed5b_1x1', 'mixed5b_3x3_bottleneck_pre_relu/conv', 'mixed5b_3x3_bottleneck_pre_relu', 'mixed5b_3x3_bottleneck', 'mixed5b_3x3_pre_relu/conv', 'mixed5b_3x3_pre_relu', 'mixed5b_3x3', 'mixed5b_5x5_bottleneck_pre_relu/conv', 'mixed5b_5x5_bottleneck_pre_relu', 'mixed5b_5x5_bottleneck', 'mixed5b_5x5_pre_relu/conv', 'mixed5b_5x5_pre_relu', 'mixed5b_5x5', 'mixed5b_pool', 'mixed5b_pool_reduce_pre_relu/conv', 'mixed5b_pool_reduce_pre_relu', 'mixed5b_pool_reduce', 'mixed5b/concat_dim', 'mixed5b', 'avgpool0', 'head0_pool', 'head0_bottleneck_pre_relu/conv', 'head0_bottleneck_pre_relu', 'head0_bottleneck', 'head0_bottleneck/reshape/shape', 'head0_bottleneck/reshape', 'nn0_pre_relu/matmul', 'nn0_pre_relu', 'nn0', 'nn0/reshape/shape', 'nn0/reshape', 'softmax0_pre_activation/matmul', 'softmax0_pre_activation', 'softmax0', 'head1_pool', 'head1_bottleneck_pre_relu/conv', 'head1_bottleneck_pre_relu', 'head1_bottleneck', 'head1_bottleneck/reshape/shape', 'head1_bottleneck/reshape', 'nn1_pre_relu/matmul', 'nn1_pre_relu', 'nn1', 'nn1/reshape/shape', 'nn1/reshape', 'softmax1_pre_activation/matmul', 'softmax1_pre_activation', 'softmax1', 'avgpool0/reshape/shape', 'avgpool0/reshape', 'softmax2_pre_activation/matmul', 'softmax2_pre_activation', 'softmax2']
        self.resize = self.tffunc(np.float32, np.int32)(self._resize)

    # Helper function that uses TF to resize an image
    @classmethod
    def _resize(cls, img, size):
        img = tf.expand_dims(img, 0)
        return tf.image.resize_bilinear(img, size)[0, :, :, :]

    def T(self, layer):
        '''Helper for getting layer output tensor'''
        return self.graph.get_tensor_by_name("import/%s:0" % layer)

    def tffunc(self, *argtypes):
        '''Helper that transforms TF-graph generating function into a regular one.
        See "resize" function below.
        '''
        placeholders = list(map(tf.placeholder, argtypes))

        def wrap(f):
            out = f(*placeholders)

            def wrapper(*args, **kw):
                return out.eval(dict(zip(placeholders, args)),
                                session=self.sess)

            return wrapper

        return wrap

    def get_random_pic(self, filepath=None):
        filepath = filepath or expanduser("~/dream_seed.jpg")
        url = "https://unsplash.it/640/480/?random"
        urllib.urlretrieve(url, filepath)
        return filepath

    def calc_grad_tiled(self, img, t_grad, tile_size=512):
        '''Compute the value of tensor t_grad over the image in a tiled way.
        Random shifts are applied to the image to blur tile boundaries over
        multiple iterations.'''
        sz = tile_size
        h, w = img.shape[:2]
        sx, sy = np.random.randint(sz, size=2)
        img_shift = np.roll(np.roll(img, sx, 1), sy, 0)
        grad = np.zeros_like(img)
        for y in range(0, max(h - sz // 2, sz), sz):
            for x in range(0, max(w - sz // 2, sz), sz):
                sub = img_shift[y:y + sz, x:x + sz]
                g = self.sess.run(t_grad, {self.t_input: sub})
                grad[y:y + sz, x:x + sz] = g
        return np.roll(np.roll(grad, -sx, 1), -sy, 0)

    def render_deepdream(self, t_grad, img0, iter_n=10, step=1.5, octave_n=4,
                         octave_scale=1.4):
        # split the image into a number of octaves
        img = img0
        octaves = []
        for i in range(octave_n - 1):
            hw = img.shape[:2]
            lo = self.resize(img, np.int32(np.float32(hw) / octave_scale))
            hi = img - self.resize(lo, hw)
            img = lo
            octaves.append(hi)

        # generate details octave by octave
        for octave in range(octave_n):
            if octave > 0:
                hi = octaves[-octave]
                img = self.resize(img, hi.shape[:2]) + hi
            for i in range(iter_n):
                g = self.calc_grad_tiled(img, t_grad, self.tile_size)
                img += g * (step / (np.abs(g).mean() + 1e-7))
                if self.verbose:
                    LOG.info("Iteration Number: %d" % i)
            if self.verbose:
                LOG.info("Octave Number: %d" % octave)

        return Image.fromarray(np.uint8(np.clip(img / 255.0, 0, 1) * 255))

    def render(self, img, layer='mixed4d_3x3_bottleneck_pre_relu',
               channel=139, iter_n=10, step=1.5, octave_n=4,
               octave_scale=1.4):
        if self.last_layer == layer and self.last_channel == channel:
            t_grad = self.last_grad
        else:
            if channel == 4242:
                t_obj = tf.square(self.graph, self.T(layer))
            else:
                t_obj = self.T(layer)[:, :, :, channel]
            t_score = tf.reduce_mean(t_obj)  # defining the optimization objective
            t_grad = tf.gradients(t_score, self.t_input)[
                0]  # behold the power of automatic differentiation!
            self.last_layer = layer
            self.last_grad = t_grad
            self.last_channel = channel
        img0 = np.float32(img)
        return self.render_deepdream(t_grad, img0, iter_n, step, octave_n,
                                octave_scale)

    def dream(self, output_name=None, seed=None, channel_value=None,
              layer_name=None,
              iter_value=10,
              step_size=1.5,
              octave_value=4, octave_scale_value=1.5):

        self.last_layer = None
        self.last_grad = None
        self.last_channel = None
        seed = seed or self.get_random_pic()
        input_img = imread(seed)
        if layer_name not in self.layers:
            layer_name = None
        channel_value = channel_value or random.randint(0,300)
        layer_name = layer_name or random.choice(self.layers)
        LOG.info(layer_name + "_" + str(channel_value))
        try:
            output_img = self.render(input_img, layer=layer_name,
                             channel=channel_value,
                            iter_n=iter_value, step=step_size, octave_n=octave_value,
                            octave_scale=octave_scale_value)
            output_name = output_name or time.asctime().strip() +"_" + layer_name.replace("/", "")+"_"+str(channel_value)
            if ".jpg" not in output_name:
                output_name += ".jpg"
            LOG.debug(output_name)
            imsave(output_name, output_img)
            return output_name
        except Exception as e:
            LOG.error(e)
            return False

    def dream_all(self, seed=None, channel_value=None,
              iter_value=10,
              step_size=1.5,
              octave_value=4, octave_scale_value=1.5):
        layers = list(self.layers)
        random.shuffle(layers)
        for layer_name in layers:
            try:
                self.dream(layer_name=layer_name, seed=seed,
                           channel_value=channel_value,
                            iter_value=iter_value, step_size=step_size,
                           octave_value=octave_value,
                            octave_scale_value=octave_scale_value)
            except Exception as e:
                LOG.error(e)

    @classmethod
    def maybe_download_and_extract(cls, model_folder):
        # """Download and extract model zip file."""
        # wget https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip
        # unzip -d model inception5h.zip
        url = "https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip"
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
        filename = url.split('/')[-1]
        filepath = os.path.join(model_folder, filename)
        if not os.path.exists(filepath):
            LOG.info("Model is not in folder, downloading")
            urllib.urlretrieve(url, filepath)
            statinfo = os.stat(filepath)
            LOG.info('Successfully downloaded '+ filename +
                          "\n"+str(statinfo.st_size) + ' bytes.')
            # unzip
            import zipfile
            zip_ref = zipfile.ZipFile(filepath, 'r')
            zip_ref.extractall(model_folder)
            zip_ref.close()

