# Adapted from https://github.com/ProGamerGov/Protobuf-Dreamer

import time
from mycroft.skills.core import MycroftSkill, Message, dig_for_message
from imgurpython import ImgurClient
import urllib2
import random
import json
from bs4 import BeautifulSoup
import urllib

import scipy.ndimage as spi
from skimage.io import imsave
import numpy as np
import os
from os.path import join, exists, expanduser
import tensorflow as tf
from PIL import Image
try:
    import yagmail
except ImportError:
    yagmail = None

__author__ = 'jarbas'


class DreamSkill(MycroftSkill):
    def __init__(self):
        super(DreamSkill, self).__init__()
        self.reload_skill = False

        # free keys for the people
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

        if "channel_value" not in self.settings:
            self.settings["channel_value"] = 139
        if "iter_value" not in self.settings:
            self.settings["iter_value"] = 10
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
        if "model_fn" not in self.settings:
            self.settings["model_fn"] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), self.settings["model"])
        if "print_model" not in self.settings:
            self.settings["print_model"] = True
        if "verbose" not in self.settings:
            self.settings["verbose"] = True
        self.last_layer = None
        self.last_grad = None
        self.last_channel = None
        self.graph = None
        self.sess = None
        self.t_input = None
        if "iter_num" not in self.settings:
            self.settings["iter_num"] = 40  # dreaming iterations
        if "output_dir" not in self.settings:
            self.settings["output_dir"] = expanduser("~/dreams")

        # check if folders
        if not os.path.exists(self.settings["output_dir"]):
            os.makedirs(self.settings["output_dir"])
        # check if model exists, if not download!
        self.maybe_download_and_extract()
        # helper resize function using TF
        self.resize = tffunc(self.sess, np.float32, np.int32)(resize)

        # private email
        if yagmail is not None:
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

    def maybe_download_and_extract(self):
        # """Download and extract model zip file."""
        # TODO get out of skill runtime, put in install
        ## wget https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip
        # unzip -d model inception5h.zip
        url = "https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip"
        if not exists(self.settings["model_folder"]):
            os.makedirs(self.settings["model_folder"])
        filename = url.split('/')[-1]
        filepath = os.path.join(self.settings["model_folder"], filename)
        if not os.path.exists(self.settings["model"]):
            self.log.info("Model is not in folder, downloading")
            urllib.urlretrieve(url, filepath)
            statinfo = os.stat(filepath)
            self.log.info('Successfully downloaded', filename,
                          statinfo.st_size, 'bytes.')
            # unzip
            import zipfile
            zip_ref = zipfile.ZipFile(filepath, 'r')
            zip_ref.extractall(self.settings["model_folder"])
            zip_ref.close()

    def initialize(self):
        self.register_intent_file("dream.intent", self.handle_dream_intent)
        self.emitter.on("dream.request", self.handle_dream_request)

    def handle_dream_intent(self, message):
        search = message.data.get("AboutKeyword")
        data = {}
        if search:
            # collect dream entropy
            self.speak("dreaming about " + search)
            pics = self.search_pic(search)
            url = random.choice(pics)
            data["dream_name"] = search + "_" + time.asctime()
        else:
            url = "https://unsplash.it/640/480/?random"

        filepath = expanduser("~/dream_seed.jpg")
        urllib.urlretrieve(url, filepath)
        data["dream_source"] = filepath
        self.emitter.emit(message.reply("dream.request", data))

    def handle_dream_request(self, message):
        # TODO dreaming queue, no multiple dreams at once,
        # TODO get all params from message
        self.log.info("Dream request received")
        source = message.data.get("dream_source", message.data.get(
            "PicturePath"))
        guide = message.data.get("dream_guide", message.data.get(
            "PicturePath"))
        name = message.data.get("dream_name")
        iter = message.data.get("iter_num", )
        categorie = message.data.get("categorie")
        channel = int(message.data.get("channel", 888))
        layer = None
        if categorie:
            # TODO fuzzy match
            if categorie in self.layer_nicknames.keys():
                layer, channel = self.layer_nicknames[categorie]
        result = None
        start = time.time()
        if channel == 888:
            channel = random.randint(1, 500)
        if source is None:
            self.log.error("No dream seed")
        # elif guide is not None:
        #    result = self.guided_dream(source, guide, name, iter)
        else:
            try:
                result = self.dream(source, name, iter, layer, channel)
            except Exception as e:
                self.log.error(str(e))
        elapsed_time = time.time() - start
        layer = random.choice(self.layers)
        message.data = {"url": None, "file": None, "elapsed_time":
            elapsed_time, "layer": layer, "channel": channel,
                        "iter_num": iter}
        if result is not None:
            data = self.client.upload_from_path(result)
            link = data["link"]
            self.speak("Here is what i dreamed",
                       metadata={"url": link, "file": result,
                                 "elapsed_time": elapsed_time})
            message.data = {"url": link, "file": result, "elapsed_time":
                elapsed_time, "layer": layer, "channel": channel,
                            "iter_num": iter}
            mail = "url: " + link +"\nelapsed: " + str(elapsed_time) \
                                  +"\nlayer: " + str(
                layer) +"\nchannel: "+ str(channel) +"\niter_num: " + str(
                iter)
            self.send(mail)

        else:
            self.speak("I could not dream this time")


    #### dreaming functions
    def dream(self, imagepah, name=None, iter=25, layer=None, channel=None):
        self.speak(
            "please wait while the dream is processed, this can take up to 15 minutes")
        if layer is None:
            layer = random.choice(self.layers)

        dreampic = spi.imread(imagepah, mode="RGB")
        if dreampic is None:
            self.log.error("Could not load seed dream pic " + imagepah)
            self.speak("I can't dream without a seed.. retry later")
            return
        else:
            self.log.info("Loaded dream seed " + imagepah)
        # creating TensorFlow session and loading the model
        self.graph = tf.Graph()
        self.sess = tf.InteractiveSession(graph=self.graph)
        # update resize function using TF session
        self.resize = tffunc(self.sess, np.float32, np.int32)(resize)
        with tf.gfile.FastGFile(self.settings["model_fn"], 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
        self.t_input = tf.placeholder(np.float32,
                                      name='input')  # define the input tensor
        imagenet_mean = 117.0
        t_preprocessed = tf.expand_dims(self.t_input - imagenet_mean, 0)
        tf.import_graph_def(graph_def, {'input': t_preprocessed})

        # Optionally print the inputs and layers of the specified graph.
        if not self.settings["print_model"]:
            self.log.debug(self.graph.get_operations())
        # TODO get all paramsfrom message
        image = None
        if not channel:
            channel = self.settings["channel_value"]

        while image is None:
            try:
                self.speak(
                    "Using layer: " + layer + " and channel: " + str(channel),
                    metadata={"channel": channel, "layer": layer})
                image = self.render(dreampic, layer=layer, channel=channel,
                                    iter_n=iter, step=self.settings[
                        "step_size"],
                                    octave_n=self.settings["octave_value"],
                                    octave_scale=self.settings[
                                        "octave_scale_value"])
            except Exception as e:
                self.speak("dreaming with this layer failed, retrying")
                self.log.error(str(e))
                # bad layer, cant dream # TODO make list accurate
                self.layers.remove(layer)
                layer = random.choice(self.layers)

        # write the output image to file
        if name is None:
            name = time.asctime().replace(" ", "_") + ".jpg"
        if ".jpg" not in name:
            name += ".jpg"
        outpath = join(self.settings["outputdir"], name)
        self.log.info("Saving dream: " + outpath)
        imsave(outpath, image)
        return outpath

    def guided_dream(self, sourcepath, guidepath, name=None, iter=25):
        self.log.error("Guided dream not implemented")
        return None

    ## dream internals
    def T(self, layer):
        '''Helper for getting layer output tensor'''
        return self.graph.get_tensor_by_name("import/%s:0" % layer)

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
                # g = calc_grad_tiled(img, t_grad)
                g = self.calc_grad_tiled(img, t_grad, self.settings[
                    "tile_size"])
                img += g * (step / (np.abs(g).mean() + 1e-7))
                if self.settings["verbose"]:
                    self.log.info("Iteration Number: %d" % i)
            if self.settings["verbose"]:
                self.log.info("Octave Number: %d" % octave)

        return Image.fromarray(np.uint8(np.clip(img / 255.0, 0, 1) * 255))

    def render(self, img, layer='mixed4d_3x3_bottleneck_pre_relu',
               channel=139, iter_n=10, step=1.5, octave_n=4,
               octave_scale=1.4):
        if self.last_layer == layer and self.last_channel == channel:
            t_grad = self.last_grad
        else:
            if channel == 4242:
                t_obj = tf.square(self.T(layer))
            else:
                t_obj = self.T(layer)[:, :, :, channel]
            t_score = tf.reduce_mean(
                t_obj)  # defining the optimization objective
            t_grad = tf.gradients(t_score, self.t_input)[
                0]  # behold the power of automatic differentiation!
            self.last_layer = layer
            self.last_grad = t_grad
            self.last_channel = channel
        img0 = np.float32(img)
        return self.render_deepdream(t_grad, img0, iter_n, step, octave_n,
                                     octave_scale)

    ## pic search
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


def tffunc(session, *argtypes):
    '''Helper that transforms TF-graph generating function into a regular one.
    See "resize" function below.
    '''
    placeholders = list(map(tf.placeholder, argtypes))

    def wrap(f):
        out = f(*placeholders)

        def wrapper(*args, **kw):
            return out.eval(dict(zip(placeholders, args)), session=session)

        return wrapper

    return wrap


# Helper function that uses TF to resize an image
def resize(img, size):
    img = tf.expand_dims(img, 0)
    return tf.image.resize_bilinear(img, size)[0, :, :, :]
