"""
app/tools/financial_data/market_data.py

Market data analytics engine.

Calculates:
- Returns
- Volatility
- Beta
- Drawdown
- Market statistics
"""


from typing import Dict, List, Any
import math



class MarketDataAnalyzer:
    """
    Analyze equity market data.
    """



    # -----------------------------------------
    # RETURNS
    # -----------------------------------------


    def daily_returns(
        self,
        prices: List[float]
    ) -> List[float]:

        """
        Calculate daily percentage returns.
        """

        returns = []


        for i in range(1, len(prices)):

            previous = prices[i-1]
            current = prices[i]


            if previous == 0:
                returns.append(0)

            else:

                returns.append(
                    (current - previous)
                    /
                    previous
                )


        return returns



    def total_return(
        self,
        prices: List[float]
    ) -> float:

        """
        Total investment return.
        """

        if len(prices) < 2:
            return 0


        return round(

            (
                prices[-1]
                -
                prices[0]
            )
            /
            prices[0],

            4
        )



    # -----------------------------------------
    # VOLATILITY
    # -----------------------------------------


    def volatility(
        self,
        prices: List[float],
        annualize: bool = True
    ) -> float:

        """
        Historical volatility.

        Standard deviation of returns.
        """


        returns = self.daily_returns(
            prices
        )


        if len(returns) < 2:
            return 0



        mean = sum(returns) / len(returns)


        variance = sum(

            (
                r - mean
            ) ** 2

            for r in returns

        ) / (len(returns)-1)



        std = math.sqrt(
            variance
        )


        if annualize:

            std *= math.sqrt(252)


        return round(
            std,
            4
        )



    # -----------------------------------------
    # BETA
    # -----------------------------------------


    def beta(
        self,
        stock_prices: List[float],
        market_prices: List[float]
    ) -> float:

        """
        Beta relative to market index.

        Formula:

        Cov(stock,market)
        -----------------
        Var(market)

        """


        stock_returns = (
            self.daily_returns(
                stock_prices
            )
        )


        market_returns = (
            self.daily_returns(
                market_prices
            )
        )


        length = min(
            len(stock_returns),
            len(market_returns)
        )


        if length == 0:
            return 0



        stock_returns = (
            stock_returns[:length]
        )

        market_returns = (
            market_returns[:length]
        )



        stock_mean = (
            sum(stock_returns)
            /
            length
        )


        market_mean = (
            sum(market_returns)
            /
            length
        )



        covariance = sum(

            (
                stock_returns[i]
                -
                stock_mean
            )
            *
            (
                market_returns[i]
                -
                market_mean
            )

            for i in range(length)

        )



        variance = sum(

            (
                r -
                market_mean
            ) ** 2

            for r in market_returns

        )


        if variance == 0:
            return 0



        return round(

            covariance /
            variance,

            3

        )



    # -----------------------------------------
    # DRAWDOWN
    # -----------------------------------------


    def maximum_drawdown(
        self,
        prices: List[float]
    ) -> float:

        """
        Largest peak-to-trough decline.
        """


        if not prices:
            return 0


        peak = prices[0]

        max_drawdown = 0



        for price in prices:


            if price > peak:

                peak = price



            drawdown = (

                price - peak

            ) / peak



            if drawdown < max_drawdown:

                max_drawdown = drawdown



        return round(
            max_drawdown,
            4
        )



    # -----------------------------------------
    # MARKET CAPITALIZATION
    # -----------------------------------------


    def market_cap(
        self,
        price: float,
        shares_outstanding: float
    ) -> float:


        return round(

            price *
            shares_outstanding,

            2

        )



    # -----------------------------------------
    # VOLUME ANALYSIS
    # -----------------------------------------


    def average_volume(
        self,
        volumes: List[int],
        window: int = 20
    ) -> float:


        if not volumes:
            return 0


        values = volumes[-window:]


        return round(

            sum(values)
            /
            len(values),

            2
        )



    def volume_change(
        self,
        volumes: List[int]
    ) -> float:


        if len(volumes) < 2:
            return 0


        previous = volumes[-2]
        current = volumes[-1]


        if previous == 0:
            return 0


        return round(

            (
                current -
                previous
            )
            /
            previous,

            4
        )



    # -----------------------------------------
    # COMPLETE MARKET PROFILE
    # -----------------------------------------


    def analyze(
        self,
        prices: List[float],
        market_prices: List[float],
        volumes: List[int],
        shares_outstanding: float
    ) -> Dict[str, Any]:


        return {


            "performance": {


                "total_return":
                    self.total_return(
                        prices
                    )

            },


            "risk": {


                "volatility":
                    self.volatility(
                        prices
                    ),


                "beta":
                    self.beta(
                        prices,
                        market_prices
                    ),


                "maximum_drawdown":
                    self.maximum_drawdown(
                        prices
                    )

            },


            "liquidity": {


                "average_volume":
                    self.average_volume(
                        volumes
                    ),


                "volume_change":
                    self.volume_change(
                        volumes
                    )

            },


            "market_value": {


                "market_cap":
                    self.market_cap(
                        prices[-1],
                        shares_outstanding
                    )

            }

        }