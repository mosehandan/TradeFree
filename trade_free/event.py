from utils.constant_util import SELL
from utils.id_util import EventId


class Event:
    """
    Event类的基类
    """
    pass


class MarketEvent(Event):
    """
    将新的市场数据注册为Event, 由Strategy对象处理
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        Parameters:
        symbol - The ticker symbol, e.g. '000001'.
        """
        self.event_id = EventId.get_next_id()  # 自增序列, 由一个事件引发的其余事件使用一个id, 用于追踪.
        self.type = 'MARKET'


class SignalEvent(Event):
    """
    将Strategy类产生的Single注册为Event, 由Portfolio对象处理
    """

    def __init__(self, event_id, symbol, direction, order_type, quantity, price, single_date):
        """
        Initialises the SignalEvent.

        Parameters:
        event_id - 自增序列, 由一个事件引发的其余事件使用一个id, 用于追踪
        symbol - The ticker symbol, e.g. '000001'.
        direction - 'B' or 'S'. 买和卖
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - 交易数量
        price - 交易价格
        single_date - 生成SignalEvent使用的数据的时间
        """
        self.event_id = event_id
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.direction = direction
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.single_date = single_date


class OrderEvent(Event):
    """
    将Portfolio产生的Single注册为Event, 由 执行系统(execution system) 处理
    The order contains a symbol (e.g. GOOG), a type (market or limit), quantity and a direction.
    """

    def __init__(self, event_id, symbol, order_type, quantity, price, direction, order_date):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        Parameters:
        event_id - 自增序列, 由一个事件引发的其余事件使用一个id, 用于追踪
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        order_date - 生成OrderEvent使用的数据的时间
        """
        self.event_id = event_id
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.direction = direction
        self.order_date = order_date

    def print_order(self):
        """
        打印到屏幕或日志
        """
        print("Order: Symbol={0}, Type={1}, Quantity={2}, Direction={3}, event_id={4}".format(self.symbol, self.order_type, self.quantity, self.direction, self.event_id))


class FillEvent(Event):
    """
    计算下单需要的数据, 包括 数量, 价格, 交易费用等
    将 订单 产生的Single注册为Event, 由 下单系统 处理
    """

    def __init__(self, event_id, symbol, exchange, quantity,
                 direction, order_type, price, commission=None):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        event_id - 自增序列, 由一个事件引发的其余事件使用一个id, 用于追踪
        timeindex - The bar-resolution when the order was filled.  下单时间
        symbol - The instrument which was filled.  证券代码
        exchange - The exchange where the order was filled.  交易所
        quantity - The filled quantity.  数量
        direction - The direction of fill ('BUY' or 'SELL') 买卖方向
        price - 交易价格
        commission - An optional commission sent from IB.  手续费
        """
        self.event_id = event_id
        self.type = 'FILL'
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.price = price
        self.order_type = order_type

        # Calculate commission
        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission

    def calculate_ib_commission(self):
        """
        当未传入手续费时, 自动计算出一个手续费, 根据各个交易所情况不同, 有不同的默认值
        招商证券:
            手续费: 0.06%, 最低5块
            印花税: 0.1%
        """
        min_service_change = 5
        service_change_percent = 0.0006
        stamp_tax_percent = 0.001

        service_change = max(min_service_change, service_change_percent * (self.price * self.quantity))
        stamp_tax = stamp_tax_percent * (self.price * self.quantity) if self.direction == SELL else 0
        full_cost = service_change + stamp_tax

        return full_cost
