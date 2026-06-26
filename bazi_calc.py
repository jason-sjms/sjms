from datetime import date

TIAN_GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI   = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

GAN_WX   = ['木','木','火','火','土','土','金','金','水','水']
ZHI_WX   = ['水','土','木','木','土','火','火','土','金','金','土','水']
GAN_YY   = [True,False,True,False,True,False,True,False,True,False]

# 納音：甲子=0 起，60甲子每對名稱（每兩個相同）
NAYIN_NAME = [
    '海中金','海中金','爐中火','爐中火','大林木','大林木',
    '路旁土','路旁土','劍鋒金','劍鋒金','山頭火','山頭火',
    '澗下水','澗下水','城頭土','城頭土','白蠟金','白蠟金',
    '楊柳木','楊柳木','泉中水','泉中水','屋上土','屋上土',
    '霹靂火','霹靂火','松柏木','松柏木','長流水','長流水',
    '沙中金','沙中金','山下火','山下火','平地木','平地木',
    '壁上土','壁上土','金箔金','金箔金','覆燈火','覆燈火',
    '天河水','天河水','大驛土','大驛土','釵釧金','釵釧金',
    '桑柘木','桑柘木','大溪水','大溪水','沙中土','沙中土',
    '天上火','天上火','石榴木','石榴木','大海水','大海水',
]
NAYIN_WX = [
    '金','金','火','火','木','木','土','土','金','金','火','火',
    '水','水','土','土','金','金','木','木','水','水','土','土',
    '火','火','木','木','水','水','金','金','火','火','木','木',
    '土','土','金','金','火','火','水','水','土','土','金','金',
    '木','木','水','水','土','土','火','火','木','木','水','水',
]

# 地支藏干（stem indices）
ZHI_HIDDEN = {
    0:[9], 1:[5,9,7], 2:[0,2,4], 3:[1], 4:[4,1,9], 5:[2,6,4],
    6:[3,5], 7:[5,3,1], 8:[6,8,4], 9:[7], 10:[4,7,3], 11:[8,0],
}

WX_RELATIONS = {
    '木':{'produces':'火','controls':'土','produced_by':'水','controlled_by':'金'},
    '火':{'produces':'土','controls':'金','produced_by':'木','controlled_by':'水'},
    '土':{'produces':'金','controls':'水','produced_by':'火','controlled_by':'木'},
    '金':{'produces':'水','controls':'木','produced_by':'土','controlled_by':'火'},
    '水':{'produces':'木','controls':'火','produced_by':'金','controlled_by':'土'},
}

# 月令旺衰加成（月支 → 各五行偏移分）
MONTH_SEASON = {
    2:{'木':2,'火':1,'水':-1,'金':-2,'土':0},
    3:{'木':3,'火':1,'水':-1,'金':-2,'土':-1},
    4:{'土':1,'木':1,'火':1,'金':-1,'水':-2},
    5:{'火':2,'土':1,'木':-1,'水':-2,'金':-1},
    6:{'火':3,'土':1,'木':-1,'水':-2,'金':-2},
    7:{'土':2,'火':1,'金':0,'木':-2,'水':-1},
    8:{'金':2,'土':1,'火':-1,'木':-2,'水':0},
    9:{'金':3,'土':0,'火':-2,'木':-2,'水':1},
    10:{'土':1,'金':1,'水':1,'火':-1,'木':-2},
    11:{'水':2,'金':1,'土':-1,'火':-2,'木':-1},
    0:{'水':3,'金':1,'土':-2,'火':-2,'木':-1},
    1:{'土':1,'水':1,'木':0,'火':-1,'金':-1},
}

