import pandas as pd

def get_sorted_programs(df, user_categories, sort_option):
    """
    유저의 관심 카테고리로 1차 필터링 후, 선택한 옵션에 따라 2차 정렬하는 함수
    """
    # 1. 유저가 온보딩에서 선택한 카테고리만 필터링
    if user_categories:
        filtered_df = df[df['카테고리'].isin(user_categories)].copy()
    else:
        filtered_df = df.copy()

    # 2. 선택된 정렬 옵션에 따른 분기 처리
    if sort_option == "🔥 포인트 높은 순":
        return filtered_df.sort_values(by="포인트", ascending=False)
        
    elif sort_option == "⏱️ 시간 대비 가성비 순":
        # 가성비 = 포인트 / 소요시간 계산 후 내림차순 정렬
        filtered_df['가성비(시간당 포인트)'] = filtered_df['포인트'] / filtered_df['소요시간(시간)']
        return filtered_df.sort_values(by="가성비(시간당 포인트)", ascending=False)
        
    elif sort_option == "🍯 꿀지수 (난이도) 높은 순":
        return filtered_df.sort_values(by="꿀지수", ascending=False)
        
    elif sort_option == "💖 혜자지수 (만족도) 높은 순":
        return filtered_df.sort_values(by="혜자지수", ascending=False)
        
    return filtered_df