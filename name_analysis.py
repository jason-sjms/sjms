from stroke_data import get_stroke_count

# 數字對應五行
def number_to_wuxing(n: int) -> str:
    digit = n % 10
    if digit in (1, 2): return '木'
    if digit in (3, 4): return '火'
    if digit in (5, 6): return '土'
    if digit in (7, 8): return '金'
    return '水'  # 0, 9

WUXING_COLOR = {'木': '#2ecc71', '火': '#e74c3c', '土': '#f39c12', '金': '#f1c40f', '水': '#3498db'}
WUXING_TRAITS = {
    '木': '仁慈、積極、有創造力、喜歡成長',
    '火': '熱情、有魅力、領導力強、積極進取',
    '土': '穩重、誠信、務實、有責任感',
    '金': '果斷、剛毅、有原則、重視名譽',
    '水': '智慧、圓融、適應力強、善於溝通',
}

# 五行相生相剋
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # 相生
KE = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}   # 相剋

def analyze_name(name: str) -> dict:
    if len(name) < 2:
        return {'error': '姓名至少需要兩個字'}

    surname = name[0]
    given = name[1:]

    # 取得各字筆畫
    strokes = [get_stroke_count(c) for c in name]
    unknown = [name[i] for i, s in enumerate(strokes) if s == 0]

    # 計算五格
    if len(name) == 2:
        # 兩字姓名
        tian = strokes[0] + 1
        ren = strokes[0] + strokes[1]
        di = strokes[1] + 1
        wai = 2
        zong = strokes[0] + strokes[1]
    elif len(name) == 3:
        # 三字姓名（最常見）
        tian = strokes[0] + 1
        ren = strokes[0] + strokes[1]
        di = strokes[1] + strokes[2]
        wai = strokes[2] + 1
        zong = sum(strokes)
    else:
        # 四字以上
        tian = strokes[0] + 1
        ren = strokes[0] + strokes[1]
        di = sum(strokes[1:])
        wai = di - strokes[1] + 1
        zong = sum(strokes)

    grids = {
        '天格': tian, '人格': ren, '地格': di, '外格': wai, '總格': zong
    }
    grid_wuxing = {k: number_to_wuxing(v) for k, v in grids.items()}

    # 三才（天格五行、人格五行、地格五行）判斷
    san_cai = (grid_wuxing['天格'], grid_wuxing['人格'], grid_wuxing['地格'])
    san_cai_score, san_cai_desc = evaluate_san_cai(san_cai)

    # 各格吉凶
    grid_scores = {k: evaluate_number(v) for k, v in grids.items()}

    # 整體評分
    total_score = round(
        grid_scores['人格']['score'] * 0.30 +
        grid_scores['地格']['score'] * 0.20 +
        grid_scores['總格']['score'] * 0.20 +
        grid_scores['天格']['score'] * 0.10 +
        grid_scores['外格']['score'] * 0.10 +
        san_cai_score * 0.10
    )

    result = {
        'name': name,
        'strokes': {name[i]: strokes[i] for i in range(len(name))},
        'unknown_chars': unknown,
        'grids': grids,
        'grid_wuxing': grid_wuxing,
        'san_cai': san_cai,
        'san_cai_score': san_cai_score,
        'san_cai_desc': san_cai_desc,
        'grid_scores': grid_scores,
        'total_score': total_score,
        'main_wuxing': grid_wuxing['人格'],
        'name_wuxing': [number_to_wuxing(s) for s in strokes],
        'char_strokes': list(zip(list(name), strokes)),
    }
    result['name_summary'] = generate_name_summary(result)
    return result

