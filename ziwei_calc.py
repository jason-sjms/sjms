import math
from datetime import date

try:
    from lunardate import LunarDate
    HAS_LUNARDATE = True
except ImportError:
    HAS_LUNARDATE = False

# ── 基本常數 ──────────────────────────────────────
TIAN_GAN  = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI    = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
SHENGXIAO = ['鼠','牛','虎','兔','龍','蛇','馬','羊','猴','雞','狗','豬']

# 12宮名稱（從命宮順時針）
PALACE_NAMES = ['命宮','兄弟','夫妻','子女','財帛','疾厄','遷移','交友','事業','田宅','福德','父母']

# 五行局：局數 → 名稱
JU_NAME = {2:'水二局', 3:'木三局', 4:'金四局', 5:'土五局', 6:'火六局'}

# 五行局查表（天干組 × 命宮地支對）
# 天干組：甲己=0, 乙庚=1, 丙辛=2, 丁壬=3, 戊癸=4
# 地支對：子午=0, 丑未=1, 寅申=2, 卯酉=3, 辰戌=4, 巳亥=5
JU_TABLE = [
    [2, 6, 5, 3, 4, 5],  # 甲己
    [6, 4, 2, 5, 3, 5],  # 乙庚
    [3, 2, 6, 4, 5, 6],  # 丙辛
    [4, 3, 5, 2, 6, 4],  # 丁壬
    [5, 6, 4, 3, 2, 4],  # 戊癸
]
STEM_GROUP  = {0:0,5:0, 1:1,6:1, 2:2,7:2, 3:3,8:3, 4:4,9:4}
BRANCH_PAIR = {0:0,6:0, 1:1,7:1, 2:2,8:2, 3:3,9:3, 4:4,10:4, 5:5,11:5}

# 時辰 → 地支序號（子=0）
HOUR_TO_BRANCH = [
    (0,1,'子'),(1,3,'丑'),(3,5,'寅'),(5,7,'卯'),(7,9,'辰'),(9,11,'巳'),
    (11,13,'午'),(13,15,'未'),(15,17,'申'),(17,19,'酉'),(19,21,'戌'),(21,24,'亥'),
]

# 宮位特質（用於運勢文字生成）
PALACE_TRAIT = {
    '命宮': '整體運勢、個性與人生方向',
    '財帛': '財運、金錢收入與理財',
    '事業': '事業發展、工作成就',
    '夫妻': '感情、婚姻與伴侶關係',
    '子女': '子女緣份、創意與下屬',
    '交友': '朋友、人際與合作',
    '田宅': '家庭、房產與居家環境',
    '遷移': '出行、變動與外部機遇',
    '福德': '精神、福氣與生活品質',
    '兄弟': '兄弟姐妹與手足緣',
    '疾厄': '健康與身心狀態',
    '父母': '長輩關係、文書與貴人',
}

# 14主星特質
STAR_TRAIT = {
    '紫微': ('帝王之星', '領導力強，有貴人相助，適合走管理路線'),
    '天機': ('智謀之星', '思維敏捷，善於規劃，利於學術與諮詢'),
    '太陽': ('光明之星', '熱情開朗，利於社交與公職，男性緣佳'),
    '武曲': ('財星',     '理財有道，意志堅強，適合財經商業'),
    '天同': ('福星',     '隨和知足，感情豐富，生活安逸'),
    '廉貞': ('囚星',     '有才幹但固執，情緒起伏，需注意人際'),
    '天府': ('庫星',     '守成穩健，財富積累，適合保守投資'),
    '太陰': ('月亮星',   '敏感細膩，直覺佳，女性緣強，利於房地產'),
    '貪狼': ('桃花星',   '多才多藝，人際廣，但易流於享樂'),
    '巨門': ('是非星',   '口才好，善分析，但易有口舌之爭'),
    '天相': ('印星',     '為人厚道，善輔助，貴人多，行政能力強'),
    '天梁': ('蔭星',     '有蔭德，喜助人，適合服務業與醫療'),
    '七殺': ('將星',     '魄力十足，開創力強，但行事衝動'),
    '破軍': ('耗星',     '勇於改革，但變動多，需防耗損'),
}

