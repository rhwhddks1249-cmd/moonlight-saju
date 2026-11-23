import os
from flask import Flask, render_template, request, jsonify
from saju_engine import SajuAnalyzer
from today_fortune import today_fortune
from love_compat import love_today, compatibility
base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))


class _Birth:
    """음력 날짜(예: 2월 30일)도 그대로 담기 위한 단순 보관함"""
    def __init__(self, year, month, day, hour, minute):
        self.year, self.month, self.day = year, month, day
        self.hour, self.minute = hour, minute



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    d = request.get_json(silent=True) or {}
    try:
        year, month, day = int(d['year']), int(d['month']), int(d['day'])
        hour, minute = int(d.get('hour', 12)), int(d.get('minute', 0))
        gender = 'female' if d.get('gender') == 'female' else 'male'
        has_hour = bool(d.get('has_hour', True))
        is_lunar = bool(d.get('is_lunar', False))
        is_leap = bool(d.get('is_leap', False))
        if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31
                and 0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("날짜 범위가 올바르지 않습니다.")
        if is_lunar:
            birth = _Birth(year, month, day, hour, minute)
        else:
            import datetime
            birth = datetime.datetime(year, month, day, hour, minute)
        result = SajuAnalyzer(name=str(d.get('name', ''))[:10], gender=gender,
                              birth_dt=birth, has_hour=has_hour,
                              is_lunar=is_lunar, is_leap=is_leap).analyze()
        return jsonify(result)
    except (KeyError, ValueError, TypeError) as e:
        return jsonify(error=f"입력값을 확인해 주세요: {e}"), 400
    except Exception as e:
        app.logger.exception("analyze failed")
        return jsonify(error="분석 중 오류가 발생했습니다."), 500


@app.route('/api/today', methods=['POST'])
def today():
    """오늘의 운세. 요청: {"day_stem": "갑"} (내 일간 한글 또는 한자 한 글자)"""
    d = request.get_json(silent=True) or {}
    try:
        return jsonify(today_fortune(d.get('day_stem')))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception:
        app.logger.exception("today failed")
        return jsonify(error="오늘의 운세를 불러오지 못했습니다."), 500


@app.route('/api/love', methods=['POST'])
def love():
    """연애운. 요청: {"day_stem": "갑", "gender": "남"}"""
    d = request.get_json(silent=True) or {}
    try:
        return jsonify(love_today(d.get('day_stem'), d.get('gender', '남')))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception:
        app.logger.exception("love failed")
        return jsonify(error="연애운을 불러오지 못했습니다."), 500


@app.route('/api/compat', methods=['POST'])
def compat():
    """궁합. 요청: {"stem_a": "갑", "stem_b": "기"}"""
    d = request.get_json(silent=True) or {}
    try:
        return jsonify(compatibility(d.get('stem_a'), d.get('stem_b')))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception:
        app.logger.exception("compat failed")
        return jsonify(error="궁합을 불러오지 못했습니다."), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=bool(os.environ.get('DEBUG')))
