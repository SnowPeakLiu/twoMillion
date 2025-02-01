class RiskManager:
    def __init__(self, max_risk_per_trade=0.01):
        self.max_risk_per_trade = max_risk_per_trade  # 单笔交易最大风险比例
        
    def validate_suggestion(self, analysis):
        """验证交易建议的合理性"""
        if analysis.get('RSI', 50) > 70:
            analysis['trading_suggestion'] = "超买区域，建议观望"
        elif analysis.get('RSI', 50) < 30:
            analysis['trading_suggestion'] = "超卖区域，关注反弹机会"
        return analysis 