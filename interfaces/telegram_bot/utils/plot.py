import os
import matplotlib.pyplot as plt
import tempfile
from datetime import datetime
from domain.entities.stats import StatsInDb
from io import BytesIO
import matplotlib.pyplot as plt


def generate_pie_chart(data: dict) -> str:
    labels = list(data.keys())
    sizes = list(data.values())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    plt.title("Статистика расходов")

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp_file.name)
    plt.close(fig)
    tmp_file.close()

    return tmp_file.name


def generate_bar_chart_bytes(data: dict, period_label: str, from_date: datetime, to_date: datetime) -> BytesIO:
    categories = list(data.keys())
    amounts = list(data.values())

    fig, ax = plt.subplots()
    ax.barh(categories, amounts, color='skyblue')
    ax.set_xlabel("Сумма трат")
    ax.set_title(f"Статистика расходов за {period_label}\n({from_date.strftime('%d.%m')} – {to_date.strftime('%d.%m')})")

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)

    # Очищаем внутренние ресурсы Matplotlib
    plt.clf()  # Очищаем текущую фигуру
    plt.cla()  # Очищаем текущую ось
    plt.close('all')

    buf.name = "stats.png"  # нужно для Telethon
    buf.seek(0)
    return buf



# def generate_bar_chart(data: dict, period_label: str, from_date: datetime, to_date: datetime) -> str:
#     categories = list(data.keys())
#     amounts = list(data.values())

#     fig, ax = plt.subplots()
#     ax.barh(categories, amounts, color='skyblue')
#     ax.set_xlabel("Сумма трат")

#     date_range = f"{from_date.strftime('%d.%m')} – {to_date.strftime('%d.%m')}"
#     ax.set_title(f"Статистика расходов за {period_label}\n({date_range})")

#     plt.tight_layout()
#     tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
#     plt.savefig(tmp_file.name)
#     plt.close(fig)
#     tmp_file.close()

#     return tmp_file.name