# 輔星特質
MINOR_STAR_TRAIT = {
    '左輔': '得人緣，有助力，逢凶化吉',
    '右弼': '獲人助，貴人多，增強吉星力量',
    '文昌': '利考試學業，口才佳，有文藝才華',
    '文曲': '藝術天份強，桃花旺，口才佳',
    '天魁': '天乙貴人，在逆境中遇貴人相助',
    '天鉞': '玉堂貴人，社交順暢，有貴人提攜',
}

# ── 犯太歲對照表 ──────────────────────────────────
# 沖：各地支對應的相沖地支（相差6位）
_CHONG = {i: (i + 6) % 12 for i in range(12)}

# 刑：三刑（寅巳申、丑戌未）+ 相刑（子卯）
_XING = {2:5, 5:8, 8:2, 1:10, 10:7, 7:1, 0:3, 3:0}

# 害：六害（子未、丑午、寅巳、卯辰、申亥、酉戌）
_HAI = {0:7, 7:0, 1:6, 6:1, 2:5, 5:2, 3:4, 4:3, 8:11, 11:8, 9:10, 10:9}

# 破：六破（子酉、丑辰、寅亥、卯午、申巳、戌未）
_PO = {0:9, 9:0, 1:4, 4:1, 2:11, 11:2, 3:6, 6:3, 8:5, 5:8, 10:7, 7:10}


def check_fan_taisui(birth_year: int, liunian_year: int) -> dict:
    """判斷流年是否犯太歲，回傳 {type, severity, message, remedy}"""
    bb = (birth_year - 4) % 12
    lb = (liunian_year - 4) % 12
    bz = DI_ZHI[bb];  lz = DI_ZHI[lb]
    bs = SHENGXIAO[bb]; ls = SHENGXIAO[lb]

    if bb == lb:
        return {
            'type': '值太歲', 'severity': 'high',
            'message': f'本命年（屬{bs}，{bz}年生），今年為{lz}年（{ls}年），即「值太歲」。本命年運勢變動較大，凡事宜謹慎低調，避免重大決策或動土遷移。',
            'remedy': '建議到廟宇安太歲、配戴本命佛或太歲符，可有效化解沖犯。',
        }
    if _CHONG.get(bb) == lb:
        return {
            'type': '沖太歲', 'severity': 'high',
            'message': f'屬{bs}（{bz}年生），今年{lz}年（{ls}年）地支相沖，即「沖太歲」。易有較大波折與變動，健康、財運、事業均需格外謹慎。',
            'remedy': '建議安太歲、祈福化解，避免重大投資與冒險行動，多行善積德可增添福蔭。',
        }
    if _XING.get(bb) == lb:
        return {
            'type': '刑太歲', 'severity': 'medium',
            'message': f'屬{bs}（{bz}年生），今年{lz}年（{ls}年）地支相刑，即「刑太歲」。易有是非口舌、官非糾紛或健康問題，宜謹言慎行。',
            'remedy': '建議保持低調，避免爭執，注意健康定期檢查，可至廟宇祈福化解。',
        }
    if _HAI.get(bb) == lb:
        return {
            'type': '害太歲', 'severity': 'medium',
            'message': f'屬{bs}（{bz}年生），今年{lz}年（{ls}年）地支相害，即「害太歲」。易有小人阻礙、人際糾紛，感情與合作關係需多留意。',
            'remedy': '宜廣結善緣，謹慎交友，可配戴化解飾品或至廟宇祈福。',
        }
    if _PO.get(bb) == lb:
        return {
            'type': '破太歲', 'severity': 'low',
            'message': f'屬{bs}（{bz}年生），今年{lz}年（{ls}年）地支相破，即「破太歲」。計劃易生變數，感情、財務需穩步推進，避免輕率行動。',
            'remedy': '宜踏實行事，避免衝動決策，保持平常心即可平順度過。',
        }
    return {'type': None, 'severity': 'none', 'message': '', 'remedy': ''}


