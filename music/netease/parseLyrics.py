from typing import List
import json
import chinese_converter


class TimeCode:
    def __init__(self, start_time: int, duration: int):
        self.start:int = start_time
        self.duration:int = duration
    
    def __str__(self) -> str:
        return f"({self.start},{self.duration})"

class LyricsNode:
    def __init__(self, time: TimeCode, text: str):
        self.text = text
        self.time = time
    
    def __str__(self) -> str:
        return f"{self.time} {self.text}"

class LyricsLine:
    def __init__(self, time: TimeCode, lyrics: str, trans: bool):
        self.time = time
        self.nodes: List[LyricsNode] = []
        self.trans = trans
        self.parse(lyrics)
    
    def __str__(self) -> str:
        nodes_str = ""
        for n in self.nodes:
            nodes_str = nodes_str + str(n) + " "
        return f"{self.time} {nodes_str}"

    def parse(self, lyrics: str):
        lyrics = lyrics.split("(")
        for l in lyrics:
            if l == "":
                continue

            time, text = l.split(")")
            try:
                start, end, color = map(int, time.split(","))
                # FIXME: color is not used, not sure what it is for
                # 猜是對唱的顏色
                if self.trans:
                    self.nodes.append(LyricsNode(TimeCode(start, end), chinese_converter.to_traditional(text)))
                else:
                    self.nodes.append(LyricsNode(TimeCode(start, end), text))
            except ValueError:
                # If the line does not have a timecode, then it is a lyric line
                # that is not timed
                # FIXME: But this time i don't wanna to implement it
                # self.nodes.append(LyricsNode(TimeCode(0, 0), l))
                pass

class LyricsByWord:
    def __init__(self, lyr: str, translate: bool = False):
        self.artist:dict = {}
        self.lyrics:List[LyricsLine] = []
        self.translate = translate
        self.parse(lyr.split('\n'))
    
    def parse(self, lyrics: List[str]):
        for line in lyrics:
            # If the line starts with '{' and ends with '}', then it is a json string
            # witch contains the artist information
            try:
                if line.startswith(r'{'):
                    continue
                    self.parseArtist(line)
                elif line.startswith(r'['):
                    self.parseLyrics(line)
            except Exception as e:
                print(f"Error: START ERR {line} END ERR")
                print(e)
                pass

    def parseArtist(self, line):
        try:
            json_data = json.loads(line.replace('\\', '').strip())
        except json.decoder.JSONDecodeError as e:
            print(e)
            print(f"JSON Error: START ERR {line[0:50]} {line[-50:]}END ERR")
            return

        key = ""
        value = ""
        for c in json_data['c']:
            if 'tx' in c:
                # print(c['tx'], end=' ')
                if key == "":
                    key = c['tx'].replace(':', '')
                else:
                    value = value + c['tx']
        
        self.artist[key] = value

    def parseLyrics(self, line):
        end_of_bracket = line.find(']')

        start, end = map (int, line[1: end_of_bracket].split(','))

        lyrics_line = LyricsLine( TimeCode(start,end), line[end_of_bracket + 1 : ] , trans=self.translate)
        self.lyrics.append(lyrics_line)

    def pprint(self):
        print(self.artist)
        for l in self.lyrics:
            print(l)
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True)


    
def main():
    a = None
    with open('lyr.txt', 'r', encoding="UTF-8") as f:
        lyrics = f.read()
        
        # print(lyrics)
        a = LyricsByWord(lyrics, translate=True)
    a.pprint()

    with open('lyrics_tw.json', 'w', encoding="UTF-8") as f:
        f.write(a.to_json())
    

if __name__ == '__main__':
    main()

