import traceback
import re

class hivelogic:
    def contains_hivelogic(self,data):
        return ur'while(x=eval(x));' in data
        
    def unpack_hivelogic(self,data):
        try:
            in_data=data
            sPattern = ur"""(var\sx.*?while\(x=eval\(x\)\);)"""
            hive_data=re.compile(sPattern,re.DOTALL).findall(in_data)
            for block in hive_data:
                unpack_val=self.decode_hivelogic(block.decode('unicode_escape'))
                in_data=in_data.replace(block,unpack_val[6:-17].decode('unicode_escape'))
            return in_data
        except:
            traceback.print_exc(file=sys.stdout)
            return data
        
    def decode_hivelogic(self,data):
        escape_again=False
        #reverse block
        if ur"""x.length,l=ol;while(x.charCodeAt""" in data \
        or ur"""x.length;for(i=l-1;i>=0;i--)""" in data:
            r = re.compile(r"""var x=("fun.*?")\s+;""",re.DOTALL)
            match1 = r.findall(data)
            if match1:
                r = re.compile(r'"(.*)"\s*')
                gs = r.findall(match1[0])
                if gs:
                    h2 = ''.join(gs)
                    r2 = re.compile(r"""f\(\\*"(.*?nuf)""")
                    g2 = r2.findall(h2)
                    if g2:
                        s = g2[0].decode('unicode_escape')
                        result = '"'+s[::-1]+'"'
                        data = data.replace(match1[0], result)
                        escape_again=True
        #swap block
        if ur"""x.charAt(i+1);try{o+=x.charAt(i)""" in data:
            r = re.compile(r"""var x=("fun.*?")\s+;""",re.DOTALL)
            match1 = r.findall(data)
            if match1:
                r = re.compile(r'(?!\\")"(.*)(?!\\")"')
                gs = r.findall(match1[0])
                if gs:
                    h2 = ''.join(gs)
                    r2 = re.compile(r"""f\(\\*"(.*?(?:fu|\"f))\)""")
                    g2 = r2.findall(h2)
                    if g2:
                        s = g2[0].decode('unicode_escape')
                        result = '"'+''.join([ s[x:x+2][::-1] for x in range(0, len(s), 2) ])+'"'
                        data = data.replace(match1[0], result)
                        escape_again=True
        #XOR block
        if ur"""y%=127;o+=St""" in data:
            r = re.compile(r"""var x=("fun.*?")\s+;""",re.DOTALL)
            match1 = r.findall(data)
            if match1:
                r = re.compile(r'"(.*)"\s*')
                gs = r.findall(match1[0])
                if gs:
                    h2 = ''.join(gs)
                    r2 = re.compile(r"""f\(\\*"(.*)",(\d+)""")
                    g2 = r2.findall(h2)
                    if g2:
                        bump=False
                        if ('i=='+g2[0][1]) in h2:
                            bump = True
                        inc=False
                        if ('i<'+g2[0][1]) in h2:
                            inc = True
                        mult=False
                        if ('i>('+g2[0][1]+'+y)') in h2:
                            mult = True
                        
                        result=""
                        y=int(g2[0][1])
                        s=g2[0][0].decode('unicode_escape')
                        for i,c in enumerate(s):
                            if bump:
                                if (i == int(g2[0][1])):
                                    y = y +i
                            if inc:
                                if (i < int(g2[0][1])):
                                    y = y + 1
                                    
                            if mult:
                                if (i > (int(g2[0][1])+y)):
                                    y = y * 2
                            y%=127
                            result+=chr(ord(c)^y)
                            y=y+1

                        data = data.replace(match1[0], '"'+result+'"')
                        escape_again=True
                        
                        
        if escape_again:
            data = self.decode_hivelogic(data)
        return data
