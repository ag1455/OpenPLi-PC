from Renderer import Renderer
from enigma import eLabel
from Components.VariableText import VariableText
from enigma import eServiceCenter, iServiceInformation, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable

class TuxNextTP(VariableText, Renderer):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)

	GUI_WIDGET = eLabel

	def connect(self, source):
		Renderer.connect(self, source)
		self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		if self.instance:
			if what[0] == self.CHANGED_CLEAR:
				self.text = "Transporder info not found !"
			else:
				serviceref = self.source.service
				info = eServiceCenter.getInstance().info(serviceref)
				if info and serviceref:
					sname = info.getInfoObject(serviceref, iServiceInformation.sTransponderData)
					fq = pol = fec = sr = orb = ""
					try:
						if sname.has_key("frequency"):
							tmp = int(sname["frequency"])/1000
							fq = str(tmp) + "  "
						if sname.has_key("polarization"):
							try:
								pol = {
									eDVBFrontendParametersSatellite.Polarisation_Horizontal : "H  ",
									eDVBFrontendParametersSatellite.Polarisation_Vertical : "V  ",
									eDVBFrontendParametersSatellite.Polarisation_CircularLeft : "CL  ",
									eDVBFrontendParametersSatellite.Polarisation_CircularRight : "CR  "}[sname["polarization"]]
							except:
								pol = "N/A  "
						if sname.has_key("fec_inner"):
							try:
								fec = {
									eDVBFrontendParametersSatellite.FEC_None : _("None  "),
									eDVBFrontendParametersSatellite.FEC_Auto : _("Auto  "),
									eDVBFrontendParametersSatellite.FEC_1_2 : "1/2  ",
									eDVBFrontendParametersSatellite.FEC_2_3 : "2/3  ",
									eDVBFrontendParametersSatellite.FEC_3_4 : "3/4  ",
									eDVBFrontendParametersSatellite.FEC_5_6 : "5/6  ",
									eDVBFrontendParametersSatellite.FEC_7_8 : "7/8  ",
									eDVBFrontendParametersSatellite.FEC_3_5 : "3/5  ",
									eDVBFrontendParametersSatellite.FEC_4_5 : "4/5  ",
									eDVBFrontendParametersSatellite.FEC_8_9 : "8/9  ",
									eDVBFrontendParametersSatellite.FEC_9_10 : "9/10  "}[sname["fec_inner"]]
							except:
								fec = "N/A  "
							if fec == "N/A  ":
								try:
									fec = {
										eDVBFrontendParametersCable.FEC_None : _("None  "),
										eDVBFrontendParametersCable.FEC_Auto : _("Auto  "),
										eDVBFrontendParametersCable.FEC_1_2 : "1/2  ",
										eDVBFrontendParametersCable.FEC_2_3 : "2/3  ",
										eDVBFrontendParametersCable.FEC_3_4 : "3/4  ",
										eDVBFrontendParametersCable.FEC_5_6 : "5/6  ",
										eDVBFrontendParametersCable.FEC_7_8 : "7/8  ",
										eDVBFrontendParametersCable.FEC_8_9 : "8/9  ",}[sname["fec_inner"]]
								except:
									fec = "N/A  "
						if sname.has_key("symbol_rate"):
							tmp = int(sname["symbol_rate"])/1000
							sr = str(tmp) + "  "
						if sname.has_key("orbital_position"):
							try:
								orb = {
											3592:'Thor 7, 5, 6, Intelsat 10-02 (0.8W)',3570:'ABS 3A (3.0W)',3560:'Amos 7, 3 (4.0W)',3550:'Eutelsat 5 West A (5.0W)',3530:'Nilesat 201, Eutelsat 7 West A (7.0W)',
											3520:'Atlantic Bird (8.0W)',3475:'Atlantic Bird (12.5W)',3460:'Express (14.0W)',3450:'Telstar (15.0W)',3520:'Eutelsat 8 West B (8.0W)',3490:'Express AM44 (11.0W)',
											3475:'Eutelsat 12 West B, WGS 3 (12.5W)',3460:'Express AM8 (14.0W)',3450:'Telstar 12 Vantage (15.0W)',3420:'Intelsat 37E (18.0W)',3400:'NSS 7, Al Yah 3 (20.0W)',
											3380:'SES 4 (22.0W)',3355:'Intelsat 905, Alcomsat 1 (24.5W)',3325:'Intelsat 907 (27.5W)',3305:'Intelsat 901 (29.5W)',3300:'Hispasat 30W-4, 30W-5, 30W-6 (30.0W)',
											3285:'Intelsat 25, 903 (31.5W)',3265:'Hylas 1, 4 (33.5W)',3255:'Intelsat 35E (34.5W)',3240:'Hispasat 36W-1 (36.0W)',3225:'NSS 10, Telstar 11N (37.5W)',
											3195:'SES 6 (40.5E)',3169:'Intelsat 11, Sky Brasil 1 (43.1W)',3150:'Intelsat 14, EchoStar 23 (45.0W)',3125:'NSS 806, SES 14 (47.5W)',3100:'Intelsat 29E (50.0W)',
											3070:'Intelsat 23 (53.0W)',3045:'Intelsat 34 (55.5W)',3020:'Intelsat 21 (58.0W)',2990:'Amazonas 2,3,5 (61.0W)',2986:'EchoStar 18 (61.4W)',2985:'EchoStar 16 (61.5W)',
											2970:'Telstar 14R (63.0W)',2950:'Star One C1, Eutelsat 65 West A (65.0W)',2930:'SES 10 (67.0w)',2901:'Viasat 2 (69.9W)',2900:'Star One C2,C4 (70.0W)',
											2882:'Arsat 1 (71.8W)',2875:'Nimiq 5 (72.7W)',2861:'Hispasat 74W-1 (73.9)',2850:'Star One C3 (75.0W)',2838:'Intelsat 16 (76.2)',2830:'QuetzSat 1 (77.0W)',
											2820:'Simon Bolivar (78.0W)',2812:'Sky Mexico 1 (78.8W)',2790:'Arsat 2 (81.0W)',2780:'Nimiq 4 (82.0W)',2770:'AMC 6 (83.0W)',2760:'Star One D1 (84.0W)',
											2785:'XM 3 (81.5W)',2775:'Sirius XM 5 (82.5W)',2725:'SES 2, TKSat 1 (87.5W)',2710:'Galaxy 28 (89.0W)',2690:'Galaxy 17, Nimiq 6 (91.0W)',3592:'Thor/Intelsat (0.8W)',
											2669:'Galaxy 25 (93.1W)',2670:'Galaxy 3C, Intelsat 31, Intelsat 30 (95.0W)',2630:'Galaxy 19 (97.0W)',2629:'EchoStar 19 (97.1W)',
											2608:'Galaxy 16, Spaceway 2 & DirecTV 11,14 (99.2W)',2592:'DirecTV 15 (100.8W)',2590:'DirecTV 8, SES 1, DirecTV 4S (101.0W)',2570:'DirecTV 10/12, SES 3 (103.0W)',
											2550:'AMC 15, EchoStar 105/SES 11 (105.W)',2529:'EchoStar 17 (107.1W)',2527:'Anik F1R, Anik G1 (107.3W)',2500:'DirecTV 5, EchoStar 10, EchoStar 11 (110.0W)',
											2489:'Anik F2 (111.1W)',2470:'Eutelsat 113 West A (113.0W)',2452:'Mexsat Bicentenario (114.8W)',2451:'Eutelsat 115 West B (114.9W)',2450:'XM 4 (115.0W)',
											2440:'Sirius FM 6 (116.0W)',2430:'Eutelsat 117 West A,B (117.0W)',2410:'Anik F3, DirecTV 7S, EchoStar 14 (119.0W)',2391:'EchoStar 9/Galaxy 23 (121.0W)',
											2430:'Galaxy 18 (123.0W)',2350:'AMC 21, Galaxy 14 (125.0W)',2330:'Galaxy 13/Horizons 1 (127.0W)',2320:'Spaceway 1 (128.0W)',2310:'Ciel 2, SES 15 (129.0W)',
											2290:'AMC 11 (131.0W)',2270:'Eutelsat 133 West A, Galaxy 15 (133.0W)',2250:'AMC 10 (135.0W)',2210:'AMC 8, 18 (139.0W)',1100:'BSat 1A,2A (110.0E)',
											1101:'N-Sat 110 (110.0E)',1131:'KoreaSat 5 (113.0E)',1400:'Express AM3 (140.0E)',1006:'AsiaSat 2 (100.5E)',1030:'Express A2 (103.0E)',1056:'Asiasat 3S (105.5E)',
											1082:'NSS 11 (108.2E)',881:'ST1 (88.0E)',900:'Yamal 201 (90.0E)',950:'Insat 4B (95.0E)',951:'NSS 6 (95.0E)',965:'Express AM33 (96.5E)',
											765:'Telestar (76.5E)',785:'ThaiCom 5 (78.5E)',800:'Express AM2/MD1 (80.0E)',830:'Insat 4A (83.0E)',852:'Intelsat 15 (85.2E)',610:'ABS 4 (61.0E)',
											750:'ABS 1/1A/Eutelsat W75 (75.0E)',720:'Intelsat (72.0E)',705:'Eutelsat W5 (70.5E)',685:'Intelsat (68.5E)',620:'Intelsat 902 (62.0E)',610:'ABS 4 (61.0E)',
											600:'Intelsat 33E (60.0E)',593:'Eutelsat 59A (59.3E)',585:'KazSat 3 (58.5E)',570:'NSS 12 (57.0E)',560:'Express AT1 (56.0E)',550:'Sat 8, G-Sat 16, Yamal 402 (55.0E)',
											530:'Express AM6 (53.0E)',525:'Al Yah 1 (52.5E)',520:'TurkmenAlem/Monacosat (52.5E)',515:'Belintersat 1 (51.5E)',505:'NSS 5 (50.5E)',500:'Turksat 4B (50.0E)',
											490:'Yamal 202 (49.0E)',480:'G-Sat 19, Afghansat 1 (48.0E)',475:'Intelsat 10 (47.5E)',460:'AzerSpace 1/Africasat 1A (46.0E)',
											450:'Intelsat 904, Intelsat 12, Galaxy 11Intelsat (45.0E)',425:'NigComSat 1R (42.5E)',420:'Turksat 3A, Turksat 4A (42.0E)',400:'Express AM7 (40.0E)',
											390:'Hellas Sat 2, Hellas Sat 3 (39.0E)',380:'Paksat 1R (38.0E)',361:'Eutelsat 36B (36.1E)',360:'Eutelsat AMU1 (36.0E)',330:'Eutelsat 33E, Intelsat 28 (33.0E)',
											315:'Astra 5B (31.5E)',310:'Hylas 2 (31.0E)',305:'Arabsat 5A (30.5E)',282:'Astra 2E, 2F, 2G (28.5E)',260:'Badr 4, 5, 6, 7 (26.0E)',255:'Es"hail 1 (25.5E)',
											235:'SES 16/GovSat 1, Astra 3B (23.5E)',215:'Astra 3B (21.5E)',200:'Arabsat 5C (20.0E)',192:'Astra 1KR, 1L, 1M, 1N (19.2E)',160:'Eutelsat 16A (16.0E)',
											130:'Hotbird 13B, 13C, 13E (13.0E)',100:'Eutelsat 10A (10.0E)',90:'Eutelsat Ka-Sat 9A, 9B (9.0E)',70:'Eutelsat 7A, 7B (7.0E)',49:'SES 5, Astra 4A (4.9E)',
											30:'Eutelsat 3B, Rascom QAF 1R (3.0E)',19:'BulgariaSat 1 (1.9E)',
											}[sname["orbital_position"]]
							except:
								orb = "Unknown"
					except:
						pass
					self.text = fq + pol + fec + sr + orb



