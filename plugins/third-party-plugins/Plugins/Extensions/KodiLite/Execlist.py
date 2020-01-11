
def Execlist(session, index):

                       if "Movietime" in index:
                               from plugins.MovietimeE2.Movietime import Movietime
                               session.open(Movietime)
                       if "KodiliveTv" in index:
                               from plugins.KodiliveTvE2.KodiveTv import Kodilive1
                               session.open(Kodilive1)
                       if "WorldCam" in index:
                               from plugins.WorldCamE2.Worldcam import Webcam1
                               session.open(Webcam1)