# ── 工具函式 ──────────────────────────────────────
def get_year_ganzhi(year: int) -> tuple:
    stem_idx  = (year - 4)  % 10
    branch_idx= (year - 4)  % 12
    return stem_idx, branch_idx, TIAN_GAN[stem_idx], DI_ZHI[branch_idx]

def get_hour_branch(hour: int) -> tuple:
    """小時(0-23) → (地支序號, 地支字)"""
    for h_start, h_end, branch in HOUR_TO_BRANCH:
        if h_start <= hour < h_end:
            idx = DI_ZHI.index(branch)
            return idx, branch
    return 0, '子'

def solar_to_lunar(year: int, month: int, day: int) -> tuple:
    """轉農曆，回傳 (農曆年, 農曆月, 農曆日, 是否閏月)"""
    if HAS_LUNARDATE:
        try:
            ld = LunarDate.fromSolarDate(year, month, day)
            return ld.year, ld.month, ld.day, ld.isLeapMonth
        except Exception:
            pass
    # fallback: 簡易估算（不精確，僅供展示）
    days_since = (date(year, month, day) - date(1900, 1, 31)).days
    lunar_day = (days_since % 30) + 1
    lunar_month = ((days_since // 30) % 12) + 1
    lunar_year = year
    return lunar_year, lunar_month, min(lunar_day, 30), False

# ── 命盤計算 ──────────────────────────────────────
def get_ming_palace(lunar_month: int, hour_branch: int) -> int:
    """命宮地支序號"""
    return (lunar_month + 1 - hour_branch + 24) % 12

def get_shen_palace(lunar_month: int, hour_branch: int) -> int:
    """身宮地支序號"""
    return (lunar_month + 1 + hour_branch) % 12

def get_wuxing_ju(year_stem: int, ming_branch: int) -> int:
    """五行局數 (2/3/4/5/6)"""
    sg = STEM_GROUP[year_stem % 10]
    bp = BRANCH_PAIR[ming_branch % 12]
    return JU_TABLE[sg][bp]

def get_ziwei_position(lunar_day: int, ju: int) -> int:
    """紫微星地支序號（丑起，逆數）"""
    return (2 - math.ceil(lunar_day / ju) + 120) % 12

def get_tianfu_position(ziwei: int) -> int:
    """天府星地支序號"""
    return (4 - ziwei + 120) % 12

def place_all_stars(ziwei: int, tianfu: int,
                   lunar_month: int, hour_branch: int,
                   year_stem: int, year_branch: int) -> dict:
    """回傳 {星名: 地支序號} 字典，含14主星＋6輔星"""
    z, f = ziwei, tianfu
    stars = {
        # 紫微組（逆布）
        '紫微': z,
        '天機': (z - 1 + 12) % 12,
        '太陽': (z - 3 + 12) % 12,
        '武曲': (z - 4 + 12) % 12,
        '天同': (z - 5 + 12) % 12,
        '廉貞': (z - 8 + 12) % 12,
        # 天府組（順布）
        '天府': f,
        '太陰': (f + 1) % 12,
        '貪狼': (f + 2) % 12,
        '巨門': (f + 3) % 12,
        '天相': (f + 4) % 12,
        '天梁': (f + 5) % 12,
        '七殺': (f + 6) % 12,
        '破軍': (z + 6) % 12,
        # 輔星
        '左輔': (3 + lunar_month) % 12,
        '右弼': (11 - lunar_month + 12) % 12,
        '文昌': (9 - year_branch + 12) % 12,
        '文曲': (4 + year_branch) % 12,
    }
    # 天魁天鉞
    tiankui_table  = {0:1,1:0,2:11,3:11,4:1,5:0,6:1,7:6,8:3,9:3}
    tianyue_table  = {0:7,1:8,2:9,3:9,4:7,5:8,6:7,7:2,8:5,9:5}
    stars['天魁'] = tiankui_table.get(year_stem % 10, 0)
    stars['天鉞'] = tianyue_table.get(year_stem % 10, 0)
    return stars

# ── 大限 / 流年 ──────────────────────────────────
def get_daxian_direction(year_stem: int, gender: str) -> int:
    """大限方向：+1 順, -1 逆"""
    yang_year = (year_stem % 2 == 0)
    male = (gender == '男')
    return 1 if (yang_year == male) else -1

def get_current_daxian(ming_branch: int, ju: int, age: int,
                        direction: int) -> tuple:
    """當前大限宮位及起訖年齡"""
    period_idx = (age - ju) // 10
    if period_idx < 0:
        period_idx = 0
    palace_branch = (ming_branch + direction * period_idx) % 12
    start_age = ju + period_idx * 10
    end_age   = start_age + 9
    return palace_branch, start_age, end_age, period_idx

def get_liunian_palace(year: int, ming_branch: int) -> int:
    """流年命宮地支序號（寅起子年，順布）"""
    year_branch = (year - 4) % 12
    return (2 + year_branch) % 12

# ── 運勢文字生成 ──────────────────────────────────
ASPECT_PALACES = {
    '財運': '財帛',
    '事業': '事業',
    '感情家庭': '夫妻',
    '人際朋友': '交友',
    '健康': '疾厄',
}

def palace_offset(ming_branch: int, target_name: str) -> int:
    """取得某宮位的地支序號"""
    idx = PALACE_NAMES.index(target_name)
    return (ming_branch + idx) % 12

def stars_in_palace(stars: dict, branch: int) -> list:
    return [s for s, b in stars.items() if b == branch]

def rate_palace(star_list: list) -> tuple:
    """根據宮內星曜給分(0-100)及評語"""
    lucky_main = {'紫微','天府','太陽','天機','武曲','太陰','天梁','天相','左輔','右弼','文昌','文曲','天魁','天鉞'}
    unlucky_main = {'廉貞','貪狼','巨門','七殺','破軍'}
    score = 60
    comments = []
    for s in star_list:
        if s in lucky_main:
            score += 10
            comments.append(f'{s}（{STAR_TRAIT.get(s, ("",""))[0]}）')
        elif s in unlucky_main:
            score -= 5
            comments.append(f'{s}（{STAR_TRAIT.get(s, ("",""))[0]}）')
        elif s in MINOR_STAR_TRAIT:
            score += 5
    score = max(20, min(100, score))
    return score, comments

def generate_fortune_text(aspect: str, year: int, palace_name: str,
                           star_list: list, score: int, is_daxian: bool) -> str:
    period = '大限' if is_daxian else f'{year}年'
    star_str = '、'.join(star_list) if star_list else '空宮'

    if score >= 80:
        level = '旺'
        prefix = '運勢極佳，'
    elif score >= 65:
        level = '吉'
        prefix = '運勢不錯，'
    elif score >= 50:
        level = '平'
        prefix = '運勢平穩，'
    else:
        level = '需謹慎'
        prefix = '運勢需注意，'

    aspect_advice = {
        '財運':    {
            '旺': '財源廣進，投資理財可積極把握機遇，正財偏財皆有收穫。',
            '吉': '收入穩定增長，適合拓展業務或開創新財路。',
            '平': '財務持平，宜節流為主，避免大筆投資風險。',
            '需謹慎': '財運有阻，謹防破財及借貸糾紛，量入為出。',
        },
        '事業':    {
            '旺': '事業飛躍，有晉升或創業良機，貴人相助，可大展鴻圖。',
            '吉': '工作發展順利，能力受到肯定，適合積極爭取機會。',
            '平': '工作穩定，循規蹈矩，守成較易，大突破需等待時機。',
            '需謹慎': '事業有波折，謹防小人阻礙，低調行事為宜。',
        },
        '感情家庭': {
            '旺': '感情美滿，家庭和諧，適合論及婚嫁或迎接新成員。',
            '吉': '感情進展順利，家人關係融洽，適合共同計劃未來。',
            '平': '感情平淡中帶溫馨，多體貼溝通，可增進感情。',
            '需謹慎': '感情易生口角，家庭需多包容，避免衝動決策。',
        },
        '人際朋友': {
            '旺': '人緣極佳，貴人頻現，社交活躍，合作事業皆宜。',
            '吉': '朋友助力多，善加利用人脈，合作順利。',
            '平': '朋友緣一般，宜真誠待人，慢慢累積人脈。',
            '需謹慎': '人際是非多，謹慎交友，避免口舌糾紛。',
        },
        '健康':    {
            '旺': '精力充沛，身體狀況佳，是運動健身的好時機。',
            '吉': '健康狀況良好，注意規律作息即可維持佳態。',
            '平': '健康平穩，注意飲食及休息，勿過度操勞。',
            '需謹慎': '健康需注意，宜定期健檢，避免積勞成疾。',
        },
    }

    advice = aspect_advice.get(aspect, {}).get(level, '')
    star_info = f'（宮內星曜：{star_str}）' if star_list else '（空宮，受鄰宮影響）'
    return f'{prefix}{advice}{star_info}'

# ── 命盤總體說明 ──────────────────────────────────
def generate_chart_summary(palaces: list, daxian: dict, ju_name: str, ganzhi: str) -> list:
    """回傳命盤總體說明段落 list"""
    items = []

    # 命宮
    ming_p = palaces[0]
    ming_main = [s for s in ming_p['stars'] if s in STAR_TRAIT]
    if ming_main:
        star = ming_main[0]
        title, desc = STAR_TRAIT[star]
        items.append(('命宮', f'坐 {star}（{title}），{desc}。'))
    else:
        items.append(('命宮', '空宮，個性靈活多變，善於適應環境，容易受外在環境影響而調整自我方向。'))

    # 財帛宮（index 4）
    cai_p = palaces[4]
    cai_main = [s for s in cai_p['stars'] if s in STAR_TRAIT]
    if cai_main:
        star = cai_main[0]
        title, desc = STAR_TRAIT[star]
        items.append(('財帛', f'{star}（{title}）坐財帛宮，{desc}，財運有穩定根基。'))
    else:
        items.append(('財帛', '財帛宮空宮，財來財去，宜積極開源節流，穩健理財為上。'))

    # 事業宮（index 8）
    ye_p = palaces[8]
    ye_main = [s for s in ye_p['stars'] if s in STAR_TRAIT]
    if ye_main:
        star = ye_main[0]
        title, desc = STAR_TRAIT[star]
        items.append(('事業', f'{star}（{title}）居事業宮，{desc}，事業具有明確發展方向。'))
    else:
        items.append(('事業', '事業宮空宮，職涯選擇廣泛多元，宜藉由大限流年尋找最佳發展契機。'))

    # 夫妻宮（index 2）
    fu_p = palaces[2]
    fu_main = [s for s in fu_p['stars'] if s in STAR_TRAIT]
    if fu_main:
        star = fu_main[0]
        title, desc = STAR_TRAIT[star]
        items.append(('感情', f'{star}（{title}）坐夫妻宮，{desc}，感情與婚姻緣份具此特質。'))
    else:
        items.append(('感情', '夫妻宮空宮，感情宜主動把握，緣份需靠自身積極經營。'))

    # 福德宮（index 10）
    fu_de_p = palaces[10]
    fude_main = [s for s in fu_de_p['stars'] if s in STAR_TRAIT]
    if fude_main:
        star = fude_main[0]
        title, desc = STAR_TRAIT[star]
        items.append(('福德', f'{star}（{title}）居福德宮，{desc}，精神生活與福份較為豐厚。'))
    else:
        items.append(('福德', '福德宮空宮，精神面宜多修身養性，培養興趣，方能增添生活福氣。'))

    # 大限
    dx = daxian
    palace_trait = PALACE_TRAIT.get(dx['palace_name'], '運勢變動')
    items.append(('大限', f'目前行至{dx["palace_name"]}大限（{dx["start_age"]}～{dx["end_age"]}歲），此限主「{palace_trait}」，宜把握此段時期的機遇，順勢而為。'))

    # 整體
    items.append(('整體', f'命主{ju_name}，{ganzhi}生，整體命格依此架構推算。流年吉凶需配合大限宮位與流年星曜共同研判，方能全面掌握運勢起伏。'))

    return items


# ── 流年詳細建議 ──────────────────────────────────
DETAILED_ADVICE = {
    '財運': {
        '旺': '財源廣進，正偏財皆旺。適合投資理財、洽談合約、開拓業務，機遇須快速把握。注意守財，避免衝動消費造成浪費。',
        '吉': '財運順暢，收入穩定成長。可小幅擴展投資或業務，謹慎評估後可積極行動。',
        '平': '財運持平，宜以守為攻。避免大筆投資或借貸，穩健理財、量入為出為上策。',
        '需謹慎': '財運有礙，慎防破財耗損。不宜投資高風險項目，留意借貸及詐騙糾紛，宜節流為主。',
    },
    '事業': {
        '旺': '事業蒸蒸日上，升遷加薪或創業機遇皆現。貴人相助力強，主動積極爭取必有所成。',
        '吉': '工作表現受肯定，發展穩健向前。可積極爭取新機會，把握合作夥伴關係與資源。',
        '平': '工作維持穩定，暫無大突破。守成為要，踏實累積實力，靜候更佳發展時機。',
        '需謹慎': '事業易有波折，防小人阻礙及職場是非。低調行事，不宜輕易換工作或貿然創業。',
    },
    '感情家庭': {
        '旺': '感情桃花旺盛，單身者易覓良緣，有伴者感情升溫、家庭和諧美滿。適合規劃人生大事。',
        '吉': '感情順利進展，家庭溫暖融洽。適合計劃婚姻、同居或生育，感情基礎穩固。',
        '平': '感情平淡，需主動維繫關係。多陪伴、多溝通、多體貼，可增進感情深度與溫度。',
        '需謹慎': '感情易起波折或口角，家庭需多包容忍讓。避免衝動決策影響長期關係的穩定。',
    },
    '人際朋友': {
        '旺': '人脈廣闊，貴人頻至。適合社交活動、拓展合作、參與社群，人際關係一切順暢。',
        '吉': '人際關係良好，朋友支持力強。善用人脈資源，合作項目容易推進並獲得成功。',
        '平': '人際普通，需主動維繫友誼。真誠待人、廣結善緣，慢慢累積可信賴的人脈基礎。',
        '需謹慎': '人際是非較多，謹防小人背刺。慎重交友，不輕易透露個人計劃與機密事務。',
    },
    '健康': {
        '旺': '精力充沛，身心狀態極佳。適合運動健身、戶外探索，整體能量旺盛，充分把握。',
        '吉': '健康良好，體力充足穩定。保持規律作息與適度運動，輕鬆維持良好身心狀態。',
        '平': '健康普通，需注意日常保養。避免過度勞累，飲食均衡、睡眠充足，定期健康檢查。',
        '需謹慎': '健康需格外留意，小心慢性病或意外傷害。宜積極休養、定期健檢，切勿拖延就醫。',
    },
}

def generate_liunian_overall(avg_score: int, daxian_name: str,
                              yr_stem: str, yr_branch: str, age: int) -> str:
    if avg_score >= 75:
        level_text = '整體運勢旺盛'
        main = '本年天時地利人和，是把握機遇、積極進取的好年份。各方面皆有良好發展，宜主動出擊，大膽追求目標，切勿錯失良機。'
    elif avg_score >= 60:
        level_text = '整體運勢偏吉'
        main = '本年運勢平穩向好，各方面皆有穩定進展。適合按部就班推進計劃，貴人適時出現，善加把握即可有所作為。'
    elif avg_score >= 45:
        level_text = '整體運勢平穩'
        main = '本年運勢中平，大起大落較少。宜守成為主，踏實累積實力，不宜輕舉妄動或做重大決策，耐心等待更佳時機。'
    else:
        level_text = '整體運勢需謹慎'
        main = '本年諸事易有阻礙，需格外謹慎小心。低調行事，避免重大決策與高風險行動，做好風險管控，靜待運勢轉機。'

    palace_trait = PALACE_TRAIT.get(daxian_name, '運勢變動')
    daxian_note = f'目前大限行至「{daxian_name}」（主「{palace_trait}」），流年運勢需結合大限宮位一併研判，方能全面掌握。'

    return f'【{level_text}】{main}　{daxian_note}'


# ── 主入口 ──────────────────────────────────────
def _compute_base(birth_year: int, birth_month: int, birth_day: int,
                  birth_hour: int, gender: str) -> dict:
    lunar_year, lunar_month, lunar_day, is_leap = solar_to_lunar(birth_year, birth_month, birth_day)
    y_stem_idx, y_branch_idx, y_stem, y_branch = get_year_ganzhi(birth_year)
    h_branch_idx, h_branch = get_hour_branch(birth_hour)
    ming_branch = get_ming_palace(lunar_month, h_branch_idx)
    shen_branch = get_shen_palace(lunar_month, h_branch_idx)
    ju = get_wuxing_ju(y_stem_idx, ming_branch)
    ziwei_branch = get_ziwei_position(lunar_day, ju)
    tianfu_branch = get_tianfu_position(ziwei_branch)
    all_stars = place_all_stars(ziwei_branch, tianfu_branch,
                                lunar_month, h_branch_idx,
                                y_stem_idx, y_branch_idx)
    direction = get_daxian_direction(y_stem_idx, gender)

    palaces = []
    for i, pname in enumerate(PALACE_NAMES):
        branch_idx = (ming_branch + i) % 12
        p_stars = [s for s, b in all_stars.items() if b == branch_idx]
        palaces.append({
            'name': pname,
            'branch': DI_ZHI[branch_idx],
            'branch_idx': branch_idx,
            'stars': p_stars,
            'is_ming': (i == 0),
            'is_shen': (branch_idx == shen_branch),
        })

    return {
        'lunar_year': lunar_year, 'lunar_month': lunar_month,
        'lunar_day': lunar_day,   'is_leap': is_leap,
        'y_stem_idx': y_stem_idx, 'y_branch_idx': y_branch_idx,
        'y_stem': y_stem,         'y_branch': y_branch,
        'h_branch_idx': h_branch_idx, 'h_branch': h_branch,
        'ming_branch': ming_branch,   'shen_branch': shen_branch,
        'ju': ju,
        'ziwei_branch': ziwei_branch, 'tianfu_branch': tianfu_branch,
        'all_stars': all_stars,       'palaces': palaces,
        'direction': direction,
    }


def generate_ziwei_chart(birth_year: int, birth_month: int, birth_day: int,
                         birth_hour: int, gender: str) -> dict:
    base = _compute_base(birth_year, birth_month, birth_day, birth_hour, gender)

    lunar_year   = base['lunar_year'];  lunar_month = base['lunar_month']
    lunar_day    = base['lunar_day'];   is_leap     = base['is_leap']
    y_stem_idx   = base['y_stem_idx'];  y_branch_idx= base['y_branch_idx']
    y_stem       = base['y_stem'];      y_branch    = base['y_branch']
    h_branch     = base['h_branch']
    ming_branch  = base['ming_branch']; shen_branch = base['shen_branch']
    ju           = base['ju']
    ziwei_branch = base['ziwei_branch']; tianfu_branch = base['tianfu_branch']
    all_stars    = base['all_stars'];   palaces     = base['palaces']
    direction    = base['direction']

    current_age = date.today().year - birth_year
    daxian_branch, dx_start, dx_end, _ = get_current_daxian(
        ming_branch, ju, current_age, direction)
    daxian_palace = DI_ZHI[daxian_branch]
    daxian_palace_name = PALACE_NAMES[(daxian_branch - ming_branch + 12) % 12]

    return {
        'input': {
            'birth': f'{birth_year}/{birth_month:02d}/{birth_day:02d}',
            'hour': birth_hour,
            'hour_branch': h_branch,
            'gender': gender,
        },
        'lunar': {
            'year': lunar_year,
            'month': lunar_month,
            'day': lunar_day,
            'is_leap': is_leap,
        },
        'ganzhi': f'{y_stem}{y_branch}年',
        'ming_branch': DI_ZHI[ming_branch],
        'shen_branch': DI_ZHI[shen_branch],
        'ju': ju,
        'ju_name': JU_NAME[ju],
        'ziwei_branch': DI_ZHI[ziwei_branch],
        'tianfu_branch': DI_ZHI[tianfu_branch],
        'palaces': palaces,
        'all_stars': {k: DI_ZHI[v] for k, v in all_stars.items()},
        'daxian': {
            'palace': daxian_palace,
            'palace_name': daxian_palace_name,
            'start_age': dx_start,
            'end_age': dx_end,
            'current_age': current_age,
        },
        'has_lunardate': HAS_LUNARDATE,
        'chart_summary': generate_chart_summary(palaces, {
            'palace_name': daxian_palace_name,
            'start_age': dx_start,
            'end_age': dx_end,
        }, JU_NAME[ju], f'{y_stem}{y_branch}年'),
    }


def calculate_liunian(birth_year: int, birth_month: int, birth_day: int,
                      birth_hour: int, gender: str, liunian_year: int) -> dict:
    base = _compute_base(birth_year, birth_month, birth_day, birth_hour, gender)

    ming_branch = base['ming_branch']
    all_stars   = base['all_stars']
    ju          = base['ju']
    direction   = base['direction']

    yr_age = liunian_year - birth_year
    liunian_ming = get_liunian_palace(liunian_year, ming_branch)
    yr_dx_branch, dx_start, dx_end, _ = get_current_daxian(
        ming_branch, ju, yr_age, direction)
    daxian_palace_name = PALACE_NAMES[(yr_dx_branch - ming_branch + 12) % 12]

    yr_stem   = TIAN_GAN[(liunian_year - 4) % 10]
    yr_branch = DI_ZHI[(liunian_year - 4) % 12]

    aspects = {}
    total_score = 0
    for aspect, palace_target in ASPECT_PALACES.items():
        target_branch = palace_offset(liunian_ming, palace_target)
        s_list   = stars_in_palace(all_stars, target_branch)
        dx_stars = stars_in_palace(all_stars, yr_dx_branch)
        combined = list(set(s_list + dx_stars))[:4]
        sc, _    = rate_palace(combined)

        if sc >= 80:   level = '旺'
        elif sc >= 65: level = '吉'
        elif sc >= 50: level = '平'
        else:          level = '需謹慎'

        text   = generate_fortune_text(aspect, liunian_year, palace_target, combined, sc, False)
        detail = DETAILED_ADVICE.get(aspect, {}).get(level, '')

        aspects[aspect] = {
            'score':  sc,
            'level':  level,
            'text':   text,
            'detail': detail,
            'stars':  combined,
            'palace': palace_target,
        }
        total_score += sc

    avg_score   = total_score // len(aspects)
    overall_text = generate_liunian_overall(avg_score, daxian_palace_name,
                                            yr_stem, yr_branch, yr_age)

    return {
        'year':               liunian_year,
        'age':                yr_age,
        'ganzhi':             f'{yr_stem}{yr_branch}年',
        'liunian_ming':       DI_ZHI[liunian_ming],
        'daxian_palace_name': daxian_palace_name,
        'daxian_start':       dx_start,
        'daxian_end':         dx_end,
        'aspects':            aspects,
        'overall_score':      avg_score,
        'overall_text':       overall_text,
        'fan_taisui':         check_fan_taisui(birth_year, liunian_year),
    }
