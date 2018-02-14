# Adapted from github.com/ProGamerGov
# wget https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip
# unzip -d model inception5h.zip

from skimage.io import imread, imsave
import numpy as np
import os
import tensorflow as tf
import time
import urllib
import random
from PIL import Image
from os.path import expanduser


class DeepDreamer(object):
    def __init__(self, model_path, print_model=True, verbose=True):

        self.model_path = model_path
        self.verbose = verbose
        self.print_model = print_model
        self.model_fn = os.path.join(os.path.dirname(os.path.realpath(
            __file__)), model_path)

        self.tile_size = 512
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
        if not self.print_model:
            print(self.graph.get_operations())

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
                if not self.verbose:
                    print "Iteration Number: %d" % i
            if not self.verbose:
                print "Octave Number: %d" % octave

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
        channel_value = channel_value or random.randint(0,100)
        layer_name = layer_name or random.choice(self.layers)
        print layer_name, channel_value
        output_img = self.render(input_img, layer=layer_name,
                             channel=channel_value,
                            iter_n=iter_value, step=step_size, octave_n=octave_value,
                            octave_scale=octave_scale_value)
        output_name = output_name or time.asctime().strip() +"_" + layer_name.replace("/", "")+"_"+str(channel_value)
        if ".jpg" not in output_name:
            output_name += ".jpg"
        print output_name
        imsave(output_name, output_img)
        return output_img

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
                print e

    def maybe_download_and_extract(self, model_folder):
        # """Download and extract model zip file."""
        # wget https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip
        # unzip -d model inception5h.zip
        url = "https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip"
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
        filename = url.split('/')[-1]
        filepath = os.path.join(model_folder, filename)
        if not os.path.exists(filepath):
            print("Model is not in folder, downloading")
            urllib.urlretrieve(url, filepath)
            statinfo = os.stat(filepath)
            print('Successfully downloaded '+ filename +
                          "\n"+str(statinfo.st_size) + ' bytes.')
            # unzip
            import zipfile
            zip_ref = zipfile.ZipFile(filepath, 'r')
            zip_ref.extractall(model_folder)
            zip_ref.close()


