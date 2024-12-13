import os
import django
from django.db import connection

# Django 프로젝트 설정 초기화
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigkihan.settings")  # 프로젝트 이름에 맞게 변경
django.setup()

# 데이터베이스 연결 및 Raw SQL 실행
def insert_default_foods():
    food_items = [
        {"name": "양파", "image": "/food_images/onion.svg", "comment": "양파, 지금 썰면 눈물 대신 달달한 웃음이 나올걸요? 🧅"},
        {"name": "감자", "image": "/food_images/potato.svg", "comment": "감자, 떠날 준비 중! 한 번 삶아줘야 다시 만나죠! 🥔"},
        {"name": "양배추", "image": "/food_images/cabbage.svg", "comment": "아삭아삭 양배추, 신선함이 곧 사라질지도 몰라요!"},
        {"name": "김치류", "image": "/food_images/kimchi.svg", "comment": "김치, 지금 가장 맛있을 때! 더 기다리면 시큼해질지도 🥬"},
        {"name": "우유", "image": "/food_images/milk.svg", "comment": "우유는 지금이 신선함의 끝! 얼른 드셔야 해유! 🥛"},
        {"name": "돼지고기", "image": "/food_images/pork.svg", "comment": "지금 굽는다면 맛도 기분도 업 돼지 🥩"},
        {"name": "소고기", "image": "/food_images/beef.svg", "comment": "부드러운 소고기, 지금 구워야 풍미를 놓치지 않아요 🥩"},
        {"name": "닭고기", "image": "/food_images/chicken.svg", "comment": "닭! 지금 요리하면 담백함이 쫙~ 펼쳐져요! 🍗"},
        {"name": "고등어", "image": "/food_images/mackerel.svg", "comment": "고등어, 오늘 굽지 않으면 고등급의 맛을 놓칠지도 몰라요! 🐟"},
        {"name": "청경채", "image": "/food_images/bokchoy.svg", "comment": "청경채의 초록빛 매력, 지금 아니면 놓쳐요! 🥬"},
        {"name": "계란", "image": "/food_images/egg.svg", "comment": "오늘이 신선함의 끝자락! 계란 후라이로 맛있게 즐기세요! 🍳"},
        {"name": "소시지", "image": "/food_images/sausage.svg", "comment": "소시지는 딱 지금이 맛있죠! 지나면 쏘쏘해져요 🥖"},
        {"name": "밥", "image": "/food_images/rice.svg", "comment": "냉장고 속에 오래 두면 밥맛 없어져요! 🍚"},
        {"name": "두부", "image": "/food_images/tofu.svg", "comment": "부드러운 지금, 바로 써야 두부의 신선함을 느낄 수 있어요! ☺️"},
        {"name": "오징어", "image": "/food_images/squid.svg", "comment": "오징어, 부드럽고 쫄깃한 그 맛, 놓치지 마세요! 🦑"},
        {"name": "조개", "image": "/food_images/shell.svg", "comment": "지금 바로 조리해야 쫄깃한 맛이 최고일 조개 🦪"},
        {"name": "배추", "image": "/food_images/napa_cabbage.svg", "comment": "배추잎이 아삭할 때 바로 드셔야죠! 🥬"},
        {"name": "무", "image": "/food_images/radish.svg", "comment": "무르기 전에 얼른 요리하세요, 무 맛이 최고예요! 👍"},
        {"name": "마늘", "image": "/food_images/garlic.svg", "comment": "마늘도 오래 두면 힘 빠져요! ‘알’ 맞은 때를 놓치지 마세요 🧄"},
        {"name": "대파", "image": "/food_images/green_onion.svg", "comment": "대파의 파릇파릇함, 곧 사라질지도 몰라요! 🌱"},
        {"name": "고추", "image": "/food_images/pepper.svg", "comment": "톡 쏘는 신선함, 지금 드셔야 고추의 매운 맛이 살아나요 🌶"},
        {"name": "된장", "image": "/food_images/soybean_paste.svg", "comment": "된장, 깊은 맛이 지금 가장 짙어요! 오래 두면 억울할 맛 🥄"},
        {"name": "간장", "image": "/food_images/soy_sauce.svg", "comment": "간장이 간당간당~ 지금이 제맛이에요!"},
        {"name": "고추장", "image": "/food_images/redpepper_paste.svg", "comment": "고추장도 타이밍이에요! 너무 오래 두면 기분만 매워져요🌶️"},
        {"name": "참기름", "image": "/food_images/sesame_oil.svg", "comment": "참 고소한 지금이 참기름 딱 쓰기 좋은 때예요! 🥄"},
        {"name": "들기름", "image": "/food_images/perilla_oil.svg", "comment": "들었어요? 들기름이 오늘 맛있게 쓰이길 기다리고 있어요!"},
        {"name": "고구마", "image": "/food_images/sweetpotato.svg", "comment": "달콤한 고구마, 지금 먹으면 꿀처럼 녹아내려요! 🍠"},
        {"name": "사과", "image": "/food_images/apple.svg", "comment": "사과합니다... 지금 안 먹으면 곧 물러질지도 몰라요! 🍎"},
        {"name": "오렌지", "image": "/food_images/orange.svg", "comment": "상큼한 비타민, 오렌지 지금 먹어야 제일 달아요! 🍊"},
        {"name": "피망", "image": "/food_images/pimento.svg", "comment": "아삭한 피망, 이대로 두면 금방 쭈글해질지도 몰라요! 🫑"},
        {"name": "바나나", "image": "/food_images/banana.svg", "comment": "바나나, 오늘이 아니면 내일은 반점의 시대가 옵니다!’ 🍌"},
        {"name": "빵", "image": "/food_images/bread.svg", "comment": "빵빵! 유효기간 알람 울립니다! 지금 먹어야 놓치지 않아요 🍞"},
        {"name": "기타", "image": "/food_images/other.svg", "comment": "오늘이 너와 나의 운명적인 요리 타이밍! 놓치면 사라질지도!"},
        {"name": "브로콜리", "image": "/food_images/broccoli.svg", "comment": "브로콜리로 초록빛 건강 충전, 신선할 때 얼른 드세요! 🥦"},
        {"name": "옥수수", "image": "/food_images/corn.svg", "comment": "톡톡 터지는 달콤함, 옥수수는 지금이 제철이에요! 🌽"},
        {"name": "가지", "image": "/food_images/egg_plant.svg", "comment": "여러가지 할 필요 없어요, 오늘의 요리는 바로 가지! 🍆"},
        {"name": "오이", "image": "/food_images/cucumber.svg", "comment": "오이, 아삭한 타이밍은 지금뿐! 늦으면 후회해요! 🥒"},
        {"name": "당근", "image": "/food_images/carrot.svg", "comment": "당근 당근 오늘 써야죠! 지금이 딱 맛있는 순간이에요. 🥕"},
        {"name": "딸기", "image": "/food_images/strawberry.svg", "comment": "딸기처럼 상큼한 하루, 지금이 제일 맛있을 때에요! 🍓"},
        {"name": "토마토", "image": "/food_images/tomato.svg", "comment": "토마토처럼 새콤달콤한 하루, 지금 만들어보세요! 🍅"}
    ]

# 데이터 삽입
    with connection.cursor() as cursor:
        for food in food_items:
            cursor.execute(
                """
                INSERT INTO default_food (name, image)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
                """,  # PostgreSQL 예시, MySQL에서는 ON CONFLICT가 아닌 REPLACE 사용
                [food["name"], food["image"]],
            )

    print("Default foods added successfully.")

# 실행
if __name__ == "__main__":
    insert_default_foods()