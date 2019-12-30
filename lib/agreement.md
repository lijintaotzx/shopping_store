# 交易通信协议

## 用户端
    * 请求结算 REQUEST {user_id}
    * 发送购物车信息 SHOPPING_CARDS {class: shopping_cards}
    * 发送结算金额信息 PAYING {class: shopping_cards} {pay_money}

## 结算端
    STATUS_CODE MSG
    200 请求成功
    400 失败原因

    STATUS_CODE:
    * 200 成功（允许）
    * 400 失败（拒绝）

    接收到的请求类型后的操作：
    * REQUEST :不操作
    * SHOPPING_CARDS :检查购物车内商品的个数，是否大于库存，大于的话返回400失败
    * PAYING :再次核对金额，以及用户支付的金额是否相等，计算找零等信息返回
