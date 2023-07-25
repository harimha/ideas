import plotly.graph_objects as go

# 예시 데이터
categories = ['Category 1', 'Category 2', 'Category 3']
values = [10, 15, 5]

# 바차트 생성
fig = go.Figure()

fig.add_trace(go.Bar(
    x=categories,
    y=values,
    width=[0.5, 0.8, 0.3],  # 각 바의 넓이를 순서대로 지정
    marker_color='blue',
    text=values,  # 바에 값 표시
    textposition='auto',
))

fig.update_layout(
    title='Bar Chart with Customized Bar Width',
    xaxis=dict(title='Category'),
    yaxis=dict(title='Value'),
)

fig.show()