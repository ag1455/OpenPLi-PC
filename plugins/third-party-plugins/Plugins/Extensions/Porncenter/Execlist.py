
def Execlist(session, index):

                       if "Exodus" in index:
                               from Plugins.Extensions.KodiLite.plugins.ExodusE2.Exodus import Exodus
                               session.open(Exodus)
                       if "KodiliveTv" in index:
                               from Plugins.Extensions.KodiLite.plugins.KodiliveTvE2.KodiveTv import Kodilive1
                               session.open(Kodilive1)
                       if "WorldCam" in index:
                               from Plugins.Extensions.KodiLite.plugins.WorldCamE2.Worldcam import Webcam1
                               session.open(Webcam1)
