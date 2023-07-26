class Visualize():
    def _get_bar_width_tradeoff(self, df_data, df_result):
        '''
        bar chart에서 투자 기간에 따른 bar width와 trade off 를 반환
        '''
        bar_width = df_result["date"].shift(-1) - df_result["date"]
        bar_width = bar_width.fillna(df_data.index[-1] - df_result["date"].iloc[-1])
        bar_width = bar_width.astype("int64") / 1000000  # microseconds 단위로 변환
        bar_tradeoff = bar_width.astype("int64") / 2000000 # 1/2 microseconds 만큼 이동

        return bar_width, bar_tradeoff

    def _set_color(self, df, column, value_color: dict):
        '''
        color 변환용 값 반환
        value_color : ex){"buy": "orange", "sell": "purple"}
        '''
        df_col = df.copy()
        for value, color in value_color.items():
            df_col.loc[df_col[column] == value, "color"] = color
        df_col = df_col["color"]

        return df_col

    def _add_trading_signal(self, df_result, fig):
        for i in range(len(df_result)):
            date = df_result.iloc[i]["date"]
            value = df_result.iloc[i]["value"]
            sig = df_result.iloc[i]["signal"]
            if sig == "buy":
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="red",
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5,
                                   secondary_y=False
                                   )
            elif sig == "sell":
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="blue",
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5,
                                   secondary_y=False)

    def visualize_1(self, df_data, df_result, html=True):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        bar_width, bar_tradeoff = self._get_bar_width_tradeoff(df_data, df_result)
        color_data = self._set_color(df_data, df_data.columns[-2], {"bull":"lightcoral", "bear":"lightskyblue"})
        color_trading = self._set_color(df_result, "signal", {"buy":"red", "sell":"blue"})
        color_return = self._set_color(df_result, "signal", {"buy":"orange", "sell":"purple"})
        fig.add_trace(go.Scatter(x=df_data.index,
                                 y=df_data["종가"],
                                 mode="markers",
                                 marker={"size": 3,
                                         "opacity": 0.5,
                                         "color": color_data},
                                 name="종가"),secondary_y=False)
        fig.add_trace(go.Scatter(x=df_result["date"],
                                 y=df_result["value"],
                                 mode="markers",
                                 marker={"size": 4,
                                         "color": color_trading},
                                 name="signal"
                                 ),secondary_y=False)
        fig.add_trace(go.Scatter(x=df_result["date"],
                                 y=df_result["acc_rtrn"],
                                 mode="lines",
                                 name="acc_rtrn"), secondary_y=True)
        fig.add_trace(go.Bar(x=df_result["date"],
                             y=df_result["rtrn"],
                             marker={"color": color_return},
                             name="rtrn",
                             opacity=0.4,
                             width=bar_width,
                             offset=bar_tradeoff,
                             text=df_result["rtrn"],
                             textposition="outside",
                             textangle=0),secondary_y=True)
        self._add_trading_signal(df_result, fig)

        if html :
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            fig.write_html(f"{now}.html")
        else:
            fig.show()
