#!/bin/env python3

import sys
import os

module_path = os.path.abspath("../pysdcv")
if module_path not in sys.path:
	        sys.path.insert(0, module_path)

from  _xdxf import XdxfParser



raw_str = '<k>we</k>\n<co><i>[wi: (полная форма); wı (редуцированная форма)]<c><abr>pers</abr></c> <c><abr>pron</abr></c> (us)</i></co>\n<dtrn><blockquote>1) мы </blockquote>\n<blockquote><blockquote><ex>where shall we go? - куда мы пойдём? </ex></blockquote></blockquote>\n<blockquote><blockquote><ex>we both thank you - мы оба благодарим вас </ex></blockquote></blockquote>\n<blockquote>2) <co><i><c><abr>шутл.</abr></c> </i></co>мы (<co><i><c><abr>употр.</abr></c> вместо 2-го лица с оттенком участия</i></co>) </blockquote>\n<blockquote><blockquote><ex>well, Jane, and how are we this morning? - ну, Джейн, как мы себя чувствуем сегодня? </ex></blockquote></blockquote>\n<blockquote>3) мы (<co><i>при высказываниях от 1-го лица в статье, научных трудах <c><abr>и т. п.</abr></c></i></co>); авторское «мы» </blockquote>\n<blockquote><blockquote><ex>we are of the opinion that ... - по нашему мнению ... </ex></blockquote></blockquote>\n<blockquote>4) мы (<co><i>для обозначения определенного круга лиц, связанных единством цели, профессии <c><abr>и т. п.</abr></c></i></co>) </blockquote>\n<blockquote><blockquote><ex>we lawyers ... - мы, адвокаты ... </ex></blockquote></blockquote>\n<blockquote>5) мы (<co><i>для обозначения неопределённого круга лиц в обобщённых суждениях</i></co>) </blockquote>\n<blockquote><blockquote><ex>as we are often apt to think - как мы часто бываем склонны считать </ex></blockquote></blockquote>\n<blockquote><blockquote><ex>we in the United States believe that ... - в Соединённых Штатах считают, что ... </ex></blockquote></blockquote>\n<blockquote>6) мы (<co><i>употребляется монархами в значении</i></co> «я») </blockquote>\n</dtrn><blockquote></blockquote>'

parser = XdxfParser()
parser.parse(raw_str)
print(parser.tostring())


