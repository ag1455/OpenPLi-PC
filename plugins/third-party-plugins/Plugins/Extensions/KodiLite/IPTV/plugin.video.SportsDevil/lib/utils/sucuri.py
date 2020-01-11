import re

def sucuri_decode(script):
    sucuri_regex = r'''sucuri_cloudproxy_js='',S='([^']+)'''
    match = re.search(sucuri_regex, script)
    if match:
        sucuri = match.group(1).decode('base-64')
        import csv
        csv.register_dialect('s', delimiter='+')
        in_list = [l for l in csv.reader([sucuri.replace('\n','')], dialect='s')][0]
        out_list = []
        for item in in_list:
            substr_regex = r'''.*?['"]?([^'"\.]+)['"]?\.substr\((\d+),\s*(\d+)\)'''
            match = re.search(substr_regex, item)
            if match:
                value, start, length = match.groups()
                out_list.append(value[int(start):int(start)+int(length)])
                continue

            charcode_regex = r'''String\.fromCharCode\(([^\)]+)\)'''
            match = re.search(charcode_regex, item)
            if match:
                value = match.group(1)
                if 'x' in value:
                    out_list.append(chr(int(value,16)))
                    continue
                else:
                    out_list.append(chr(int(value)))
                    continue

            slice_regex = r'''.*?['"]?([^'"\.]+)['"]?\.slice\((\d+),\s*(\d+)\)'''
            match = re.search(slice_regex, item)
            if match:
                value, begin, end = match.groups()
                out_list.append(value[int(begin):int(end)])
                continue

            charat_regex = r'''.*?['"]?([^'"\.]+)['"]?\.charAt\((\d+)\)'''
            match = re.search(charat_regex, item)
            if match:
                value, index = match.groups()
                out_list.append(value[int(index)])
                continue

            out_list.append(item.strip(""" "'"""))

    cookie_regex = r'''(\w{32}).*?(sucuri\w+)='''
    match = re.search(cookie_regex, ''.join(out_list))
    if match:
        value, name = match.groups()
        return name, value
