import os
import django
from django.db import connection

# Django 프로젝트 설정 초기화
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigkihan.settings")  # 프로젝트 이름에 맞게 변경
django.setup()

# 데이터베이스 연결 및 Raw SQL 실행
def insert_default_foods():

    food_items = [
        {"name": "양파", "image": "/food_images/onion.svg"},
        {"name": "양배추", "image": "/food_images/cabbage.svg"},
        {"name": "김치류", "image": "/food_images/kimchi.svg"},
        {"name": "우유", "image": "/food_images/milk.svg"},
        {"name": "돼지고기", "image": "/food_images/pork.svg"},
        {"name": "소고기", "image": "/food_images/beef.svg"},
        {"name": "고등어", "image": "/food_images/mackerel.svg"},
        {"name": "청경채", "image": "/food_images/bokchoy.svg"},
        {"name": "계란", "image": "/food_images/egg.svg"},
        {"name": "소시지", "image": "/food_images/sausage.svg"},
        {"name": "두부", "image": "/food_images/tofu.svg"},
        {"name": "밥", "image": "/food_images/rice.svg"},
        {"name": "오징어", "image": "/food_images/squid.svg"},
        {"name": "조개", "image": "/food_images/clam.svg"},
        {"name": "배추", "image": "/food_images/napa_cabbage.svg"},
        {"name": "무", "image": "/food_images/radish.svg"},
        {"name": "마늘", "image": "/food_images/garlic.svg"},
        {"name": "대파", "image": "/food_images/leek.svg"},
        {"name": "고추", "image": "/food_images/chili.svg"},
        {"name": "된장", "image": "/food_images/doenjang.svg"},
        {"name": "간장", "image": "/food_images/soy_sauce.svg"},
        {"name": "고추장", "image": "/food_images/redpepper_paste.svg"},
        {"name": "참기름", "image": "/food_images/sesame_oil.svg"},
        {"name": "들기름", "image": "/food_images/perilla_oil.svg"},
        {"name": "고구마", "image": "/food_images/sweet_potato.svg"},
        {"name": "사과", "image": "/food_images/apple.svg"},
        {"name": "오렌지", "image": "/food_images/orange.svg"},
        {"name": "피망", "image": "/food_images/bell_pepper.svg"},
        {"name": "바나나", "image": "/food_images/banana.svg"},
        {"name": "기타", "image": "/food_images/etc.svg"},
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