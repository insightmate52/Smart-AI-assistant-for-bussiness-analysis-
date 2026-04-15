import os
import uuid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import seaborn as sns

# ===========================
# 🎨 THEME (BROWN UI MATCH)
# ===========================
BROWN_PALETTE = [
    "#a67c52",  # brown
    "#d4a373",  # gold
    "#c2410c",  # soft orange
    "#9ca3af",  # grey
]

sns.set_theme(style="darkgrid", palette=BROWN_PALETTE)

plt.style.use("dark_background")

plt.rcParams.update({
    "figure.facecolor": "none",
    "axes.facecolor": "none",

    "axes.labelcolor": "#ffffff",
    "xtick.color": "#ffffff",
    "ytick.color": "#ffffff",
    "text.color": "#ffffff",

    "grid.color": "#d4a373",
    "grid.alpha": 0.25,

    "axes.edgecolor": "#d4a373",
})

# ===========================
# 🧼 SAVE FIX (IMPORTANT)
# ===========================
def save_plot_clean(path):
    plt.tight_layout()
    plt.savefig(path, transparent=True, bbox_inches='tight')
    plt.close()

# ===========================
# 🧹 CLEAN DATA
# ===========================
def clean_data(df):
    df = df.reset_index(drop=True).copy()

    date_cols = [c for c in df.columns if "date" in c.lower()]
    if date_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.sort_values(date_col)
        df = df.drop(columns=[date_col])

    df = df.dropna(how="all")
    df = df.ffill().bfill()

    return df

# ===========================
# 🔍 VALIDATE
# ===========================
def validate_data(df):
    if df.shape[0] < 5:
        print("⚠️ Very few rows")
    if df.shape[1] < 2:
        print("⚠️ Very few columns")

# ===========================
# 📝 TEXT INSIGHTS
# ===========================
def get_top5_text_insights(df):
    insights = []

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    if not num_cols:
        return ["No numeric columns found."]

    col = num_cols[0]
    insights.append(f"Average value of {col} is {df[col].mean():.2f}.")

    if len(num_cols) >= 2:
        corr = df[num_cols].corr().abs().copy()
        mask = np.tril(np.ones(corr.shape), k=0).astype(bool)
        corr.where(~mask, inplace=True)

        if not corr.stack().empty:
            pair = corr.stack().idxmax()
            insights.append(f"{pair[0]} shows strong correlation with {pair[1]}.")

    if cat_cols:
        top_cat = df.groupby(cat_cols[0])[col].sum().idxmax()
        insights.append(f"{top_cat} contributes highest value to {col}.")

    insights.append(f"Top 10% of {col} are high-value records.")
    insights.append(f"Bottom 10% of {col} indicate potential risk.")

    return insights[:5]

# ===========================
# 📊 VISUAL INSIGHTS
# ===========================
def get_top5_visual_insights(df, output_dir="static/insights"):
    os.makedirs(output_dir, exist_ok=True)
    images = []

    uid = uuid.uuid4().hex[:6]

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    if not num_cols:
        return images

    # 1️⃣ Histogram
    plt.figure()
    plt.hist(df[num_cols[0]], bins=20, color="#a67c52")
    path = f"viz_{uid}_hist.png"
    save_plot_clean(os.path.join(output_dir, path))
    images.append(path)

    # 2️⃣ Scatter
    if len(num_cols) >= 2:
        plt.figure()
        plt.scatter(df[num_cols[0]], df[num_cols[1]], color="#d4a373")
        path = f"viz_{uid}_scatter.png"
        save_plot_clean(os.path.join(output_dir, path))
        images.append(path)

    # 3️⃣ Bar
    if cat_cols:
        plt.figure()
        df.groupby(cat_cols[0])[num_cols[0]].sum().head(5).plot(
            kind="bar",
            color="#a67c52"
        )
        path = f"viz_{uid}_bar.png"
        save_plot_clean(os.path.join(output_dir, path))
        images.append(path)

    # 4️⃣ Boxplot
    plt.figure()
    plt.boxplot(df[num_cols[0]])
    path = f"viz_{uid}_box.png"
    save_plot_clean(os.path.join(output_dir, path))
    images.append(path)

    # 5️⃣ Heatmap
    if len(num_cols) >= 3:
        plt.figure(figsize=(6, 4))
        corr = df[num_cols].corr()

        plt.imshow(corr, cmap="copper")  # 🔥 brown tone
        plt.colorbar()

        plt.xticks(range(len(num_cols)), num_cols, rotation=45)
        plt.yticks(range(len(num_cols)), num_cols)

        path = f"viz_{uid}_heat.png"
        save_plot_clean(os.path.join(output_dir, path))
        images.append(path)

    return images[:5]
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os, uuid

def create_report(text_insights, visual_images, output_dir="static"):
    os.makedirs(output_dir, exist_ok=True)

    report_path = os.path.join(
        output_dir, f"report_{uuid.uuid4().hex[:6]}.pdf"
    )

    doc = SimpleDocTemplate(report_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # 🎨 STYLES
    title_style = styles["Heading1"]
    title_style.textColor = colors.HexColor("#5a3e2b")  # brown theme

    subtitle_style = styles["Heading2"]
    subtitle_style.textColor = colors.HexColor("#a67c52")

    normal_style = styles["BodyText"]
    normal_style.fontSize = 11

    content = []

    # =========================
    # TITLE
    # =========================
    content.append(Paragraph("InsightMate Report", title_style))
    content.append(Spacer(1, 20))

    # =========================
    # TEXT INSIGHTS
    # =========================
    content.append(Paragraph("Top 5 Insights", subtitle_style))
    content.append(Spacer(1, 10))

    for i, ins in enumerate(text_insights, 1):
        content.append(Paragraph(f"<b>{i}.</b> {ins}", normal_style))
        content.append(Spacer(1, 8))

    content.append(Spacer(1, 20))

    # =========================
    # VISUAL INSIGHTS
    # =========================
    content.append(Paragraph("Visual Insights", subtitle_style))
    content.append(Spacer(1, 10))

    for img in visual_images:
        img_path = os.path.join("static/insights", img)

        if os.path.exists(img_path):
            content.append(Image(img_path, width=450, height=280))
            content.append(Spacer(1, 15))

    # =========================
    # BUILD
    # =========================
    doc.build(content)

    return report_path