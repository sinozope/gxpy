import numpy as np
import os
import unittest

import geosoft
import geosoft.gxapi as gxapi
import geosoft.gxpy.gx as gx
import geosoft.gxpy.system as gsys
import geosoft.gxpy.vv as gxvv
import geosoft.gxpy.utility as gxu

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gxp = gx.GXpy(log=print)

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def start(cls,test):
        cls.gxp.log("*** {} > {}".format(os.path.split(__file__)[1], test))

    def test_vv(self):
        self.start(gsys.func_name())

        self.assertEqual(gxvv.__version__, geosoft.__version__)

        with gxvv.GXvv(dtype=np.float) as vv:
            self.assertEqual(vv.fid, (0.0, 1.0))

        fid = (10.1,0.99)
        with gxvv.GXvv(dtype=np.float,fid=fid) as vv:
            self.assertEqual(vv.fid, fid)
            self.assertEqual(vv.length, 0)

            fid = (-45,7)
            vv.fid = fid
            self.assertEqual(vv.fid, fid)

            vv.reFid((-40,8),4)
            self.assertEqual(vv.fid, (-40,8))
            self.assertEqual(vv.length, 4)

        with gxvv.GXvv([1, 2, 3, 4, 5, 6]) as vv:
            self.assertEqual(vv.fid, (0.0, 1.0))
            self.assertEqual(vv.length, 6)
            self.assertEqual(vv.dtype, np.int32)
            self.assertEqual(vv.gxtype, gxu.gx_dtype(np.int32))

        with gxvv.GXvv([1, 2, 3, 4, 5, 6], dtype=np.int64) as vv:
            self.assertEqual(vv.fid, (0.0, 1.0))
            self.assertEqual(vv.length, 6)
            self.assertEqual(vv.dtype, np.int64)
            self.assertEqual(vv.gxtype, gxu.gx_dtype(np.int64))

    def test_np(self):
        self.start(gsys.func_name())

        fid = (99,0.1)
        npdata = np.array([1,2,3,4,5,6,7])
        with gxvv.GXvv(npdata, fid=fid) as vv:
            self.assertEqual(vv.fid, fid)
            self.assertEqual(vv.length, len(npdata))

            np2 = vv.get_np(vv.dtype)
            self.assertEqual(np2[0].shape,(7,))
            np2,fid2 = vv.get_np(vv.dtype,start=1)
            self.assertEqual(fid2,(99.1,.1))
            self.assertEqual(np2.shape,(6,))
            self.assertEqual(vv.get_np(vv.dtype,start=6)[0].shape,(1,))
            self.assertRaises(gxvv.VVException, vv.get_np, vv.dtype, start=7)

            np3,fid3 = vv.get_np(np.int)
            self.assertEqual(fid3,fid)
            self.assertEqual(np3[0], 1)
            self.assertEqual(np3[6], 7)

            self.assertEqual(vv.get_float(6), 7.0)
            self.assertEqual(vv.get_int(6), 7)
            self.assertEqual(vv.get_string(6), "7")

        npdata = np.array([1,2,3,4,5,6,7],dtype=np.int)
        with gxvv.GXvv(npdata, fid=fid) as vv:
            np3= vv.get_np(dtype=np.int64)
            self.assertEqual(np3[0][0],1)
            self.assertEqual(np3[0][6],7)
            np3 = vv.get_np(np.float)
            self.assertEqual(np3[0][0],1.)
            self.assertEqual(np3[0][6],7.)

            vv.set_np(np.array([4,5,6,7], dtype=np.int))
            np3,fid = vv.get_np(dtype=np.int64)
            self.assertEqual(len(np3), 4)
            self.assertEqual(np3[0], 4)
            self.assertEqual(np3[3], 7)
            np3,fid = vv.get_np(np.float)
            self.assertEqual(np3[0], 4.)
            self.assertEqual(np3[3], 7.)

        npdata = np.array(['4', '5', '6', '7'])
        vv3= gxvv.GXvv(npdata, fid=fid)
        np3, fid = vv3.get_np()
        self.assertEqual(len(np3), 4)
        self.assertEqual(np3[0], '4')
        self.assertEqual(np3[3], '7')
        np3, fid = vv.get_np(np.float)
        self.assertEqual(np3[0], 4.)
        self.assertEqual(np3[3], 7.)

        npdata = np.array(['4000', '50', '60', '-70'])
        vv3 = gxvv.GXvv(npdata, fid=fid)
        np3, fid = vv3.get_np()
        self.assertEqual(len(np3), 4)
        self.assertEqual(np3[0], '4000')
        self.assertEqual(np3[3], '-70')
        np3, fid = vv3.get_np(np.float)
        self.assertEqual(np3[0], 4000.)
        self.assertEqual(np3[3], -70.)

    def test_strings(self):
        self.start(gsys.func_name())

        fidvv = (99,0.1)
        npdata = np.array(["name", "maki", "neil", "rider"])
        with  gxvv.GXvv(npdata, fid=fidvv) as vv:
            self.assertEqual(vv.fid,fidvv)
            self.assertEqual(vv.length,len(npdata))
            self.assertEqual(vv.gxtype,-5)
            self.assertTrue(vv.dtype.type is np.str_)
            self.assertEqual(str(vv.dtype),'<U5')

            npd,fid = vv.get_np(vv.dtype)
            self.assertEqual(npd[0],"name")
            self.assertEqual(npd[1],"maki")
            self.assertEqual(npd[2],"neil")
            self.assertEqual(npd[3],"rider")

            npd,fid = vv.get_np(vv.dtype,start=2,n=2)
            self.assertEqual(npd[0],"neil")
            self.assertEqual(npd[1],"rider")
            self.assertEqual(fid,(99.2,0.1))

        npdata = np.array(["1","2","3","4000","*"])
        with gxvv.GXvv(npdata, fid=fid) as vv:
            npd,fid = vv.get_np(np.float)
            self.assertEqual(npd[0],1.0)
            self.assertEqual(npd[1],2.0)
            self.assertEqual(npd[2],3.0)
            self.assertEqual(npd[3],4000.0)
            self.assertEqual(npd[4],gxapi.rDUMMY)

        npdata = np.array(["1","2","3","4000","40000","*"])
        with gxvv.GXvv(npdata, fid=fid) as vv:
            npd,fid = vv.get_np(np.int)
            self.assertEqual(npd[0],1)
            self.assertEqual(npd[1],2)
            self.assertEqual(npd[2],3)
            self.assertEqual(npd[3],4000)
            self.assertEqual(npd[4],40000)
            self.assertEqual(npd[5],gxapi.iDUMMY)

        npdata = np.array(["1","2","3","4000","40000","*"])
        with gxvv.GXvv(npdata, fid=fid) as vv:
            npd,fid = vv.get_np(np.int,start=2, n=3)
            self.assertEqual(npd[0],3)
            self.assertEqual(npd[1],4000)
            self.assertEqual(npd[2],40000)


        npdata = np.array(["make_it_big enough"])
        with gxvv.GXvv(npdata, fid=fid) as vv:
            npd, fid = vv.get_np(np.int, start=0, n=1)
            self.assertEqual(npd[0], gxapi.iDUMMY)

            npdata = np.array([1.,2.,-30.,-87.66662])
            vv.set_np(npdata)
            npd, fid = vv.get_np(start=0, n=4)
            self.assertEqual(npd[0], "1.0")
            self.assertEqual(npd[2], "-30.0")
            self.assertEqual(npd[3], "-87.66662")

    def test_list(self):
        self.start(gsys.func_name())

        l = [1, 2, 3]
        with gxvv.GXvv(l) as vv:
            self.assertEqual(vv.list(), l)
        l = [1., 2., 3.]
        with gxvv.GXvv(l) as vv:
            self.assertEqual(vv.list(), l)
        l = ["a", "b", "abc"]
        with gxvv.GXvv(l) as vv:
            self.assertEqual(vv.list(), l)

    def test_string(self):
        self.start(gsys.func_name())

        l = [1, 2, 3]
        with gxvv.GXvv(l, dtype='U45') as vv:
            self.assertEqual(vv.list(), ['1', '2', '3'])

        l = [1, 2, "abcdefg"]
        with gxvv.GXvv(l, dtype='U4') as vv:
            self.assertEqual(vv.list(), ['1', '2', 'abcd'])


##############################################################################################
if __name__ == '__main__':

    unittest.main()