def evaluate_number(n: int) -> dict:
    """評估數字的吉凶（簡化版81靈數）"""
    lucky = {1,3,5,6,7,8,11,13,15,16,17,18,21,23,24,25,31,32,33,35,37,38,41,45,47,48,52,57,58,61,63,65,67,68}
    moderate = {2,10,20,22,30,40,50,60}
    n10 = n % 81 or 81
    if n10 in lucky:
        return {'score': 85, 'label': '吉', 'color': '#27ae60'}
    elif n10 in moderate:
        return {'score': 60, 'label': '中', 'color': '#f39c12'}
    else:
        return {'score': 40, 'label': '凶', 'color': '#e74c3c'}

def generate_name_summary(result: dict) -> list:
    """回傳姓名分析總體說明段落 list"""
    items = []

    # 整體評分
    score = result['total_score']
    if score >= 75:
        overall = f'整體命名評分 {score} 分，名字五行配置吉祥，有助於運勢發展，是一個佳名。'
    elif score >= 55:
        overall = f'整體命名評分 {score} 分，名字五行配置尚可，運勢平穩，後天努力可彌補不足。'
    else:
        overall = f'整體命名評分 {score} 分，名字五行配置較弱，建議考慮調整用字以改善運勢。'
    items.append(('整體評分', overall))

    # 人格（最重要的格）
    ren_score = result['grid_scores']['人格']
    ren_num   = result['grids']['人格']
    ren_wx    = result['grid_wuxing']['人格']
    wx_trait  = WUXING_TRAITS.get(ren_wx, '')
    items.append(('人格', f'人格數理為 {ren_num}（{ren_wx}），評定為「{ren_score["label"]}」。人格代表個性核心，{ren_wx}行主：{wx_trait}。'))

    # 三才
    items.append(('三才五行', result['san_cai_desc']))

    # 天格
    tian_score = result['grid_scores']['天格']
    tian_num   = result['grids']['天格']
    items.append(('天格', f'天格數理 {tian_num}，評定「{tian_score["label"]}」，代表先天祖德與長輩緣份的影響。'))

    # 地格
    di_score = result['grid_scores']['地格']
    di_num   = result['grids']['地格']
    items.append(('地格', f'地格數理 {di_num}，評定「{di_score["label"]}」，反映中年以後的基礎運與晚年發展。'))

    # 總格
    zong_score = result['grid_scores']['總格']
    zong_num   = result['grids']['總格']
    items.append(('總格', f'總格數理 {zong_num}，評定「{zong_score["label"]}」，代表一生整體命運走向與晚年福祉。'))

    # 主五行建議
    main_wx = result['main_wuxing']
    wx_color_name = {'木': '綠色', '火': '紅色', '土': '黃色', '金': '白色', '水': '黑藍色'}
    items.append(('五行建議', f'命主五行屬「{main_wx}」，日常可多接觸{wx_color_name.get(main_wx, "")}系物品、朝{main_wx}行旺盛的方位發展，有助增強自身能量。'))

    return items


def evaluate_san_cai(san_cai: tuple) -> tuple:
    """三才五行相生相剋分析"""
    t, r, d = san_cai
    sheng_count = 0
    ke_count = 0
    if SHENG.get(t) == r: sheng_count += 1
    elif KE.get(t) == r: ke_count += 1
    if SHENG.get(r) == d: sheng_count += 1
    elif KE.get(r) == d: ke_count += 1

    if ke_count == 0 and sheng_count == 2:
        return 90, f'三才相生（{t}→{r}→{d}），大吉！運勢亨通，諸事順遂。'
    elif ke_count == 0 and sheng_count == 1:
        return 75, f'三才半生（{t}·{r}→{d}或{t}→{r}·{d}），吉中帶平，運勢穩定。'
    elif ke_count == 1 and sheng_count == 1:
        return 55, f'三才生剋並存（{t}·{r}·{d}），吉凶相半，需靠後天努力。'
    elif ke_count == 2:
        return 30, f'三才相剋（{t}·{r}·{d}），運勢較阻，宜謹慎行事。'
    else:
        return 60, f'三才平和（{t}·{r}·{d}），運勢平穩，無大起伏。'
