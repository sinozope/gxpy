
import geosoft
import numpy as np
import geosoft.gxapi as gxapi
from . import utility as gxu

__version__ = geosoft.__version__


def _t(s):
    return geosoft.gxpy.system.translate(s)


class VVException(Exception):
    '''
    Exceptions from this module.

    .. versionadded:: 9.1
    '''
    pass


class GXvv():
    '''
    VV class wrapper.

    :param array:   array-like, None to create an empty VV
    :param dtype:   numpy data type.  For unicode strings 'U#', where # is a string length. If not specified
                    the type is taken from first element in array, of if no array the default is 'float'.
    :param fid:     fid tuple (start,increment), default (0.0,1.0)
    :constructor vv_np:  create from a numpy array

    .. versionchanged:: 9.2
        allow construction directly from arrays

    .. versionadded:: 9.1
    '''

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __init__(self, array=None, dtype=None, fid=(0.0, 1.0)):

        if (array is not None) and (type(array) is not np.ndarray):
            if dtype is None:
                dtype = np.dtype(type(array[0]))
            array = np.array(array, dtype=dtype)
            dtype = array.dtype # if strings, type will change to the longest string

        if dtype is None:
            dtype = array.dtype

        self._gxtype = gxu.gx_dtype(dtype)
        self._dtype = gxu.dtype_gx(self._gxtype)
        self._vv = gxapi.GXVV.create_ext(self._gxtype, 0)
        self._vv.set_fid_start(fid[0])
        self._vv.set_fid_incr(fid[1])
        self._sr = None

        if array is not None:
            if self._gxtype >= 0:
                self._vv.set_data_np(0, array.flatten())
            else:
                # strings
                array = array.flatten()
                ne = array.shape[0]
                for i in range(ne):
                    self._vv.set_string(i, str(array[i]))

    @property
    def fid(self):
        '''
        :return:    fid tuple (start,increment)

        .. versionadded:: 9.1
        '''
        start = self._vv.get_fid_start()
        incr = self._vv.get_fid_incr()
        return (start, incr)

    @fid.setter
    def fid(self, fid):
        '''
        Set the fiducial of the vv.

        :param fid: (fidStart,fidIncrement)

        .. versionadded:: 9.2
        '''
        self._vv.set_fid_start(fid[0])
        self._vv.set_fid_incr(fid[1])

    @property
    def length(self):
        '''
        :return:    number of elements in the VV

        .. versionadded:: 9.1
        '''
        return self._vv.length()

    @property
    def gxtype(self):
        '''
        :return: GX data type

        .. versionadded:: 9.1
        '''
        return self._gxtype

    @property
    def dtype(self):
        '''
        :return: numpy data type

        .. versionadded:: 9.1
        '''
        return self._dtype

    def reFid(self, fid, length):
        '''
        Resample VV to a new fiducial and length

        :param fid: (start,incr)
        :param length: length

        .. versionadded:: 9.1
        '''
        self._vv.re_fid(fid[0], fid[1], length)

    def get_np(self, dtype=None, start=0, n=None):
        '''
        Return vv data in a numpy array

        :param start:   index of first value, must be >=0
        :param n:       number of values wanted
        :param dtype:   numpy data type wanted
        :returns:       (data, (fid_start, fid_incr))

        .. versionadded:: 9.1
        '''

        if dtype is None:
            dtype = self._dtype
        else:
            dtype = np.dtype(dtype)

        if n is None:
            n = self.length - start
        else:
            n = min((self.length - start), n)

        if (n <= 0) or (start < 0):
            raise VVException(_t('Cannot get (start,n) ({},{}) from vv of length {}').format(start, n, self.length))

        # strings wanted
        if dtype.type is np.str_:
            if self._sr is None:
                self._sr = gxapi.str_ref()
            npd = np.empty((n,), dtype=dtype)
            for i in range(start, start + n):
                self._vv.get_string(i, self._sr)
                npd[i - start] = self._sr.value

        # numeric wanted
        else:

            # strings to numeric
            if self._gxtype < 0:
                if np.issubclass_(dtype.type, np.integer):
                    vvd = gxapi.GXVV.create_ext(gxapi.GS_LONG, n)
                else:
                    vvd = gxapi.GXVV.create_ext(gxapi.GS_DOUBLE, n)

                vvd.copy(self._vv)  # this will do the conversion
                npd = vvd.get_data_np(start, n, dtype)

            # numeric to numeric
            else:
                npd = self._vv.get_data_np(start, n, dtype)

        fid = self.fid
        start = fid[0] + start * fid[1]
        return npd, (start, fid[1])

    def set_np(self, npdata, fid=(0.0, 1.0)):
        """
        Set vv data from a numpy array

        :param npdata:  numpy data array
        :param fid:     fid tuple (start,increment), default (0.0,1.0)

        .. versionadded:: 9.1
        """

        npdata = npdata.flatten()

        # numerical data
        if self._gxtype >= 0:
            self._vv.set_data_np(0, npdata)

        # strings
        else:
            ne = npdata.shape[0]
            for i in range(ne):
                self._vv.set_string(i, str(npdata[i]))

        self._vv.set_len(npdata.shape[0])
        self.fid = fid

    def get_float(self, index):
        """ return float value """
        return self._vv.get_double(index)

    def get_int(self, index):
        """ return integer value """
        return self._vv.get_int(index)

    def get_string(self, index):
        """ return string value """
        s = gxapi.str_ref()
        self._vv.get_string(index, s)
        return s.value

    def list(self):
        """
        Return the content of a VV as a Python list.  Only use this when you know
        a VV is short.  This function is not efficient.

        :return: list containing the content of a VV.

        .. versionadded:: 9.2
        """

        if gxu.is_string(self._gxtype):
            getter = self.get_string
        elif gxu.is_float(self._gxtype):
            getter = self.get_float
        else:
            getter = self.get_int

        return [getter(i) for i in range(self.length)]
