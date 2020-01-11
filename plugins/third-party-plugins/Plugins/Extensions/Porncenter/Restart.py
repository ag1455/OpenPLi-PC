##############Test 1###############
import os
from Screens.Standby import TryQuitMainloop

def Restart(session):
      session.open(TryQuitMainloop, 3)  

