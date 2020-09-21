#!/usr/bin/env python3
# coding=utf-8

"""    
    @File: Patent-Crack.py
    @Desc: 
    @Author: lv junling
    @Date Created: 2018/10/22
"""
import os
import pickle
import numpy as np
from PIL import Image


class PatentCrack(object):
    def __init__(self, pkl_fn=None):
        if pkl_fn is None:
            print('[error]Must specify the pickle filename.')
            return
        self.pkl_fn = pkl_fn
        if os.path.exists(pkl_fn):
            self._load_pkl()
        else:
            self.gen_pkl_fn()

    def gen_pkl_fn(self):
        imgs_path = u'data'
        chi_1_imgs = ['1.jpeg', '2.jpeg', '3.jpeg', '4.jpeg', '5.jpeg',
                      '6.jpeg', '7.jpeg', '8.jpeg', '9.jpeg']

        op_imgs    = ['1.jpeg', '7.jpeg']

        chi_3_imgs = ['100.jpeg', '101.jpeg', '102.jpeg', '103.jpeg', '104.jpeg', '105.jpeg',
                      '106.jpeg', '107.jpeg', '108.jpeg', '109.jpeg']

        chi_1_arr = np.zeros([10, 20, 11], dtype=np.bool)
        for idx, img_fn in enumerate(chi_1_imgs):
            c1, _, _, _ = self._get_split_img(os.path.join(imgs_path, img_fn))
            chi_1_arr[idx+1] = c1

        op_arr = np.zeros([3, 20, 12], dtype=np.bool)
        for idx, img_fn in enumerate(op_imgs):
            _, _, op, _ = self._get_split_img(os.path.join(imgs_path, img_fn))
            op_arr[idx] = op

        chi_3_arr = np.zeros([10, 20, 10], dtype=np.bool)
        for idx, img_fn in enumerate(chi_3_imgs):
            _, _, _, c3 = self._get_split_img(os.path.join(imgs_path, img_fn))
            chi_3_arr[idx] = c3

        fout = open(self.pkl_fn, 'wb')
        data = {'chi_1': chi_1_arr, 'op': op_arr, 'chi_3': chi_3_arr}
        pickle.dump(data, fout)
        fout.close()

        self._load_pkl()

    def _load_pkl(self):
        data = pickle.load(open(self.pkl_fn, 'rb'))
        self.chi_1_arr = data['chi_1']
        self.op_arr = data['op']
        self.chi_3_arr = data['chi_3']

    @staticmethod
    def _get_split_img(img_fn):
        img_arr = np.array(Image.open(img_fn).convert('L'))
        img_arr[img_arr < 156] = 1
        img_arr[img_arr >= 156] = 0
        img_arr = img_arr.astype(np.bool)
        chi_1_arr = img_arr[:,  3:14]
        op_arr    = img_arr[:, 22:34]
        chi_3_arr = img_arr[:, 41:51]
        return chi_1_arr,  op_arr, chi_3_arr

    @staticmethod
    def _cal_result(num1, num3,op):
        if op == 0:
            return num1 + num3
        elif op == 1:
            return num1 - num3
        elif op == 2:
            return num1 * num3
        else:
            return int(num1 / num3)

    def feed(self, img_fn):
        chi_1_arr,  op_arr, chi_3_arr = self._get_split_img(img_fn)
        chi_1_arr = np.tile(chi_1_arr[np.newaxis, :], [10, 1, 1])
        op_arr = np.tile(op_arr[np.newaxis, :], [3, 1, 1])
        chi_1_sum = np.sum(
            np.sum(np.bitwise_and(chi_1_arr, self.chi_1_arr), axis=2), axis=1)
        op_sum = np.sum(
            np.sum(np.bitwise_and(op_arr, self.op_arr), axis=2), axis=1)
        op_sum[1] += 1   # 区分减号和加号
        chi_3_sum = np.sum(
            np.sum(np.bitwise_and(chi_3_arr, self.chi_3_arr), axis=2), axis=1)
        num1 = chi_1_sum.argmax()
        op = op_sum.argmax()
        num3 = chi_3_sum.argmax()
        result = self._cal_result(num1, num3, op)
        return result
        