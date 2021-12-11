firstrun = 0
playlist_exists = False

current_selection = 0
current_playlist = []
bouquets_exist = False

haslive = False
hasvod = False
hasseries = False

finished = False

livecategories = []
vodcategories = []
seriescategories = []

livestreams = []
vodstreams = []
seriesstreams = []

getm3ustreams = []

categories = []
selectedcategories = []
ignoredcategories = []

haslzma = False

bouquet_id = 0
name = ''
old_name = ''
live_type = '4097'
vod_type = '4097'
selected_live_categories = []
selected_vod_categories = []
selected_series_categories = []

ignore_live_categories = []
ignore_vod_categories = []
ignore_series_categories = []

live_update = '---'
vod_update = '---'
series_update = '---'
xmltv_address = ''
vod_order = 'original'


epg_rytec_uk = False
epg_swap_names = False
epg_force_rytec_uk = False

live = True
vod = False
series = False

has_epg_importer = False
epg_provider = False
if has_epg_importer:
    epg_provider = True

prefix_name = True

livebuffer = "0"
vodbuffer = "0"

# catchup globals

currentref = None
currentrefstring = ""
name = ""
archive = []
dates = []
username = ""
password = ""
domain = ""
refstreamnum = ""

rytecnames = []

fixepg = False
catchupshift = 0
