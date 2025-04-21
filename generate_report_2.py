import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import os

# ----------------------------------------
# 1. 기본 경로 설정
# ----------------------------------------
data_file = "data.csv"
template_dir = "templates"
output_dir = "output"
static_dir = "static"

# ----------------------------------------
# 2. 문항 분류 설정 (하드코딩 OK)
# ----------------------------------------
score_top_questions = ['score_1', 'score_4']
score_sub_questions = {
    'score_1': ['score_2', 'score_3'],
    'score_4': ['score_5', 'score_6', 'score_7', 'score_8', 'score_9', 'score_10']
}
select_questions = ['select_성장요인', 'select_문화요인', 'select_몰입요인']

# ----------------------------------------
# 3. 디렉토리 준비
# ----------------------------------------
Path(output_dir).mkdir(exist_ok=True)
Path(static_dir).mkdir(exist_ok=True)

# ----------------------------------------
# 4. 데이터 불러오기
# ----------------------------------------
df = pd.read_csv(data_file)
teams = df["팀"].unique()

# ----------------------------------------
# 5. Jinja2 환경 설정
# ----------------------------------------
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template("report_with_graphs.html")

# ----------------------------------------
# 6. 팀별 페이지 생성
# ----------------------------------------
for team in teams:
    team_df = df[df["팀"] == team]
    team_static = Path(static_dir) / team
    team_static.mkdir(parents=True, exist_ok=True)

    top_results = []
    sub_results = []
    select_results = []

    # 6-1. 상위 점수형 문항 → 반원형 게이지
    for top_q in score_top_questions:
        values = team_df[top_q].dropna()
        if values.empty:
            continue
        score = round(values.mean(), 1)
        label = top_q.replace("score_", "")

        fig, ax = plt.subplots(figsize=(4, 2))
        ax.barh(0, score, height=0.3, color="#3f51b5")
        ax.set_xlim(0, 5)
        ax.set_yticks([])
        ax.set_title(f"{label} 평균: {score}", fontsize=10)
        plt.tight_layout()
        filename = f"{label}_gauge.png"
        fig.savefig(team_static / filename)
        plt.close()

        top_results.append({
            "이름": top_q,
            "라벨": label,
            "값": score,
            "파일": filename
        })

    # 6-2. 하위 점수형 문항 → 바 게이지
    for top_q, sub_qs in score_sub_questions.items():
        sub_list = []
        for sub_q in sub_qs:
            values = team_df[sub_q].dropna()
            if values.empty:
                continue
            score = round(values.mean(), 1)
            label = sub_q.replace("score_", "")

            fig, ax = plt.subplots(figsize=(3, 0.4))
            ax.barh([label], [score], color="#4caf50")
            ax.set_xlim(0, 5)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            plt.tight_layout()
            filename = f"{label}_bar.png"
            fig.savefig(team_static / filename)
            plt.close()

            sub_list.append({
                "이름": sub_q,
                "라벨": label,
                "값": score,
                "파일": filename
            })

        if sub_list:
            sub_results.append({
                "상위": top_q.replace("score_", ""),
                "하위": sub_list
            })

    # 6-3. 선택형 → Top5 주관식 항목 비율 추출
    for sel_q in select_questions:
        select_cols = [col for col in team_df.columns if col.startswith(sel_q + "_")]
        if not select_cols:
            continue
        counts = team_df[select_cols].sum().sort_values(ascending=False)
        total = counts.sum()
        top_items = []
        for i, (col, count) in enumerate(counts.head(5).items(), 1):
            item = col.replace(sel_q + "_", "")
            percent = int(round((count / total) * 100)) if total > 0 else 0
            top_items.append(f"{i}. {item} ({percent}%)")
        select_results.append({
            "질문": sel_q.replace("select_", ""),
            "top5": top_items
        })

    # 6-4. HTML 렌더링
    html = template.render(
        team={"팀": team},
        top_results=top_results,
        sub_results=sub_results,
        select_results=select_results
    )

    with open(Path(output_dir) / f"team_{team}.html", "w", encoding="utf-8") as f:
        f.write(html)
