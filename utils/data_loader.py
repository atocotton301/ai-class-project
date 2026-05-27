import pandas as pd
import os

# 프로그램 데이터를 누적하여 저장하는 함수
def accumulate_programs(new_programs_list):
    file_path = "data/programs.csv"
    
    # 1. 긁어온 새로운 데이터를 데이터프레임으로 변환
    new_df = pd.DataFrame(new_programs_list)
    
    # 2. 기존에 쌓아둔 csv 파일이 이미 존재한다면?
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        old_df = pd.read_csv(file_path)
        
        # 기존 데이터와 새 데이터를 합친 후 'title(프로그램명)' 기준으로 중복 제거
        # keep='first'를 쓰면 기존에 쌓여있던 데이터가 유지됩니다.
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
        final_df = combined_df.drop_duplicates(subset=['title'], keep='first')
    else:
        # 기존 파일이 없으면 새 데이터가 곧 최종 데이터
        final_df = new_df
        
    # 3. 중복이 제거된 최종 데이터를 csv에 다시 깔끔하게 저장
    final_df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f" 현재 누적된 총 비교과 프로그램 개수: {len(final_df)}개")