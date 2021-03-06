# import pydevd
# pydevd.settrace('localhost', port=34765, stdoutToServer=True, stderrToServer=True)

import os
import numpy as np

import geosoft.gxpy.gx as gx
import geosoft.gxapi as gxapi
import geosoft.gxpy.geometry as gxgm
import geosoft.gxpy.view as gxv
import geosoft.gxpy.map as gxmap
import geosoft.gxpy.viewer as gxvwr

###############################################################################################

def sample_map(gxp, mapname='test', rescale=1.0, locate=None):

    with gxmap.GXmap.new(mapname, overwrite=True) as gmap:

        """
        with gxv.GXview(gmap, 'base',area=(0, 0, 200, 150), scale=100.0)as vw:
            vw.xy_rectangle(vw.extent(), pen={"line_color":'B'})
        with gxv.GXview(gmap, 'data', map_location=(5,5), area=(0,0,300,250)) as vw:
            vw.xy_rectangle(vw.extent())
        """

        p2 = gxgm.Point((110, 110)) * rescale
        with gxv.GXview(gmap, "rectangle_test", area=(0, 0, p2.x, p2.y), scale=100.0) as view:
            view.start_group('rect')
            view.xy_rectangle(((0, 0), p2), pen={'line_thick': 1})

            p1 = gxgm.Point((5, 5)) * rescale
            p2 = gxgm.Point((100, 100)) * rescale
            poff = gxgm.Point((10, 5)) * rescale
            view.pen = {'fill_color': gxapi.C_LT_GREEN}
            view.xy_rectangle((p1, p2))

            view.pen = {'line_style': (2, 2.0)}
            view.xy_line((p1 + poff, p2 - poff))

        p2 = gxgm.Point((250, 110)) * rescale
        with gxv.GXview3d(gmap, viewname="poly", area=(0, 0, p2.x, p2.y), scale=100.0) as view:
            view.start_group('stuff')
            view.xy_rectangle(((0, 0), p2), pen={'line_thick': 3, 'line_color':'B'})
            plinelist = [[110, 5],
                         [120, 20],
                         [130, 15],
                         [150, 50],
                         [160, 70],
                         [175, 35],
                         [190, 65],
                         [220, 50],
                         [235, 18.5]]
            pp = gxgm.PPoint.from_list(plinelist) * rescale
            view.pen = {'line_style': (2, 2.0)}
            view.xy_poly_line(pp)
            view.pen = {'line_style': (4, 2.0), 'line_smooth': gxv.SMOOTH_AKIMA}
            view.xy_poly_line(pp)

            ppp = np.array(plinelist)
            pp = gxgm.PPoint(ppp[3:, :]) * rescale
            view.pen = {'line_style': (5, 5.0),
                          'line_smooth': gxv.SMOOTH_CUBIC,
                          'line_color': gxapi.C_RED,
                          'line_thick': 0.25,
                          'fill_color': gxapi.C_LT_BLUE}
            view.xy_poly_line(pp, close=True)

            view.pen = {'fill_color': gxapi.C_LT_GREEN}
            pp = (pp - (100, 0, 0)) / 2 + (100, 0, 0)
            view.xy_poly_line(pp, close=True)
            pp += (0, 25, 0)
            view.pen = {'fill_color': "B"}
            view.xy_poly_line(pp, close=True)

            #TODO - viewer does not properly disply items on the plane if the box_3d is called
            view.box_3d(((20, 10, 30), (80,50,50)), pen={'fill_color': 'R255G100B50'})

        return gmap.filename

def test_mapviewer(gxp):

    sample = sample_map(gxp, mapname = os.path.join(gxp.temp_folder(), 'test_3d'))
    #sample = sample_map(gxp, mapname= 'test_3d')
    gxvwr.map(sample) #TODO where is the 3D view?  It is a tiny dot in the bottom left.  I can't figure out how to locate it.
    gxvwr.v3d(sample)

if __name__ == '__main__':

    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    with gx.GXpy(parent_window=-1, log=print) as gxp:
        test_mapviewer(gxp)
