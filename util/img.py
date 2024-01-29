import matplotlib.pyplot as plt
import pandas as pd


# 年度利润变化图
def lr_img():
    df = pd.read_csv('../data/lr/SH600006.csv')
    grouped = df.groupby(df['REPORT_DATE'].astype(str).str[:4])
    aggregated = grouped['OPERATE_INCOME'].last()

    x = aggregated.index
    y = aggregated.values

    # 计算增长率
    growth_rate = [(y[i + 1] - y[i]) / y[i] * 100 for i in range(len(y) - 1)]
    print('avg:', f'{sum(growth_rate) / len(growth_rate):.2f}%\n')

    # 绘制折线图
    plt.xticks(rotation=90)
    plt.plot(x, y, marker='o')

    # 在每个数据点上显示增长率
    for i in range(0, len(y) - 1):
        print(x[i + 1], f'{growth_rate[i]:.2f}%')
        plt.text(i + 1, y[i + 1], f'{growth_rate[i]:.2f}%', ha='center', va='bottom')

    plt.title('增长率')
    plt.xlabel('X轴')
    plt.ylabel('Y轴')
    plt.show()


if __name__ == '__main__':
    lr_img()
