import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["figure.facecolor"] = "white"

def plot_combined_score_graph(
    top_question: str,
    sub_questions: list,
    df_all,
    df_team,
    team_name="팀A",
    save_path="static"
):
    os.makedirs(save_path, exist_ok=True)

    # 평균 계산
    top_score = df_team[top_question].mean()
    top_dept_avg = df_all[top_question].mean()
    sub_scores = [(q, df_team[q].mean(), df_all[q].mean()) for q in sub_questions]

    # 전체 그래프 틀 구성
    fig = plt.figure(figsize=(8, 6))  # PPT 좌측에 잘 맞게
    ax_gauge = plt.subplot2grid((5, 1), (0, 0), rowspan=2)
    ax_bar = plt.subplot2grid((5, 1), (2, 0), rowspan=3)

    # -------------------------
    # 상단 하프 게이지 차트
    # -------------------------
    theta = np.linspace(-np.pi, 0, 100)
    x = np.cos(theta)
    y = np.sin(theta)

    ax_gauge.plot(x, y, color="lightgray", lw=30, solid_capstyle='round')
    angle = -np.pi + (top_score / 5) * np.pi
    ax_gauge.plot(
        [0, np.cos(angle)],
        [0, np.sin(angle)],
        color="dodgerblue",
        lw=8,
        solid_capstyle='round'
    )

    # 전체 평균 점선
    avg_angle = -np.pi + (top_dept_avg / 5) * np.pi
    ax_gauge.plot(
        [0, np.cos(avg_angle)],
        [0, np.sin(avg_angle)],
        color="gray",
        linestyle="--",
        lw=2,
    )

    ax_gauge.text(0, -1.2, f"{top_question}\n팀 평균: {top_score:.2f} / 전체 평균: {top_dept_avg:.2f}", 
                  ha="center", fontsize=12)
    ax_gauge.axis("off")

    # -------------------------
    # 하단 수평 막대 그래프
    # -------------------------
    questions = [q for q, _, _ in sub_scores]
    team_vals = [s for _, s, _ in sub_scores]
    dept_vals = [d for _, _, d in sub_scores]

    y_pos = np.arange(len(questions))
    ax_bar.barh(y_pos, team_vals, color="lightcoral", height=0.4)
    for i, d_avg in enumerate(dept_vals):
        ax_bar.axvline(d_avg, color="gray", linestyle="--", lw=1)
        ax_bar.text(d_avg + 0.05, i, f"{d_avg:.2f}", va='center', fontsize=8, color="gray")

    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(questions, fontsize=10)
    ax_bar.set_xlim(0, 5)
    ax_bar.set_xlabel("점수")
    ax_bar.invert_yaxis()  # 위에서 아래로
    ax_bar.set_title("세부 항목 점수 (회색 점선 = 전체 평균)", fontsize=11)

    # -------------------------
    # 저장
    # -------------------------
    filename = f"{team_name}_{top_question[:10]}_통합그래프.png"
    filepath = os.path.join(save_path, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"[+] 저장 완료: {filepath}")
