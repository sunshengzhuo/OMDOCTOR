"""
生成扩展药材数据 — 从25味扩展到200+味
运行: cd backend && python -m app.data.generate_herbs
输出: app/data/herbs_extended.json
"""
import json
from pathlib import Path

HERBS_DATA = [
  # ── 解表药 ──
  {"name": "麻黄", "aliases": ["龙沙", "卑相"], "category": "解表药", "nature": "温", "flavor": "辛、微苦", "meridian_tropism": "归肺、膀胱经", "efficacy": "发汗解表，宣肺平喘，利水消肿", "dosage_min": 2, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "桂枝", "aliases": ["柳桂", "嫩桂枝"], "category": "解表药", "nature": "温", "flavor": "辛、甘", "meridian_tropism": "归心、肺、膀胱经", "efficacy": "发汗解肌，温通经脉，助阳化气，平冲降逆", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "紫苏", "aliases": ["苏叶", "赤苏"], "category": "解表药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肺、脾经", "efficacy": "解表散寒，行气和胃，解鱼蟹毒", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "荆芥", "aliases": ["假苏", "姜芥"], "category": "解表药", "nature": "微温", "flavor": "辛", "meridian_tropism": "归肺、肝经", "efficacy": "解表散风，透疹消疮，炒炭止血", "dosage_min": 5, "dosage_max": 10, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "防风", "aliases": ["屏风", "铜芸"], "category": "解表药", "nature": "微温", "flavor": "辛、甘", "meridian_tropism": "归膀胱、肝、脾经", "efficacy": "祛风解表，胜湿止痛，止痉", "dosage_min": 5, "dosage_max": 10, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "羌活", "aliases": ["羌青", "护羌使者"], "category": "解表药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归膀胱、肾经", "efficacy": "解表散寒，祛风胜湿，止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "白芷", "aliases": ["芳香", "泽芬"], "category": "解表药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肺、胃、大肠经", "efficacy": "解表散寒，祛风止痛，通鼻窍，燥湿止带，消肿排脓", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "细辛", "aliases": ["小辛", "少辛"], "category": "解表药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肺、肾经", "efficacy": "解表散寒，祛风止痛，通窍，温肺化饮", "dosage_min": 1, "dosage_max": 3, "toxicity": "有小毒", "pregnancy_contraindicated": False},
  {"name": "藁本", "aliases": ["藁茇"], "category": "解表药", "nature": "温", "flavor": "辛", "meridian_tropism": "归膀胱经", "efficacy": "祛风散寒，除湿止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "苍耳子", "aliases": ["苍耳", "虱麻头"], "category": "解表药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归肺经", "efficacy": "散风寒，通鼻窍，祛风湿", "dosage_min": 3, "dosage_max": 9, "toxicity": "有小毒", "pregnancy_contraindicated": False},
  {"name": "辛夷", "aliases": ["木笔花", "望春花"], "category": "解表药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肺、胃经", "efficacy": "散风寒，通鼻窍", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "薄荷", "aliases": ["银丹草", "苏薄荷"], "category": "解表药", "nature": "凉", "flavor": "辛", "meridian_tropism": "归肺、肝经", "efficacy": "疏散风热，清利头目，利咽透疹，疏肝行气", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "牛蒡子", "aliases": ["恶实", "鼠粘子"], "category": "解表药", "nature": "寒", "flavor": "辛、苦", "meridian_tropism": "归肺、胃经", "efficacy": "疏散风热，宣肺透疹，解毒利咽", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "蝉蜕", "aliases": ["蝉退", "蝉衣"], "category": "解表药", "nature": "寒", "flavor": "甘", "meridian_tropism": "归肺、肝经", "efficacy": "疏散风热，利咽透疹，明目退翳，解痉", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "桑叶", "aliases": ["冬桑叶", "霜桑叶"], "category": "解表药", "nature": "寒", "flavor": "甘、苦", "meridian_tropism": "归肺、肝经", "efficacy": "疏散风热，清肺润燥，平肝明目", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "菊花", "aliases": ["甘菊", "杭菊"], "category": "解表药", "nature": "微寒", "flavor": "甘、苦", "meridian_tropism": "归肺、肝经", "efficacy": "疏散风热，平肝明目，清热解毒", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "蔓荆子", "aliases": ["荆子", "万荆子"], "category": "解表药", "nature": "微寒", "flavor": "辛、苦", "meridian_tropism": "归膀胱、肝、胃经", "efficacy": "疏散风热，清利头目", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "柴胡", "aliases": ["地熏", "茹草"], "category": "解表药", "nature": "微寒", "flavor": "辛、苦", "meridian_tropism": "归肝、胆、肺经", "efficacy": "和解表里，疏肝升阳", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "升麻", "aliases": ["周升麻", "鸡骨升麻"], "category": "解表药", "nature": "微寒", "flavor": "辛、微甘", "meridian_tropism": "归肺、脾、胃、大肠经", "efficacy": "发表透疹，清热解毒，升举阳气", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "葛根", "aliases": ["干葛", "甘葛"], "category": "解表药", "nature": "凉", "flavor": "甘、辛", "meridian_tropism": "归脾、胃经", "efficacy": "解肌退热，生津止渴，透疹，升阳止泻，通经活络，解酒毒", "dosage_min": 10, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "淡豆豉", "aliases": ["豆豉", "香豉"], "category": "解表药", "nature": "凉", "flavor": "苦、辛", "meridian_tropism": "归肺、胃经", "efficacy": "解表除烦，宣发郁热", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "浮萍", "aliases": ["水萍", "田萍"], "category": "解表药", "nature": "寒", "flavor": "辛", "meridian_tropism": "归肺、膀胱经", "efficacy": "宣散风热，透疹利水", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 清热药 ──
  {"name": "石膏", "aliases": ["白虎", "细理石"], "category": "清热药", "nature": "大寒", "flavor": "甘、辛", "meridian_tropism": "归肺、胃经", "efficacy": "清热泻火，除烦止渴", "dosage_min": 15, "dosage_max": 60, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "知母", "aliases": ["蚔母", "连母"], "category": "清热药", "nature": "寒", "flavor": "苦、甘", "meridian_tropism": "归肺、胃、肾经", "efficacy": "清热泻火，滋阴润燥", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "栀子", "aliases": ["山栀", "黄栀子"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归心、肺、三焦经", "efficacy": "泻火除烦，清热利湿，凉血解毒", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "黄芩", "aliases": ["腐肠", "经芩"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肺、胆、脾、大肠、小肠经", "efficacy": "清热燥湿，泻火解毒，止血安胎", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "黄连", "aliases": ["王连", "支连"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归心、脾、胃、肝、胆、大肠经", "efficacy": "清热燥湿，泻火解毒", "dosage_min": 2, "dosage_max": 5, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "黄柏", "aliases": ["檗木", "檗皮"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肾、膀胱经", "efficacy": "清热燥湿，泻火除蒸，解毒疗疮", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "龙胆", "aliases": ["龙胆草", "胆草"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肝、胆经", "efficacy": "清热燥湿，泻肝胆火", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "苦参", "aliases": ["苦骨", "地槐"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归心、肝、胃、大肠、膀胱经", "efficacy": "清热燥湿，杀虫利尿", "dosage_min": 3, "dosage_max": 9, "toxicity": "有小毒", "pregnancy_contraindicated": True},
  {"name": "金银花", "aliases": ["忍冬花", "双花"], "category": "清热药", "nature": "寒", "flavor": "甘", "meridian_tropism": "归肺、心、胃经", "efficacy": "清热解毒，疏散风热", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "连翘", "aliases": ["旱连子", "大翘"], "category": "清热药", "nature": "微寒", "flavor": "苦", "meridian_tropism": "归肺、心、小肠经", "efficacy": "清热解毒，消肿散结，疏散风热", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "蒲公英", "aliases": ["黄花地丁", "婆婆丁"], "category": "清热药", "nature": "寒", "flavor": "苦、甘", "meridian_tropism": "归肝、胃经", "efficacy": "清热解毒，消肿散结，利湿通淋", "dosage_min": 10, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "紫花地丁", "aliases": ["地丁", "苦地丁"], "category": "清热药", "nature": "寒", "flavor": "苦、辛", "meridian_tropism": "归心、肝经", "efficacy": "清热解毒，凉血消肿", "dosage_min": 10, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "大青叶", "aliases": ["蓝叶", "靛青叶"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归心、胃经", "efficacy": "清热解毒，凉血消斑", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "板蓝根", "aliases": ["靛青根", "蓝靛根"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归心、胃经", "efficacy": "清热解毒，凉血利咽", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "青黛", "aliases": ["靛花", "蓝露"], "category": "清热药", "nature": "寒", "flavor": "咸", "meridian_tropism": "归肝经", "efficacy": "清热解毒，凉血消斑，泻火定惊", "dosage_min": 1.5, "dosage_max": 3, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "射干", "aliases": ["乌扇", "鬼扇"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肺经", "efficacy": "清热解毒，消痰利咽", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "山豆根", "aliases": ["广豆根", "苦豆根"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肺、胃经", "efficacy": "清热解毒，利咽消肿", "dosage_min": 3, "dosage_max": 6, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "白头翁", "aliases": ["野丈人", "胡王使者"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归胃、大肠经", "efficacy": "清热解毒，凉血止痢", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "马齿苋", "aliases": ["马齿草", "五行草"], "category": "清热药", "nature": "寒", "flavor": "酸", "meridian_tropism": "归肝、大肠经", "efficacy": "清热解毒，凉血止血，止痢", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "鸦胆子", "aliases": ["老鸦胆", "苦榛子"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归大肠、肝经", "efficacy": "清热解毒，截疟止痢，腐蚀赘疣", "dosage_min": 0.5, "dosage_max": 2, "toxicity": "有小毒", "pregnancy_contraindicated": True},
  {"name": "生地黄", "aliases": ["生地", "干地黄"], "category": "清热药", "nature": "寒", "flavor": "甘、苦", "meridian_tropism": "归心、肝、肾经", "efficacy": "清热凉血，养阴生津", "dosage_min": 10, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "玄参", "aliases": ["元参", "黑参"], "category": "清热药", "nature": "微寒", "flavor": "甘、苦、咸", "meridian_tropism": "归肺、胃、肾经", "efficacy": "清热凉血，滋阴降火，解毒散结", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "牡丹皮", "aliases": ["丹皮", "粉丹皮"], "category": "清热药", "nature": "微寒", "flavor": "苦、辛", "meridian_tropism": "归心、肝、肾经", "efficacy": "清热凉血，活血化瘀", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "赤芍", "aliases": ["赤芍药", "红芍药"], "category": "清热药", "nature": "微寒", "flavor": "苦", "meridian_tropism": "归肝经", "efficacy": "清热凉血，散瘀止痛", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "紫草", "aliases": ["紫丹", "地血"], "category": "清热药", "nature": "寒", "flavor": "甘、咸", "meridian_tropism": "归心、肝经", "efficacy": "清热凉血，活血解毒，透疹消斑", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "水牛角", "aliases": ["牛角"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归心、肝经", "efficacy": "清热凉血，解毒定惊", "dosage_min": 15, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "青蒿", "aliases": ["草蒿", "香蒿"], "category": "清热药", "nature": "寒", "flavor": "苦、辛", "meridian_tropism": "归肝、胆经", "efficacy": "清透虚热，凉血除蒸，解暑截疟", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "地骨皮", "aliases": ["枸杞根皮"], "category": "清热药", "nature": "寒", "flavor": "甘", "meridian_tropism": "归肺、肝、肾经", "efficacy": "凉血除蒸，清肺降火", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "银柴胡", "aliases": ["银胡", "牛肚根"], "category": "清热药", "nature": "微寒", "flavor": "甘", "meridian_tropism": "归肝、胃经", "efficacy": "清虚热，除疳热", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "胡黄连", "aliases": ["假黄连"], "category": "清热药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肝、胃、大肠经", "efficacy": "退虚热，除疳热，清湿热", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 泻下药 ──
  {"name": "大黄", "aliases": ["将军", "锦纹", "川军"], "category": "泻下药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归脾、胃、大肠、肝、心包经", "efficacy": "泻下攻积，清热泻火，凉血解毒，逐瘀通经", "dosage_min": 3, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "芒硝", "aliases": ["朴硝", "皮硝"], "category": "泻下药", "nature": "寒", "flavor": "咸、苦", "meridian_tropism": "归胃、大肠经", "efficacy": "泻下通便，润燥软坚，清火消肿", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "番泻叶", "aliases": ["泻叶"], "category": "泻下药", "nature": "寒", "flavor": "甘、苦", "meridian_tropism": "归大肠经", "efficacy": "泻热行滞，通便利水", "dosage_min": 2, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "火麻仁", "aliases": ["麻子仁", "大麻仁"], "category": "泻下药", "nature": "平", "flavor": "甘", "meridian_tropism": "归脾、胃、大肠经", "efficacy": "润肠通便", "dosage_min": 10, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "郁李仁", "aliases": ["李仁", "郁子"], "category": "泻下药", "nature": "平", "flavor": "辛、苦、甘", "meridian_tropism": "归脾、大肠、小肠经", "efficacy": "润肠通便，下气利水", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "甘遂", "aliases": ["甘泽", "陵蒿"], "category": "泻下药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肺、肾、大肠经", "efficacy": "泻水逐饮，消肿散结", "dosage_min": 0.5, "dosage_max": 1.5, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "大戟", "aliases": ["京大戟", "红芽大戟"], "category": "泻下药", "nature": "寒", "flavor": "苦、辛", "meridian_tropism": "归肺、脾、肾经", "efficacy": "泻水逐饮，消肿散结", "dosage_min": 1.5, "dosage_max": 3, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "芫花", "aliases": ["赤芫", "杜芫"], "category": "泻下药", "nature": "温", "flavor": "苦、辛", "meridian_tropism": "归肺、脾、肾经", "efficacy": "泻水逐饮，祛痰止咳，杀虫疗疮", "dosage_min": 1.5, "dosage_max": 3, "toxicity": "有毒", "pregnancy_contraindicated": True},

  # ── 祛风湿药 ──
  {"name": "独活", "aliases": ["独摇草", "长生草"], "category": "祛风湿药", "nature": "微温", "flavor": "辛、苦", "meridian_tropism": "归肾、膀胱经", "efficacy": "祛风除湿，通痹止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "威灵仙", "aliases": ["铁脚威灵仙", "灵仙"], "category": "祛风湿药", "nature": "温", "flavor": "辛、咸", "meridian_tropism": "归膀胱经", "efficacy": "祛风湿，通经络，消骨鲠", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "川乌", "aliases": ["川乌头"], "category": "祛风湿药", "nature": "热", "flavor": "辛、苦", "meridian_tropism": "归心、肝、肾、脾经", "efficacy": "祛风除湿，温经止痛", "dosage_min": 1.5, "dosage_max": 3, "toxicity": "有大毒", "pregnancy_contraindicated": True},
  {"name": "草乌", "aliases": ["草乌头"], "category": "祛风湿药", "nature": "热", "flavor": "辛、苦", "meridian_tropism": "归心、肝、肾、脾经", "efficacy": "祛风除湿，温经止痛", "dosage_min": 1.5, "dosage_max": 3, "toxicity": "有大毒", "pregnancy_contraindicated": True},
  {"name": "蕲蛇", "aliases": ["白花蛇", "百步蛇"], "category": "祛风湿药", "nature": "温", "flavor": "甘、咸", "meridian_tropism": "归肝经", "efficacy": "祛风通络，止痉", "dosage_min": 3, "dosage_max": 9, "toxicity": "有毒", "pregnancy_contraindicated": False},
  {"name": "木瓜", "aliases": ["贴梗海棠", "铁脚梨"], "category": "祛风湿药", "nature": "温", "flavor": "酸", "meridian_tropism": "归肝、脾经", "efficacy": "舒筋活络，和胃化湿", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "秦艽", "aliases": ["秦纠", "大艽"], "category": "祛风湿药", "nature": "平", "flavor": "辛、苦", "meridian_tropism": "归胃、肝、胆经", "efficacy": "祛风湿，清湿热，止痹痛，退虚热", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "桑寄生", "aliases": ["寄生", "广寄生"], "category": "祛风湿药", "nature": "平", "flavor": "苦、甘", "meridian_tropism": "归肝、肾经", "efficacy": "祛风湿，补肝肾，强筋骨，安胎元", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "五加皮", "aliases": ["南五加皮"], "category": "祛风湿药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归肝、肾经", "efficacy": "祛风除湿，补益肝肾，强筋壮骨，利水消肿", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 化湿药 ──
  {"name": "苍术", "aliases": ["赤术", "青术"], "category": "化湿药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归脾、胃、肝经", "efficacy": "燥湿健脾，祛风散寒，明目", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "厚朴", "aliases": ["赤朴", "烈朴"], "category": "化湿药", "nature": "温", "flavor": "苦、辛", "meridian_tropism": "归脾、胃、肺、大肠经", "efficacy": "燥湿消痰，下气除满", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "藿香", "aliases": ["土藿香", "排香草"], "category": "化湿药", "nature": "微温", "flavor": "辛", "meridian_tropism": "归脾、胃、肺经", "efficacy": "化湿醒脾，辟秽和中，解暑发表", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "佩兰", "aliases": ["兰草", "水香"], "category": "化湿药", "nature": "平", "flavor": "辛", "meridian_tropism": "归脾、胃、肺经", "efficacy": "化湿醒脾，解暑", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "砂仁", "aliases": ["春砂仁", "缩砂仁"], "category": "化湿药", "nature": "温", "flavor": "辛", "meridian_tropism": "归脾、胃、肾经", "efficacy": "化湿开胃，温脾止泻，理气安胎", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "白豆蔻", "aliases": ["豆蔻", "白蔻"], "category": "化湿药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肺、脾、胃经", "efficacy": "化湿行气，温中止呕", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "草豆蔻", "aliases": ["草蔻", "豆蔻"], "category": "化湿药", "nature": "温", "flavor": "辛", "meridian_tropism": "归脾、胃经", "efficacy": "燥湿行气，温中止呕", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 利水渗湿药 ──
  {"name": "茯苓", "aliases": ["云苓", "松苓"], "category": "利水渗湿药", "nature": "平", "flavor": "甘、淡", "meridian_tropism": "归心、肺、脾、肾经", "efficacy": "利水渗湿，健脾宁心", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "泽泻", "aliases": ["水泻", "芒芋"], "category": "利水渗湿药", "nature": "寒", "flavor": "甘、淡", "meridian_tropism": "归肾、膀胱经", "efficacy": "利水渗湿，泄热化浊", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "薏苡仁", "aliases": ["薏米", "苡仁"], "category": "利水渗湿药", "nature": "凉", "flavor": "甘、淡", "meridian_tropism": "归脾、胃、肺经", "efficacy": "利水渗湿，健脾止泻，解毒散结", "dosage_min": 9, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "车前子", "aliases": ["车前实", "凤眼前仁"], "category": "利水渗湿药", "nature": "寒", "flavor": "甘", "meridian_tropism": "归肝、肾、肺、小肠经", "efficacy": "清热利尿，渗湿通淋，明目祛痰", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "滑石", "aliases": ["画石", "液石"], "category": "利水渗湿药", "nature": "寒", "flavor": "甘、淡", "meridian_tropism": "归膀胱、肺经", "efficacy": "利尿通淋，清热解暑，收湿敛疮", "dosage_min": 10, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "木通", "aliases": ["关木通", "川木通"], "category": "利水渗湿药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归心、小肠、膀胱经", "efficacy": "利尿通淋，清心除烦，通经下乳", "dosage_min": 3, "dosage_max": 6, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "通草", "aliases": ["葱草", "白通草"], "category": "利水渗湿药", "nature": "微寒", "flavor": "甘、淡", "meridian_tropism": "归肺、胃经", "efficacy": "清热利尿，通气下乳", "dosage_min": 3, "dosage_max": 5, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "瞿麦", "aliases": ["巨麦", "大菊"], "category": "利水渗湿药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归心、小肠经", "efficacy": "利尿通淋，破血通经", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "茵陈", "aliases": ["茵陈蒿", "绵茵陈"], "category": "利水渗湿药", "nature": "微寒", "flavor": "苦、辛", "meridian_tropism": "归脾、胃、肝、胆经", "efficacy": "清利湿热，利胆退黄", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "金钱草", "aliases": ["过路黄", "铜钱草"], "category": "利水渗湿药", "nature": "微寒", "flavor": "甘、咸", "meridian_tropism": "归肝、胆、肾、膀胱经", "efficacy": "利湿退黄，利尿通淋，解毒消肿", "dosage_min": 15, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "海金沙", "aliases": ["竹园荽"], "category": "利水渗湿药", "nature": "寒", "flavor": "甘、咸", "meridian_tropism": "归膀胱、小肠经", "efficacy": "清利湿热，通淋止痛", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 温里药 ──
  {"name": "附子", "aliases": ["附片", "黑顺片"], "category": "温里药", "nature": "大热", "flavor": "辛、甘", "meridian_tropism": "归心、肾、脾经", "efficacy": "回阳救逆，补火助阳，散寒止痛", "dosage_min": 3, "dosage_max": 15, "toxicity": "有大毒", "pregnancy_contraindicated": True},
  {"name": "干姜", "aliases": ["白姜", "均姜"], "category": "温里药", "nature": "热", "flavor": "辛", "meridian_tropism": "归脾、胃、肾、心、肺经", "efficacy": "温中散寒，回阳通脉，温肺化饮", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "肉桂", "aliases": ["官桂", "桂皮"], "category": "温里药", "nature": "大热", "flavor": "辛、甘", "meridian_tropism": "归肾、脾、心、肝经", "efficacy": "补火助阳，引火归元，散寒止痛，温通经脉", "dosage_min": 1, "dosage_max": 5, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "吴茱萸", "aliases": ["吴萸", "左力"], "category": "温里药", "nature": "热", "flavor": "辛、苦", "meridian_tropism": "归肝、脾、胃、肾经", "efficacy": "散寒止痛，降逆止呕，助阳止泻", "dosage_min": 2, "dosage_max": 5, "toxicity": "有小毒", "pregnancy_contraindicated": False},
  {"name": "小茴香", "aliases": ["茴香", "谷茴香"], "category": "温里药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肝、肾、脾、胃经", "efficacy": "散寒止痛，理气和胃", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "丁香", "aliases": ["公丁香", "丁子香"], "category": "温里药", "nature": "温", "flavor": "辛", "meridian_tropism": "归脾、胃、肺、肾经", "efficacy": "温中降逆，补肾助阳", "dosage_min": 1, "dosage_max": 3, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "高良姜", "aliases": ["良姜", "小良姜"], "category": "温里药", "nature": "热", "flavor": "辛", "meridian_tropism": "归脾、胃经", "efficacy": "温胃止呕，散寒止痛", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "花椒", "aliases": ["蜀椒", "川椒"], "category": "温里药", "nature": "温", "flavor": "辛", "meridian_tropism": "归脾、胃、肾经", "efficacy": "温中止痛，杀虫止痒", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "胡椒", "aliases": ["白胡椒", "黑胡椒"], "category": "温里药", "nature": "热", "flavor": "辛", "meridian_tropism": "归胃、大肠经", "efficacy": "温中散寒，下气消痰", "dosage_min": 1, "dosage_max": 3, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 理气药 ──
  {"name": "陈皮", "aliases": ["橘皮", "贵老"], "category": "理气药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归脾、肺经", "efficacy": "理气健脾，燥湿化痰", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "枳实", "aliases": ["鹅眼枳实"], "category": "理气药", "nature": "微寒", "flavor": "苦、辛、酸", "meridian_tropism": "归脾、胃经", "efficacy": "破气消积，化痰散痞", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "枳壳", "aliases": ["川枳壳"], "category": "理气药", "nature": "微寒", "flavor": "苦、辛、酸", "meridian_tropism": "归脾、胃经", "efficacy": "理气宽中，行滞消胀", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "香附", "aliases": ["莎草根", "香附子"], "category": "理气药", "nature": "平", "flavor": "辛、微苦、微甘", "meridian_tropism": "归肝、脾、三焦经", "efficacy": "疏肝解郁，理气宽中，调经止痛", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "木香", "aliases": ["广木香", "云木香"], "category": "理气药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归脾、胃、大肠、三焦、胆经", "efficacy": "行气止痛，健脾消食", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "乌药", "aliases": ["台乌药", "矮樟"], "category": "理气药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肺、脾、肾、膀胱经", "efficacy": "行气止痛，温肾散寒", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "沉香", "aliases": ["蜜香", "沉水香"], "category": "理气药", "nature": "微温", "flavor": "辛、苦", "meridian_tropism": "归脾、胃、肾经", "efficacy": "行气止痛，温中止呕，纳气平喘", "dosage_min": 1, "dosage_max": 5, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "檀香", "aliases": ["白檀香"], "category": "理气药", "nature": "温", "flavor": "辛", "meridian_tropism": "归脾、胃、心、肺经", "efficacy": "行气温中，开胃止痛", "dosage_min": 1, "dosage_max": 3, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "薤白", "aliases": ["野蒜", "小独蒜"], "category": "理气药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归心、肺、胃、大肠经", "efficacy": "通阳散结，行气导滞", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "大腹皮", "aliases": ["槟榔皮", "大腹毛"], "category": "理气药", "nature": "微温", "flavor": "辛", "meridian_tropism": "归脾、胃、大肠、小肠经", "efficacy": "行气宽中，行水消肿", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "青皮", "aliases": ["青橘皮", "小青皮"], "category": "理气药", "nature": "温", "flavor": "苦、辛", "meridian_tropism": "归肝、胆、胃经", "efficacy": "疏肝破气，消积化滞", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "佛手", "aliases": ["佛手柑", "五指柑"], "category": "理气药", "nature": "温", "flavor": "辛、苦、酸", "meridian_tropism": "归肝、脾、胃、肺经", "efficacy": "疏肝解郁，理气和中，燥湿化痰", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "玫瑰花", "aliases": ["徘徊花", "笔头花"], "category": "理气药", "nature": "温", "flavor": "甘、微苦", "meridian_tropism": "归肝、脾经", "efficacy": "行气解郁，和血止痛", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 消食药 ──
  {"name": "山楂", "aliases": ["酸楂", "山里红"], "category": "消食药", "nature": "微温", "flavor": "酸、甘", "meridian_tropism": "归脾、胃、肝经", "efficacy": "消食健胃，行气散瘀，化浊降脂", "dosage_min": 10, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "神曲", "aliases": ["六神曲", "建曲"], "category": "消食药", "nature": "温", "flavor": "甘、辛", "meridian_tropism": "归脾、胃经", "efficacy": "消食和胃", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "麦芽", "aliases": ["大麦芽", "麦糵"], "category": "消食药", "nature": "平", "flavor": "甘", "meridian_tropism": "归脾、胃经", "efficacy": "行气消食，健脾开胃，回乳消胀", "dosage_min": 10, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "谷芽", "aliases": ["稻芽", "粟芽"], "category": "消食药", "nature": "温", "flavor": "甘", "meridian_tropism": "归脾、胃经", "efficacy": "消食和中，健脾开胃", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "莱菔子", "aliases": ["萝卜子", "芦菔子"], "category": "消食药", "nature": "平", "flavor": "辛、甘", "meridian_tropism": "归肺、脾、胃经", "efficacy": "消食除胀，降气化痰", "dosage_min": 5, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "鸡内金", "aliases": ["鸡肫皮", "鸡黄皮"], "category": "消食药", "nature": "平", "flavor": "甘", "meridian_tropism": "归脾、胃、小肠、膀胱经", "efficacy": "消食健胃，固精止遗，化结石", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 止血药 ──
  {"name": "白及", "aliases": ["白芨", "甘根"], "category": "止血药", "nature": "微寒", "flavor": "苦、甘、涩", "meridian_tropism": "归肺、肝、胃经", "efficacy": "收敛止血，消肿生肌", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "仙鹤草", "aliases": ["龙芽草", "脱力草"], "category": "止血药", "nature": "平", "flavor": "苦、涩", "meridian_tropism": "归心、肝经", "efficacy": "收敛止血，截疟止痢，解毒补虚", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "蒲黄", "aliases": ["蒲花", "蒲棒粉"], "category": "止血药", "nature": "平", "flavor": "甘", "meridian_tropism": "归肝、心包经", "efficacy": "止血化瘀，通淋", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "三七", "aliases": ["田七", "金不换"], "category": "止血药", "nature": "温", "flavor": "甘、微苦", "meridian_tropism": "归肝、胃经", "efficacy": "散瘀止血，消肿定痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "茜草", "aliases": ["血见愁", "地苏木"], "category": "止血药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肝经", "efficacy": "凉血止血，祛瘀通经", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "艾叶", "aliases": ["艾蒿", "灸草"], "category": "止血药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归肝、脾、肾经", "efficacy": "散寒止痛，温经止血", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "地榆", "aliases": ["黄爪香", "玉豉"], "category": "止血药", "nature": "微寒", "flavor": "苦、酸、涩", "meridian_tropism": "归肝、大肠经", "efficacy": "凉血止血，解毒敛疮", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "槐花", "aliases": ["槐蕊"], "category": "止血药", "nature": "微寒", "flavor": "苦", "meridian_tropism": "归肝、大肠经", "efficacy": "凉血止血，清肝泻火", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "白茅根", "aliases": ["茅根", "茅草根"], "category": "止血药", "nature": "寒", "flavor": "甘", "meridian_tropism": "归肺、胃、膀胱经", "efficacy": "凉血止血，清热利尿", "dosage_min": 9, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 活血化瘀药 ──
  {"name": "川芎", "aliases": ["芎藭", "小叶川芎"], "category": "活血化瘀药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肝、胆、心包经", "efficacy": "活血行气，祛风止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "丹参", "aliases": ["血参", "赤参"], "category": "活血化瘀药", "nature": "微寒", "flavor": "苦", "meridian_tropism": "归心、心包、肝经", "efficacy": "活血祛瘀，通经止痛，清心除烦，凉血消痈", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "红花", "aliases": ["草红花", "红蓝花"], "category": "活血化瘀药", "nature": "温", "flavor": "辛", "meridian_tropism": "归心、肝经", "efficacy": "活血通经，散瘀止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "桃仁", "aliases": ["桃核仁"], "category": "活血化瘀药", "nature": "平", "flavor": "苦、甘", "meridian_tropism": "归心、肝、大肠经", "efficacy": "活血祛瘀，润肠通便，止咳平喘", "dosage_min": 5, "dosage_max": 9, "toxicity": "有小毒", "pregnancy_contraindicated": True},
  {"name": "益母草", "aliases": ["茺蔚", "坤草"], "category": "活血化瘀药", "nature": "微寒", "flavor": "辛、苦", "meridian_tropism": "归心、肝、膀胱经", "efficacy": "活血调经，利尿消肿，清热解毒", "dosage_min": 9, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "牛膝", "aliases": ["怀牛膝", "川牛膝"], "category": "活血化瘀药", "nature": "平", "flavor": "苦、甘、酸", "meridian_tropism": "归肝、肾经", "efficacy": "补肝肾，强筋骨，逐瘀通经，引血下行", "dosage_min": 5, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "鸡血藤", "aliases": ["血风藤"], "category": "活血化瘀药", "nature": "温", "flavor": "苦、甘", "meridian_tropism": "归肝、肾经", "efficacy": "活血补血，调经止痛，舒筋活络", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "延胡索", "aliases": ["元胡", "玄胡索"], "category": "活血化瘀药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归肝、脾经", "efficacy": "活血行气止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "郁金", "aliases": ["玉金", "马蒁"], "category": "活血化瘀药", "nature": "寒", "flavor": "辛、苦", "meridian_tropism": "归肝、心、肺经", "efficacy": "活血止痛，行气解郁，清心凉血，利胆退黄", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "姜黄", "aliases": ["黄姜", "宝鼎香"], "category": "活血化瘀药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归肝、脾经", "efficacy": "破血行气，通经止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "乳香", "aliases": ["熏陆香", "马尾香"], "category": "活血化瘀药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归心、肝、脾经", "efficacy": "活血行气止痛，消肿生肌", "dosage_min": 3, "dosage_max": 5, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "没药", "aliases": ["末药"], "category": "活血化瘀药", "nature": "平", "flavor": "辛、苦", "meridian_tropism": "归心、肝、脾经", "efficacy": "散瘀定痛，消肿生肌", "dosage_min": 3, "dosage_max": 5, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "五灵脂", "aliases": ["灵脂", "寒号虫粪"], "category": "活血化瘀药", "nature": "温", "flavor": "苦、甘", "meridian_tropism": "归肝经", "efficacy": "活血止痛，化瘀止血", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "莪术", "aliases": ["温莪术", "蓬术"], "category": "活血化瘀药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归肝、脾经", "efficacy": "破血行气，消积止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "三棱", "aliases": ["荆三棱", "京三棱"], "category": "活血化瘀药", "nature": "平", "flavor": "辛、苦", "meridian_tropism": "归肝、脾经", "efficacy": "破血行气，消积止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "水蛭", "aliases": ["蚂蟥"], "category": "活血化瘀药", "nature": "平", "flavor": "咸、苦", "meridian_tropism": "归肝经", "efficacy": "破血通经，逐瘀消癥", "dosage_min": 1, "dosage_max": 3, "toxicity": "有小毒", "pregnancy_contraindicated": True},
  {"name": "穿山甲", "aliases": ["鲮鲤甲", "甲片"], "category": "活血化瘀药", "nature": "微寒", "flavor": "咸", "meridian_tropism": "归肝、胃经", "efficacy": "活血消癥，通经下乳，消肿排脓", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "王不留行", "aliases": ["留行子", "麦蓝子"], "category": "活血化瘀药", "nature": "平", "flavor": "苦", "meridian_tropism": "归肝、胃经", "efficacy": "活血通经，下乳消肿，利尿通淋", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": True},

  # ── 化痰止咳平喘药 ──
  {"name": "半夏", "aliases": ["地文", "守田"], "category": "化痰止咳平喘药", "nature": "温", "flavor": "辛", "meridian_tropism": "归脾、胃、肺经", "efficacy": "燥湿化痰，降逆止呕，消痞散结", "dosage_min": 3, "dosage_max": 9, "toxicity": "有毒", "pregnancy_contraindicated": False},
  {"name": "天南星", "aliases": ["南星", "虎掌"], "category": "化痰止咳平喘药", "nature": "温", "flavor": "苦、辛", "meridian_tropism": "归肺、肝、脾经", "efficacy": "燥湿化痰，祛风止痉，散结消肿", "dosage_min": 3, "dosage_max": 9, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "白芥子", "aliases": ["芥子", "辣菜子"], "category": "化痰止咳平喘药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肺经", "efficacy": "温肺豁痰利气，散结通络止痛", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "桔梗", "aliases": ["符蔰", "白药"], "category": "化痰止咳平喘药", "nature": "平", "flavor": "苦、辛", "meridian_tropism": "归肺经", "efficacy": "宣肺利咽，祛痰排脓", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "旋覆花", "aliases": ["金佛花", "六月菊"], "category": "化痰止咳平喘药", "nature": "微温", "flavor": "苦、辛、咸", "meridian_tropism": "归肺、脾、胃、大肠经", "efficacy": "降气消痰，行水止呕", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "瓜蒌", "aliases": ["栝楼", "天瓜"], "category": "化痰止咳平喘药", "nature": "寒", "flavor": "甘、微苦", "meridian_tropism": "归肺、胃、大肠经", "efficacy": "清热涤痰，宽胸散结，润肠通便", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "贝母", "aliases": ["川贝", "浙贝", "土贝"], "category": "化痰止咳平喘药", "nature": "微寒", "flavor": "苦", "meridian_tropism": "归肺、心经", "efficacy": "清热润肺，化痰止咳，散结消痈", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "竹茹", "aliases": ["竹皮", "青竹茹"], "category": "化痰止咳平喘药", "nature": "微寒", "flavor": "甘", "meridian_tropism": "归肺、胃、心、胆经", "efficacy": "清热化痰，除烦止呕", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "前胡", "aliases": ["姨妈菜", "罗鬼菜"], "category": "化痰止咳平喘药", "nature": "微寒", "flavor": "苦、辛", "meridian_tropism": "归肺经", "efficacy": "降气化痰，散风清热", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "杏仁", "aliases": ["苦杏仁", "北杏"], "category": "化痰止咳平喘药", "nature": "微温", "flavor": "苦", "meridian_tropism": "归肺、大肠经", "efficacy": "降气止咳平喘，润肠通便", "dosage_min": 5, "dosage_max": 9, "toxicity": "有小毒", "pregnancy_contraindicated": False},
  {"name": "紫苏子", "aliases": ["苏子", "黑苏子"], "category": "化痰止咳平喘药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肺经", "efficacy": "降气消痰，平喘润肠", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "百部", "aliases": ["百条根", "九虫根"], "category": "化痰止咳平喘药", "nature": "微温", "flavor": "甘、苦", "meridian_tropism": "归肺经", "efficacy": "润肺下气止咳，杀虫灭虱", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "紫菀", "aliases": ["紫蒨", "返魂草"], "category": "化痰止咳平喘药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归肺经", "efficacy": "润肺下气，消痰止咳", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "款冬花", "aliases": ["冬花", "艾冬花"], "category": "化痰止咳平喘药", "nature": "温", "flavor": "辛、微苦", "meridian_tropism": "归肺经", "efficacy": "润肺下气，止咳化痰", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "枇杷叶", "aliases": ["巴叶", "芦桔叶"], "category": "化痰止咳平喘药", "nature": "微寒", "flavor": "苦", "meridian_tropism": "归肺、胃经", "efficacy": "清肺止咳，降逆止呕", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "桑白皮", "aliases": ["桑根皮", "桑皮"], "category": "化痰止咳平喘药", "nature": "寒", "flavor": "甘", "meridian_tropism": "归肺经", "efficacy": "泻肺平喘，利水消肿", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "葶苈子", "aliases": ["大适", "丁历"], "category": "化痰止咳平喘药", "nature": "大寒", "flavor": "辛、苦", "meridian_tropism": "归肺、膀胱经", "efficacy": "泻肺平喘，行水消肿", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 安神药 ──
  {"name": "酸枣仁", "aliases": ["枣仁", "酸枣核"], "category": "安神药", "nature": "平", "flavor": "甘、酸", "meridian_tropism": "归心、肝、胆经", "efficacy": "养心补肝，宁心安神，敛汗生津", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "柏子仁", "aliases": ["柏实", "侧柏子"], "category": "安神药", "nature": "平", "flavor": "甘", "meridian_tropism": "归心、肾、大肠经", "efficacy": "养心安神，润肠通便", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "远志", "aliases": ["细草", "小草"], "category": "安神药", "nature": "温", "flavor": "苦、辛", "meridian_tropism": "归心、肾、肺经", "efficacy": "安神益智，祛痰开窍，消散痈肿", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "合欢皮", "aliases": ["合昏皮", "夜合皮"], "category": "安神药", "nature": "平", "flavor": "甘", "meridian_tropism": "归心、肝经", "efficacy": "解郁安神，活血消肿", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "龙骨", "aliases": ["白龙骨", "五花龙骨"], "category": "安神药", "nature": "平", "flavor": "甘、涩", "meridian_tropism": "归心、肝、肾经", "efficacy": "镇惊安神，平肝潜阳，收敛固涩", "dosage_min": 15, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "牡蛎", "aliases": ["蛎蛤", "蚝壳"], "category": "安神药", "nature": "微寒", "flavor": "咸", "meridian_tropism": "归肝、胆、肾经", "efficacy": "重镇安神，潜阳补阴，软坚散结", "dosage_min": 15, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "朱砂", "aliases": ["丹砂", "辰砂"], "category": "安神药", "nature": "微寒", "flavor": "甘", "meridian_tropism": "归心经", "efficacy": "清心镇惊，安神解毒", "dosage_min": 0.1, "dosage_max": 0.5, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "磁石", "aliases": ["吸铁石", "玄石"], "category": "安神药", "nature": "寒", "flavor": "咸", "meridian_tropism": "归肾、肝经", "efficacy": "镇惊安神，平肝潜阳，聪耳明目，纳气平喘", "dosage_min": 15, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 平肝息风药 ──
  {"name": "天麻", "aliases": ["赤箭", "定风草"], "category": "平肝息风药", "nature": "平", "flavor": "甘", "meridian_tropism": "归肝经", "efficacy": "息风止痉，平抑肝阳，祛风通络", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "钩藤", "aliases": ["钩丁", "双钩"], "category": "平肝息风药", "nature": "凉", "flavor": "甘", "meridian_tropism": "归肝、心包经", "efficacy": "息风定惊，清热平肝", "dosage_min": 3, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "石决明", "aliases": ["鲍鱼壳", "九孔螺"], "category": "平肝息风药", "nature": "寒", "flavor": "咸", "meridian_tropism": "归肝经", "efficacy": "平肝潜阳，清肝明目", "dosage_min": 6, "dosage_max": 20, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "珍珠母", "aliases": ["珠母", "明珠母"], "category": "平肝息风药", "nature": "寒", "flavor": "咸", "meridian_tropism": "归肝、心经", "efficacy": "平肝潜阳，安神定惊，明目退翳", "dosage_min": 10, "dosage_max": 25, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "代赭石", "aliases": ["赭石", "钉头赭石"], "category": "平肝息风药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归肝、心、肺、胃经", "efficacy": "平肝潜阳，重镇降逆，凉血止血", "dosage_min": 9, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "全蝎", "aliases": ["蝎子", "全虫"], "category": "平肝息风药", "nature": "平", "flavor": "辛", "meridian_tropism": "归肝经", "efficacy": "息风镇痉，通络止痛，攻毒散结", "dosage_min": 3, "dosage_max": 6, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "蜈蚣", "aliases": ["百足虫", "天龙"], "category": "平肝息风药", "nature": "温", "flavor": "辛", "meridian_tropism": "归肝经", "efficacy": "息风镇痉，通络止痛，攻毒散结", "dosage_min": 3, "dosage_max": 5, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "地龙", "aliases": ["蚯蚓", "土龙"], "category": "平肝息风药", "nature": "寒", "flavor": "咸", "meridian_tropism": "归肝、脾、膀胱经", "efficacy": "清热定惊，通络平喘，利尿", "dosage_min": 5, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "僵蚕", "aliases": ["白僵蚕", "天虫"], "category": "平肝息风药", "nature": "平", "flavor": "咸、辛", "meridian_tropism": "归肝、肺经", "efficacy": "息风止痉，祛风止痛，化痰散结", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 开窍药 ──
  {"name": "麝香", "aliases": ["遗香", "心结香"], "category": "开窍药", "nature": "温", "flavor": "辛", "meridian_tropism": "归心、脾经", "efficacy": "开窍醒神，活血通经，消肿止痛", "dosage_min": 0.03, "dosage_max": 0.1, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "冰片", "aliases": ["龙脑", "梅片"], "category": "开窍药", "nature": "微寒", "flavor": "辛、苦", "meridian_tropism": "归心、脾、肺经", "efficacy": "开窍醒神，清热止痛", "dosage_min": 0.15, "dosage_max": 0.3, "toxicity": "无毒", "pregnancy_contraindicated": True},
  {"name": "石菖蒲", "aliases": ["菖蒲", "昌阳"], "category": "开窍药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归心、胃经", "efficacy": "开窍豁痰，醒神益智，化湿开胃", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "苏合香", "aliases": ["帝膏", "苏合油"], "category": "开窍药", "nature": "温", "flavor": "辛", "meridian_tropism": "归心、脾经", "efficacy": "开窍辟秽，止痛", "dosage_min": 0.3, "dosage_max": 1, "toxicity": "无毒", "pregnancy_contraindicated": True},

  # ── 补虚药 ──
  {"name": "人参", "aliases": ["棒锤", "山参", "园参", "红参"], "category": "补虚药", "nature": "温", "flavor": "甘、微苦", "meridian_tropism": "归脾、肺、心、肾经", "efficacy": "大补元气，复脉固脱，补脾益肺，生津养血，安神益智", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "党参", "aliases": ["上党人参", "黄参"], "category": "补虚药", "nature": "平", "flavor": "甘", "meridian_tropism": "归脾、肺经", "efficacy": "健脾益肺，养血生津", "dosage_min": 9, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "黄芪", "aliases": ["绵芪", "黄耆"], "category": "补虚药", "nature": "微温", "flavor": "甘", "meridian_tropism": "归肺、脾经", "efficacy": "补气升阳，固表止汗，利水消肿，生津养血，托毒排脓", "dosage_min": 9, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "白术", "aliases": ["于术", "冬白术"], "category": "补虚药", "nature": "温", "flavor": "甘、苦", "meridian_tropism": "归脾、胃经", "efficacy": "健脾益气，燥湿利水，止汗安胎", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "山药", "aliases": ["薯蓣", "淮山"], "category": "补虚药", "nature": "平", "flavor": "甘", "meridian_tropism": "归脾、肺、肾经", "efficacy": "补脾养胃，生津益肺，补肾涩精", "dosage_min": 15, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "甘草", "aliases": ["国老", "蜜草", "粉草"], "category": "补虚药", "nature": "平", "flavor": "甘", "meridian_tropism": "归心、肺、脾、胃经", "efficacy": "补脾益气，清热解毒，祛痰止咳，缓急止痛，调和诸药", "dosage_min": 2, "dosage_max": 10, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "大枣", "aliases": ["红枣", "干枣"], "category": "补虚药", "nature": "温", "flavor": "甘", "meridian_tropism": "归脾、胃、心经", "efficacy": "补中益气，养血安神", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "当归", "aliases": ["干归", "秦归"], "category": "补虚药", "nature": "温", "flavor": "甘、辛", "meridian_tropism": "归肝、心、脾经", "efficacy": "补血活血，调经止痛，润肠通便", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "熟地黄", "aliases": ["熟地", "大熟地"], "category": "补虚药", "nature": "微温", "flavor": "甘", "meridian_tropism": "归肝、肾经", "efficacy": "补血滋阴，益精填髓", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "白芍", "aliases": ["金芍药", "白芍药"], "category": "补虚药", "nature": "微寒", "flavor": "苦、酸", "meridian_tropism": "归肝、脾经", "efficacy": "养血调经，敛阴止汗，柔肝止痛，平抑肝阳", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "阿胶", "aliases": ["傅致胶", "盆覆胶"], "category": "补虚药", "nature": "平", "flavor": "甘", "meridian_tropism": "归肺、肝、肾经", "efficacy": "补血滋阴，润燥止血", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "何首乌", "aliases": ["首乌", "赤首乌"], "category": "补虚药", "nature": "微温", "flavor": "苦、甘、涩", "meridian_tropism": "归肝、心、肾经", "efficacy": "解毒消痈，润肠通便，补肝肾益精血", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "龙眼肉", "aliases": ["桂圆肉", "益智"], "category": "补虚药", "nature": "温", "flavor": "甘", "meridian_tropism": "归心、脾经", "efficacy": "补益心脾，养血安神", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "鹿茸", "aliases": ["斑龙珠"], "category": "补虚药", "nature": "温", "flavor": "甘、咸", "meridian_tropism": "归肾、肝经", "efficacy": "壮肾阳，益精血，强筋骨，调冲任，托疮毒", "dosage_min": 1, "dosage_max": 2, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "淫羊藿", "aliases": ["仙灵脾", "三枝九叶草"], "category": "补虚药", "nature": "温", "flavor": "辛、甘", "meridian_tropism": "归肝、肾经", "efficacy": "补肾阳，强筋骨，祛风湿", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "巴戟天", "aliases": ["鸡肠风", "兔子肠"], "category": "补虚药", "nature": "微温", "flavor": "辛、甘", "meridian_tropism": "归肾、肝经", "efficacy": "补肾阳，强筋骨，祛风除湿", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "肉苁蓉", "aliases": ["大芸", "寸芸"], "category": "补虚药", "nature": "温", "flavor": "甘、咸", "meridian_tropism": "归肾、大肠经", "efficacy": "补肾阳，益精血，润肠通便", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "补骨脂", "aliases": ["破故纸", "婆固脂"], "category": "补虚药", "nature": "温", "flavor": "辛、苦", "meridian_tropism": "归肾、脾经", "efficacy": "补肾助阳，温脾止泻，纳气平喘", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "杜仲", "aliases": ["丝连皮", "玉丝皮"], "category": "补虚药", "nature": "温", "flavor": "甘", "meridian_tropism": "归肝、肾经", "efficacy": "补肝肾，强筋骨，安胎", "dosage_min": 6, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "续断", "aliases": ["川断", "接骨草"], "category": "补虚药", "nature": "微温", "flavor": "苦、辛", "meridian_tropism": "归肝、肾经", "efficacy": "补肝肾，强筋骨，续折伤，止崩漏", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "菟丝子", "aliases": ["豆寄生", "黄丝"], "category": "补虚药", "nature": "平", "flavor": "甘", "meridian_tropism": "归肝、肾、脾经", "efficacy": "补益肝肾，固精缩尿，安胎明目，止泻", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "沙苑子", "aliases": ["潼蒺藜", "沙苑蒺藜"], "category": "补虚药", "nature": "温", "flavor": "甘", "meridian_tropism": "归肝、肾经", "efficacy": "补肾助阳，固精缩尿，养肝明目", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "蛤蚧", "aliases": ["大壁虎", "仙蟾"], "category": "补虚药", "nature": "平", "flavor": "咸", "meridian_tropism": "归肺、肾经", "efficacy": "补肺益肾，纳气平喘，助阳益精", "dosage_min": 3, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "冬虫夏草", "aliases": ["虫草", "夏草冬虫"], "category": "补虚药", "nature": "平", "flavor": "甘", "meridian_tropism": "归肾、肺经", "efficacy": "补肾益肺，止血化痰", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "南沙参", "aliases": ["沙参", "泡参"], "category": "补虚药", "nature": "微寒", "flavor": "甘", "meridian_tropism": "归肺、胃经", "efficacy": "养阴清肺，益胃生津，化痰益气", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "北沙参", "aliases": ["海沙参", "银沙参"], "category": "补虚药", "nature": "微寒", "flavor": "甘、微苦", "meridian_tropism": "归肺、胃经", "efficacy": "养阴清肺，益胃生津", "dosage_min": 5, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "麦冬", "aliases": ["麦门冬", "寸冬"], "category": "补虚药", "nature": "微寒", "flavor": "甘、微苦", "meridian_tropism": "归心、肺、胃经", "efficacy": "养阴生津，润肺清心", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "天冬", "aliases": ["天门冬", "明天冬"], "category": "补虚药", "nature": "寒", "flavor": "甘、苦", "meridian_tropism": "归肺、肾经", "efficacy": "养阴润燥，清肺生津", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "石斛", "aliases": ["金钗石斛", "黄草"], "category": "补虚药", "nature": "微寒", "flavor": "甘", "meridian_tropism": "归胃、肾经", "efficacy": "益胃生津，滋阴清热", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "百合", "aliases": ["白百合", "蒜脑薯"], "category": "补虚药", "nature": "微寒", "flavor": "甘", "meridian_tropism": "归心、肺经", "efficacy": "养阴润肺，清心安神", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "枸杞子", "aliases": ["枸杞红实", "甜菜子"], "category": "补虚药", "nature": "平", "flavor": "甘", "meridian_tropism": "归肝、肾经", "efficacy": "滋补肝肾，益精明目", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "女贞子", "aliases": ["女贞实", "冬青子"], "category": "补虚药", "nature": "凉", "flavor": "甘、苦", "meridian_tropism": "归肝、肾经", "efficacy": "滋补肝肾，明目乌发", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "墨旱莲", "aliases": ["旱莲草", "鳢肠"], "category": "补虚药", "nature": "寒", "flavor": "甘、酸", "meridian_tropism": "归肾、肝经", "efficacy": "滋补肝肾，凉血止血", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "龟甲", "aliases": ["龟板", "龟壳"], "category": "补虚药", "nature": "寒", "flavor": "甘、咸", "meridian_tropism": "归肝、肾、心经", "efficacy": "滋阴潜阳，益肾强骨，养血补心，固经止崩", "dosage_min": 9, "dosage_max": 24, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "鳖甲", "aliases": ["上甲", "团鱼甲"], "category": "补虚药", "nature": "寒", "flavor": "咸", "meridian_tropism": "归肝、肾经", "efficacy": "滋阴潜阳，退热除蒸，软坚散结", "dosage_min": 9, "dosage_max": 24, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 收涩药 ──
  {"name": "五味子", "aliases": ["五梅子", "山花椒"], "category": "收涩药", "nature": "温", "flavor": "酸、甘", "meridian_tropism": "归肺、心、肾经", "efficacy": "收敛固涩，益气生津，补肾宁心", "dosage_min": 2, "dosage_max": 6, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "乌梅", "aliases": ["梅实", "熏梅"], "category": "收涩药", "nature": "平", "flavor": "酸、涩", "meridian_tropism": "归肝、脾、肺、大肠经", "efficacy": "敛肺涩肠，生津安蛔", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "山茱萸", "aliases": ["山萸肉", "枣皮"], "category": "收涩药", "nature": "微温", "flavor": "酸、涩", "meridian_tropism": "归肝、肾经", "efficacy": "补益肝肾，收涩固脱", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "覆盆子", "aliases": ["小托盘"], "category": "收涩药", "nature": "温", "flavor": "甘、酸", "meridian_tropism": "归肝、肾、膀胱经", "efficacy": "益肾固精缩尿，养肝明目", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "金樱子", "aliases": ["刺梨子", "山石榴"], "category": "收涩药", "nature": "平", "flavor": "酸、甘、涩", "meridian_tropism": "归肾、膀胱、大肠经", "efficacy": "固精缩尿，固崩止带，涩肠止泻", "dosage_min": 6, "dosage_max": 12, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "莲子", "aliases": ["莲实", "莲肉"], "category": "收涩药", "nature": "平", "flavor": "甘、涩", "meridian_tropism": "归脾、肾、心经", "efficacy": "补脾止泻，止带，益肾涩精，养心安神", "dosage_min": 6, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "芡实", "aliases": ["鸡头米", "水鸡头"], "category": "收涩药", "nature": "平", "flavor": "甘、涩", "meridian_tropism": "归脾、肾经", "efficacy": "益肾固精，补脾止泻，除湿止带", "dosage_min": 9, "dosage_max": 15, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "海螵蛸", "aliases": ["乌贼骨", "墨鱼骨"], "category": "收涩药", "nature": "微温", "flavor": "咸、涩", "meridian_tropism": "归脾、肾经", "efficacy": "收敛止血，固精止带，制酸止痛，收湿敛疮", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "桑螵蛸", "aliases": ["螵蛸", "刀螂子"], "category": "收涩药", "nature": "平", "flavor": "甘、咸", "meridian_tropism": "归肝、肾经", "efficacy": "固精缩尿，补肾助阳", "dosage_min": 5, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "麻黄根", "aliases": ["苦椿菜"], "category": "收涩药", "nature": "平", "flavor": "甘、涩", "meridian_tropism": "归心、肺经", "efficacy": "固表止汗", "dosage_min": 3, "dosage_max": 9, "toxicity": "无毒", "pregnancy_contraindicated": False},
  {"name": "浮小麦", "aliases": ["浮麦"], "category": "收涩药", "nature": "凉", "flavor": "甘", "meridian_tropism": "归心经", "efficacy": "固表止汗，益气除烦", "dosage_min": 15, "dosage_max": 30, "toxicity": "无毒", "pregnancy_contraindicated": False},

  # ── 涌吐药 ──
  {"name": "瓜蒂", "aliases": ["苦丁香", "甜瓜蒂"], "category": "涌吐药", "nature": "寒", "flavor": "苦", "meridian_tropism": "归胃经", "efficacy": "涌吐痰食，祛湿退黄", "dosage_min": 0.6, "dosage_max": 1.5, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "常山", "aliases": ["恒山", "鸡骨常山"], "category": "涌吐药", "nature": "寒", "flavor": "苦、辛", "meridian_tropism": "归肺、肝、心经", "efficacy": "涌吐痰涎，截疟", "dosage_min": 5, "dosage_max": 9, "toxicity": "有毒", "pregnancy_contraindicated": True},
  {"name": "藜芦", "aliases": ["山葱", "七厘丹"], "category": "涌吐药", "nature": "寒", "flavor": "辛、苦", "meridian_tropism": "归肺、胃、肝经", "efficacy": "涌吐风痰，杀虫", "dosage_min": 0.3, "dosage_max": 0.9, "toxicity": "有毒", "pregnancy_contraindicated": True},
]


def generate():
    """生成扩展药材 JSON"""
    output_file = Path(__file__).parent / "herbs_extended.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(HERBS_DATA, f, ensure_ascii=False, indent=2)
    print(f"[Herbs] 生成 {len(HERBS_DATA)} 味药材 → {output_file}")


if __name__ == "__main__":
    generate()
