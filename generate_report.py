import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from matplotlib.patches import Wedge

plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

# -------------------------------
# STEP 1: 데이터 로드 & 분류
# -------------------------------
df = pd.read_csv("data.csv")
df["부서"] = df["부서"].fillna("부서")

def classify_columns(df):
    score_cols = [col for col in df.columns if col.startswith("score_")]
    select_candidates = [col for col in df.columns if "_" in col and not col.startswith("score_")]
    prefixes = [col.split("_")[0] for col in select_candidates]
    duplicated_prefixes = [p for p in set(prefixes) if prefixes.count(p) > 1]
    select_cols = [col for col in df.columns if any(col.startswith(p + "_") for p in duplicated_prefixes)]
    return score_cols, duplicated_prefixes, select_cols

score_cols, select_prefixes, select_cols = classify_columns(df)

# -------------------------------
# STEP 2: 분석 및 그래프 생성
# -------------------------------
top_results = []
sns.set(style="whitegrid", font_scale=1.1)

for (dept, team), group in df.groupby(["부서", "팀"]):
    result = {"부서": dept, "팀": team, "지표": []}
    team_dir = Path("static") / team
    team_dir.mkdir(parents=True, exist_ok=True)

    for col in score_cols:
        team_mean = round(group[col].mean(), 2)
        dept_mean = round(df[df["부서"] == dept][col].mean(), 2)

        result["지표"].append({"이름": col, "값": team_mean, "강조": True})

        def plot_half_donut(value, label, filename, max_val=100.0, 부서평균=None):
            percent = (value / max_val) * 100
            angle = (percent / 100) * 180
            fig, ax = plt.subplots(figsize=(3, 2))
            ax.add_patch(Wedge((0, 0), 1, 0, 180, width=0.3, facecolor="#e0e0e0"))
            ax.add_patch(Wedge((0, 0), 1, 180 - angle, 180, width=0.3, facecolor="#f25f5c"))
            ax.text(0, -0.1, f"{value:.1f}", ha='center', va='top', fontsize=10)
            ax.text(0, 0.25, label.replace("score_", ""), ha='center', va='bottom', fontsize=11)

            if 부서평균 is not None:
                dept_angle = (부서평균 / max_val) * 180
                rad = np.deg2rad(180 - dept_angle)
                x = 1 * np.cos(rad)
                y = 1 * np.sin(rad)
                ax.plot([0, x], [0, y], linestyle="dotted", color="black", linewidth=2)
                ax.text(x * 0.8, y * 0.8, f"부서평균\n{부서평균:.1f}", fontsize=7, ha='center', va='center', backgroundcolor='white')

            ax.set_xlim(-1.1, 1.1)
            ax.set_ylim(-0.2, 1.1)
            ax.axis('off')
            plt.tight_layout()
            plt.savefig(filename, dpi=150)
            plt.close()

        plot_half_donut(team_mean, col, team_dir / f"{col}_gauge.png", max_val=100.0, 부서평균=dept_mean)

    for prefix in select_prefixes:
        cols = [col for col in select_cols if col.startswith(prefix + "_")]
        counts = group[cols].sum().sort_values(ascending=False).head(3)
        for label, count in counts.items():
            name = label.split("_", 1)[1]
            result["지표"].append({"이름": f"{prefix}_Top", "값": f"{name} ({int(count)}명)", "강조": False})

        labels = [c.split("_", 1)[1] for c in counts.index]
        data = pd.DataFrame({"항목": labels, "응답수": counts.values})
        plt.figure(figsize=(6, 3.5))
        ax = sns.barplot(data=data, x="응답수", y="항목", hue="항목", palette="pastel", dodge=False, legend=False)
        plt.title(f"{team}팀 - {prefix} 응답 Top3", fontsize=13)
        plt.xlabel("응답 수")
        plt.ylabel("항목")
        for i, v in enumerate(data["응답수"]):
            ax.text(v + 0.3, i, f"{int(v)}명", color='black', va='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(team_dir / f"{prefix}_Top3.png", dpi=150)
        plt.close()

    comments = group["기타의견"].dropna().astype(str).str.strip()
    result["기타의견"] = comments[comments != ""].tolist()
    top_results.append(result)

# -------------------------------
# STEP 3: HTML 템플릿으로 보고서 생성
# -------------------------------
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("report_with_graphs.html")
html = template.render(results=top_results, select_prefixes=select_prefixes)
Path("team_report_with_graphs.html").write_text(html, encoding="utf-8")
print("✅ HTML 보고서 생성 완료!")