# 12 節（定月界）：(陽曆月, 近似日基數, 節名, 對應月支index)
JIE_CONSTANTS = [
    (1,  5.4055, '小寒', 1),
    (2,  3.87,   '立春', 2),
    (3,  5.63,   '驚蟄', 3),
    (4,  4.81,   '清明', 4),
    (5,  5.52,   '立夏', 5),
    (6,  5.678,  '芒種', 6),
    (7,  7.108,  '小暑', 7),
    (8,  7.5,    '立秋', 8),
    (9,  7.646,  '白露', 9),
    (10, 7.9,    '寒露', 10),
    (11, 7.438,  '立冬', 11),
    (12, 7.18,   '大雪', 0),
]

def _jie_day(year, C):
    y = year - 1900
    return int(C + 0.242194 * y) - (y // 4)

def _all_jie_dates(years):
    result = []
    for y in years:
        for cal_m, C, name, branch in JIE_CONSTANTS:
            try:
                d = _jie_day(y, C)
                result.append((date(y, cal_m, d), branch, name))
            except ValueError:
                pass
    result.sort(key=lambda x: x[0])
    return result

def get_bazi_year_month(birth_date):
    y = birth_date.year
    lichun_day = _jie_day(y, 3.87)
    lichun = date(y, 2, lichun_day)
    bazi_year = y if birth_date >= lichun else y - 1

    jie_list = _all_jie_dates([y - 1, y, y + 1])

    month_branch, month_jie = 1, '小寒'
    for jd, branch, name in jie_list:
        if jd <= birth_date:
            month_branch, month_jie = branch, name
        else:
            break

    near_jie = any(abs((birth_date - jd).days) <= 2 for jd, _, _ in jie_list)
    return bazi_year, month_branch, month_jie, near_jie

def get_day_ganzhi(birth_date):
    delta = (birth_date - date(1900, 1, 1)).days  # 1900/1/1 = 甲戌
    return delta % 10, (delta + 10) % 12

def get_hour_branch(hour):
    for s, e, b in [(23,24,0),(0,1,0),(1,3,1),(3,5,2),(5,7,3),(7,9,4),
                    (9,11,5),(11,13,6),(13,15,7),(15,17,8),(17,19,9),(19,21,10),(21,23,11)]:
        if s <= hour < e:
            return b
    return 0

def get_month_stem(year_stem_idx, month_branch_idx):
    """五虎遁年起月法"""
    yin_stem = [2, 4, 6, 8, 0][year_stem_idx % 5]
    return (yin_stem + (month_branch_idx - 2 + 12) % 12) % 10

def get_hour_stem(day_stem_idx, hour_branch_idx):
    """五鼠遁日起時法"""
    zi_stem = [0, 2, 4, 6, 8][day_stem_idx % 5]
    return (zi_stem + hour_branch_idx) % 10

def nayin(stem_idx, branch_idx):
    n = (6 * stem_idx - 5 * branch_idx) % 60
    return NAYIN_NAME[n], NAYIN_WX[n]

def shi_shen(day_stem_idx, other_stem_idx):
    """十神關係（日主對他干）"""
    dm_wx = GAN_WX[day_stem_idx]
    dm_yy = GAN_YY[day_stem_idx]
    ot_wx = GAN_WX[other_stem_idx]
    ot_yy = GAN_YY[other_stem_idx]
    same = (dm_yy == ot_yy)
    rel = WX_RELATIONS[dm_wx]
    if ot_wx == dm_wx:        return '比肩' if same else '劫財'
    if rel['produces'] == ot_wx:  return '食神' if same else '傷官'
    if rel['controls'] == ot_wx:  return '偏財' if same else '正財'
    if rel['controlled_by'] == ot_wx: return '七殺' if same else '正官'
    if rel['produced_by'] == ot_wx:   return '偏印' if same else '正印'
    return ''

def calc_wx_scores(year_s, year_b, month_s, month_b, day_s, day_b, hour_s, hour_b):
    scores = {wx: 0.0 for wx in '木火土金水'}
    def add(s_idx, b_idx, s_w, b_w):
        scores[GAN_WX[s_idx]] += s_w
        scores[ZHI_WX[b_idx]] += b_w
        for h in ZHI_HIDDEN.get(b_idx, []):
            scores[GAN_WX[h]] += 0.4
    add(year_s,  year_b,  1.0, 1.0)
    add(month_s, month_b, 1.0, 1.5)  # 月令最重
    add(day_s,   day_b,   1.0, 1.0)
    add(hour_s,  hour_b,  1.0, 1.0)
    return scores

def assess_strength(day_stem_idx, month_branch_idx, wx_scores):
    dm_wx = GAN_WX[day_stem_idx]
    rel   = WX_RELATIONS[dm_wx]
    raw   = wx_scores[dm_wx]
    raw  += wx_scores[rel['produced_by']] * 0.8
    raw  -= wx_scores[rel['controlled_by']] * 0.6
    raw  -= wx_scores[rel['produces']] * 0.3
    season = MONTH_SEASON.get(month_branch_idx, {})
    raw  += season.get(dm_wx, 0) * 1.5
    score = max(0, min(100, int(50 + raw * 4)))
    label = '身強' if score >= 65 else '身弱' if score <= 42 else '身中'
    return score, label

def get_yong_shen(day_stem_idx, strength_label):
    dm_wx = GAN_WX[day_stem_idx]
    rel   = WX_RELATIONS[dm_wx]
    if strength_label == '身強':
        xi = [rel['produces'], rel['controls'], rel['controlled_by']]
        ji = [dm_wx, rel['produced_by']]
        exp = f'日主{dm_wx}旺，宜{xi[0]}（食傷）洩秀、{xi[1]}（財）生活，或{xi[2]}（官殺）制衡，忌再補{ji[0]}/{ji[1]}（比劫/印）。'
    elif strength_label == '身弱':
        xi = [rel['produced_by'], dm_wx]
        ji = [rel['controlled_by'], rel['produces']]
        exp = f'日主{dm_wx}弱，喜{xi[0]}（印）生扶、{xi[1]}（比劫）助身，忌{ji[0]}（官殺）剋制與{ji[1]}（食傷）洩氣。'
    else:
        xi = [rel['produces'], rel['produced_by']]
        ji = [rel['controlled_by']]
        exp = f'日主{dm_wx}中和，命格較平衡，喜{xi[0]}（食傷）發秀、{xi[1]}（印）護主，忌{ji[0]}過重剋身。'
    return xi[:2], ji[:2], exp

def get_dayun_start(birth_date, bazi_year_stem_idx, gender, month_branch_idx):
    yang_year = (bazi_year_stem_idx % 2 == 0)
    male      = (gender == '男')
    forward   = (yang_year == male)

    jie_list = _all_jie_dates([birth_date.year - 1, birth_date.year, birth_date.year + 1])

    days = 90
    if forward:
        for jd, _, _ in jie_list:
            if jd > birth_date:
                days = (jd - birth_date).days
                break
    else:
        prev = None
        for jd, _, _ in jie_list:
            if jd < birth_date:
                prev = jd
            else:
                break
        if prev:
            days = (birth_date - prev).days

    start_y = days // 3
    start_m = (days % 3) * 4
    return start_y, start_m, forward

def get_dayun_list(month_stem_idx, month_branch_idx, forward, start_y, start_m, day_stem_idx, count=8):
    result = []
    for i in range(1, count + 1):
        if forward:
            s = (month_stem_idx + i) % 10
            b = (month_branch_idx + i) % 12
        else:
            s = (month_stem_idx - i + 10) % 10
            b = (month_branch_idx - i + 12) % 12
        ny, nm = NAYIN_NAME[(6*s - 5*b) % 60], NAYIN_WX[(6*s - 5*b) % 60]
        age_s = start_y + (i - 1) * 10
        result.append({
            'ganzhi':    TIAN_GAN[s] + DI_ZHI[b],
            'stem':      TIAN_GAN[s],
            'branch':    DI_ZHI[b],
            'stem_wx':   GAN_WX[s],
            'branch_wx': ZHI_WX[b],
            'nayin':     ny,
            'nayin_wx':  nm,
            'shi_shen':  shi_shen(day_stem_idx, s),
            'age_start': age_s,
            'age_end':   age_s + 9,
        })
    return result


# ── 日主性格描述 ──────────────────────────────────
DM_PERSONALITY = {
    '甲': ('大林木', '性格正直剛毅，具有強烈的上進心與領導氣質，如大樹般頂天立地。重視原則，不輕易妥協，適合開創事業。但有時過於固執，需學習彈性應變。'),
    '乙': ('花草木', '個性溫柔細膩、善於溝通，有藝術品味，懂得藉助外力達成目標。人際關係良好，適合走公關、文創、服務業。惟有時缺乏主見，需培養決斷力。'),
    '丙': ('太陽火', '熱情開朗、充滿活力，具有感召力，如太陽一般照亮四周。樂於分享，社交活躍，適合公眾事業、教育、娛樂行業。需注意衝動和過度自信。'),
    '丁': ('燈燭火', '細心敏銳、感情豐富，有獨特的藝術直覺。思考縝密，擅長深度溝通，適合文學、心理、醫療輔導。在壓力下易情緒波動，需保持內心平靜。'),
    '戊': ('高山土', '個性穩重踏實、可靠誠信，如大山一般厚德載物。具有高度責任感，善於管理與守護，適合行政、金融、不動產。需避免過度保守而錯失機遇。'),
    '己': ('田園土', '謙遜包容、心思細膩，善於照顧他人。具有親和力，適合服務業、醫療、教育。有時過於顧慮他人感受，容易委曲求全，需建立自我主張。'),
    '庚': ('刀劍金', '個性剛強果決、執行力強，做事雷厲風行。具有競爭意識和挑戰精神，適合軍警、法律、工程、商業談判。需注意過於強硬而傷和氣。'),
    '辛': ('珠寶金', '重視品質與美感，有高雅的審美眼光，追求完美。敏感細膩，具有鑑別力，適合珠寶、設計、精品、財務管理。需避免因求完美而患得患失。'),
    '壬': ('大海水', '思維廣博、適應力強，如大海般包容萬物。具有戰略眼光，善於整合資源，適合貿易、外交、策劃。有時過於理想化，需落實執行力。'),
    '癸': ('雨露水', '直覺敏銳、富有同理心，善於感知他人情緒。具有滋養與柔韌的特質，適合諮詢、藝術、心靈成長領域。需注意情緒化和過度敏感的傾向。'),
}

# 十神代表意涵（在各柱位的解讀）
SS_MEANING = {
    '比肩': {'財': '財運較為獨立，不易借助他人之力', '事業': '工作競爭力強，宜自主創業', '感情': '感情上較為獨立，需主動經營'},
    '劫財': {'財': '財來財去，易有破財，需謹慎理財', '事業': '競爭激烈，提防合夥糾紛', '感情': '感情多波折，需包容互讓'},
    '食神': {'財': '偏財旺，有才藝帶財的機遇', '事業': '適合文創、技術、餐飲等發揮才藝', '感情': '感情溫馨，有口福與生活品味'},
    '傷官': {'財': '財路廣，但財來財去', '事業': '才氣出眾，適合藝術創作、顧問', '感情': '感情細膩但易有衝突，婚姻需磨合'},
    '偏財': {'財': '偏財旺，善於投機與商業', '事業': '靈活多變，善把握機遇', '感情': '桃花較旺，感情生活豐富'},
    '正財': {'財': '正財穩健，適合穩定理財', '事業': '踏實努力，收入穩定', '感情': '感情忠誠，家庭觀念強'},
    '七殺': {'財': '財運有阻，需防小人破財', '事業': '有衝勁，適合競爭激烈行業', '感情': '感情強烈，易有衝突，需包容'},
    '正官': {'財': '正當財路，宜走正規途徑', '事業': '適合公職或大企業，穩步晉升', '感情': '感情正統，婚姻穩定'},
    '偏印': {'財': '財運易受阻，需多方嘗試', '事業': '適合學術、研究、特殊技藝', '感情': '感情較為內斂，需主動表達'},
    '正印': {'財': '財運平穩，有貴人助', '事業': '適合教育、文化、公益', '感情': '感情細膩，重視精神交流'},
}

def generate_bazi_summary(pillars, day_master_stem, day_master_wx, strength_label,
                           xi_list, ji_list, gender, bazi_year_stem_idx):
    items = []

    # 1. 日主性格
    name, desc = DM_PERSONALITY.get(day_master_stem, ('', '個性多元，需綜合全局判斷。'))
    yang_str = '陽' if GAN_YY[TIAN_GAN.index(day_master_stem)] else '陰'
    items.append(('日主性格', f'日主{day_master_stem}（{name}），屬{yang_str}{day_master_wx}。{desc}'))

    # 2. 月柱（環境與父母）
    m = pillars['month']
    ss_m = m.get('shi_shen', '')
    m_meaning = SS_MEANING.get(ss_m, {})
    items.append(('月柱環境', f'月柱{m["ganzhi"]}（{m["nayin"]}），月干為「{ss_m}」。'
                  f'月柱代表成長環境與父母。{m_meaning.get("事業","月令為命格強弱的關鍵，影響日主的力量與發展方向。")}'))

    # 3. 年柱（祖上與童年）
    y = pillars['year']
    ss_y = y.get('shi_shen', '')
    items.append(('年柱祖蔭', f'年柱{y["ganzhi"]}（{y["nayin"]}），天干為「{ss_y}」。'
                  f'年柱反映祖先庇蔭與童年環境。'
                  + ('有長輩或貴人蔭護，根基穩固。' if ss_y in ('正印','偏印','正官','正財') else
                     '早年環境較多變動，靠自身努力開創。')))

    # 4. 時柱（晚年與子息）
    h = pillars['hour']
    ss_h = h.get('shi_shen', '')
    items.append(('時柱晚運', f'時柱{h["ganzhi"]}（{h["nayin"]}），天干為「{ss_h}」。'
                  f'時柱主晚年運勢與子女緣。'
                  + ('晚年運佳，子女孝順，晚景安康。' if ss_h in ('食神','正財','正官','正印') else
                     '晚年宜及早規劃，子女緣需用心經營。')))

    # 5. 強弱與命格方向
    wx_xi = '、'.join(xi_list)
    wx_ji = '、'.join(ji_list) if ji_list else '無特定忌神'
    if strength_label == '身強':
        direction = (f'命主日主旺盛，精力充沛、意志力強，適合走創業、競爭型路線。'
                     f'喜{wx_xi}洩秀生財，行業以能發揮才能的領域為宜。'
                     f'忌{wx_ji}再補，避免過剛易折。')
    elif strength_label == '身弱':
        direction = (f'命主日主偏弱，行事宜借助貴人之力，善用團隊合作。'
                     f'喜{wx_xi}生扶，適合穩健發展的職涯，循序漸進累積實力。'
                     f'忌{wx_ji}剋洩，需避免過度耗散精力。')
    else:
        direction = (f'命主日主中和，命格平衡，適應力強，各行業皆有發展空間。'
                     f'喜{wx_xi}調候，行事靈活，宜把握流年大運的契機發力。')
    items.append(('命格方向', direction))

    # 6. 喜用五行對應行業
    WX_CAREER = {
        '木': '文教、出版、林業、設計、成長型企業',
        '火': '科技、能源、媒體、娛樂、餐飲、照明',
        '土': '不動產、農業、建築、倉儲、仲介、政府',
        '金': '金融、法律、機械、珠寶、軍警、製造',
        '水': '貿易、物流、旅遊、諮詢、水利、哲學',
    }
    career_list = '、'.join(WX_CAREER.get(wx, '') for wx in xi_list if wx in WX_CAREER)
    if career_list:
        items.append(('適合行業', f'喜用神為{wx_xi}，對應行業：{career_list}。選擇與喜用五行相符的職業或居住環境，有助提升整體運勢。'))

    return items


def calculate_bazi(birth_year, birth_month, birth_day, birth_hour, gender):
    birth_date = date(birth_year, birth_month, birth_day)

    bazi_year, month_branch, month_jie, near_jie = get_bazi_year_month(birth_date)

    # 年柱
    y_stem  = (bazi_year - 4) % 10
    y_branch = (bazi_year - 4) % 12

    # 月柱
    m_stem  = get_month_stem(y_stem, month_branch)
    m_branch = month_branch

    # 日柱
    d_stem, d_branch = get_day_ganzhi(birth_date)

    # 時柱
    h_branch = get_hour_branch(birth_hour)
    h_stem   = get_hour_stem(d_stem, h_branch)

    def pillar(s, b, pos=None):
        ny_name, ny_wx = nayin(s, b)
        p = {
            'stem':      TIAN_GAN[s],
            'branch':    DI_ZHI[b],
            'stem_idx':  s,
            'branch_idx':b,
            'ganzhi':    TIAN_GAN[s] + DI_ZHI[b],
            'stem_wx':   GAN_WX[s],
            'branch_wx': ZHI_WX[b],
            'nayin':     ny_name,
            'nayin_wx':  ny_wx,
            'hidden':    [TIAN_GAN[h] for h in ZHI_HIDDEN.get(b, [])],
        }
        if pos and pos != 'day':
            p['shi_shen'] = shi_shen(d_stem, s)
            p['hidden_ss'] = [shi_shen(d_stem, h) for h in ZHI_HIDDEN.get(b, [])]
        return p

    pillars = {
        'year':  pillar(y_stem, y_branch, 'year'),
        'month': pillar(m_stem, m_branch, 'month'),
        'day':   pillar(d_stem, d_branch, 'day'),
        'hour':  pillar(h_stem, h_branch, 'hour'),
    }

    wx_scores = calc_wx_scores(y_stem, y_branch, m_stem, m_branch, d_stem, d_branch, h_stem, h_branch)
    strength_score, strength_label = assess_strength(d_stem, m_branch, wx_scores)
    xi, ji, yong_exp = get_yong_shen(d_stem, strength_label)

    dy_start_y, dy_start_m, forward = get_dayun_start(birth_date, y_stem, gender, m_branch)
    dayuns = get_dayun_list(m_stem, m_branch, forward, dy_start_y, dy_start_m, d_stem)

    # 目前大運
    today_age = date.today().year - birth_year
    current_dy = None
    for dy in dayuns:
        if dy['age_start'] <= today_age <= dy['age_end']:
            current_dy = dy
            break

    summary = generate_bazi_summary(
        pillars, TIAN_GAN[d_stem], GAN_WX[d_stem], strength_label,
        xi, ji, gender, y_stem)

    return {
        'pillars':        pillars,
        'day_master':     {'stem': TIAN_GAN[d_stem], 'element': GAN_WX[d_stem], 'yang': GAN_YY[d_stem]},
        'wx_scores':      {k: round(v, 1) for k, v in wx_scores.items()},
        'strength':       {'score': strength_score, 'label': strength_label},
        'yong_shen':      {'xi': xi, 'ji': ji, 'explanation': yong_exp},
        'dayun':          dayuns,
        'dayun_start':    {'year': dy_start_y, 'month': dy_start_m, 'forward': forward},
        'current_dayun':  current_dy,
        'bazi_year':      bazi_year,
        'month_jie':      month_jie,
        'near_jie_warning': near_jie,
        'summary':        summary,
    }
