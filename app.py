import os
import threading
import webbrowser
from flask import Flask, render_template, request, jsonify
from name_analysis import analyze_name
from ziwei_calc import generate_ziwei_chart, calculate_liunian
from bazi_calc import calculate_bazi

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    name         = data.get('name', '').strip()
    birth_year   = int(data.get('year', 1990))
    birth_month  = int(data.get('month', 1))
    birth_day    = int(data.get('day', 1))
    birth_hour   = int(data.get('hour', 0))
    gender       = data.get('gender', '男')
    liunian_year = int(data.get('liunian_year', 2026))

    errors = []
    if not name:
        errors.append('請輸入姓名')
    if len(name) < 2:
        errors.append('姓名至少需要兩個字')
    if errors:
        return jsonify({'error': '、'.join(errors)}), 400

    try:
        name_result = analyze_name(name)
    except Exception as e:
        name_result = {'error': str(e)}

    try:
        chart_result = generate_ziwei_chart(
            birth_year, birth_month, birth_day, birth_hour, gender)
    except Exception as e:
        chart_result = {'error': str(e)}

    try:
        liunian_result = calculate_liunian(
            birth_year, birth_month, birth_day, birth_hour, gender, liunian_year)
    except Exception as e:
        liunian_result = {'error': str(e)}

    try:
        bazi_result = calculate_bazi(birth_year, birth_month, birth_day, birth_hour, gender)
    except Exception as e:
        bazi_result = {'error': str(e)}

    return jsonify({
        'name_analysis': name_result,
        'ziwei_chart':   chart_result,
        'liunian':       liunian_result,
        'bazi':          bazi_result,
    })

@app.route('/liunian', methods=['POST'])
def liunian():
    data = request.json
    try:
        birth_year  = int(data.get('year', 1990))
        birth_month = int(data.get('month', 1))
        birth_day   = int(data.get('day', 1))
        birth_hour  = int(data.get('hour', 0))
        gender      = data.get('gender', '男')
        liunian_year = int(data.get('liunian_year', 2026))
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'資料格式錯誤：{e}'}), 400

    try:
        result = calculate_liunian(birth_year, birth_month, birth_day,
                                   birth_hour, gender, liunian_year)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(result)


if __name__ == '__main__':
    import sys
    if '--local' in sys.argv:
        print('神機妙算 啟動中...')
        print('請開啟瀏覽器：http://127.0.0.1:5000')
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            threading.Thread(target=lambda: (threading.Event().wait(1.5), webbrowser.open('http://127.0.0.1:5000')), daemon=True).start()
        app.run(debug=True)
    else:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
