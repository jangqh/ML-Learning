import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from tensorflow_practice.CNN.LeNet5 import LeNet5_infernece
from tensorflow.contrib.layers import l2_regularizer
import numpy as np

BATCH_SIZE = 100
LEARNING_RATE_BASE = 0.01
LEARNING_RATE_DECAY = 0.99
REGULARIZATION_RATE = 0.0001
TRAINING_STEPS = 6000
MOVING_AVERAGE_DECAY = 0.99


def train(mnist):
    """

    :param mnist:
    :return:
    """
    # 定义输出为4维矩阵的placeholder
    x = tf.placeholder(tf.float32, [
        BATCH_SIZE,
        LeNet5_infernece.IMAGE_SIZE,
        LeNet5_infernece.IMAGE_SIZE,
        LeNet5_infernece.NUM_CHANNELS],
                       name='x-input')
    y_true = tf.placeholder(tf.float32, [None, LeNet5_infernece.OUTPUT_NODE], name='y-input')

    regularizer = l2_regularizer(REGULARIZATION_RATE)
    y = LeNet5_infernece.inference(x, False, regularizer)
    global_step = tf.Variable(0, trainable=False)

    # 定义损失函数、学习率、滑动平均操作以及训练过程。
    variable_averages = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)
    variables_averages_op = variable_averages.apply(tf.trainable_variables())
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y, labels=tf.argmax(y_true, 1))
    cross_entropy_mean = tf.reduce_mean(cross_entropy)
    # 定义 loss
    loss = cross_entropy_mean + tf.add_n(tf.get_collection('losses'))
    learning_rate = tf.train.exponential_decay(
        LEARNING_RATE_BASE,
        global_step,
        mnist.train.num_examples / BATCH_SIZE, LEARNING_RATE_DECAY,
        staircase=True)

    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step=global_step)
    with tf.control_dependencies([train_step, variables_averages_op]):
        train_op = tf.no_op(name='train')

    # 初始化TensorFlow持久化类。
    saver = tf.train.Saver()
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        for i in range(TRAINING_STEPS):
            xs, ys = mnist.train.next_batch(BATCH_SIZE)

            reshaped_xs = np.reshape(xs, (
                BATCH_SIZE,
                LeNet5_infernece.IMAGE_SIZE,
                LeNet5_infernece.IMAGE_SIZE,
                LeNet5_infernece.NUM_CHANNELS))
            _, loss_value, step = sess.run([train_op, loss, global_step], feed_dict={x: reshaped_xs, y_true: ys})

            if i % 100 == 0:
                print("After %d training step(s), loss on training batch is %g." % (step, loss_value))


def main(argv=None):
    # input_data.read_data_sets() 从网络上自动下载 MNIST 数据集
    mnist = input_data.read_data_sets("d:/in/MNIST_data", one_hot=True)
    train(mnist)


if __name__ == '__main__':
    main()
"""
After 1 training step(s), loss on training batch is 4.84312.
After 1001 training step(s), loss on training batch is 0.727191.
"""
