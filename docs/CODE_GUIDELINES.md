# Code Guidelines

## Not Recommended Practices

Avoid using inefficient or unclear methods in your code. For example, instead of:

```python
returns = []
for i in range(1, len(df)):
    returns.append((df['close'][i] - df['close'][i-1]) / df['close'][i-1])
```

consider using vectorized operations provided by libraries like pandas or NumPy for better clarity and performance.

## API Calls

- Implement rate limiting for API requests.
- Utilize connection pooling where possible.
- Add retry mechanisms for transient failures.

Example using the tenacity library:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_data():
    pass
```

## Version Control

### Git Guidelines
- Develop using feature branches.
- Format your commit messages clearly and consistently.
- Regularly merge changes from the main branch to keep your branch updated.

### Commit Message Template

```
<type>(<scope>): <subject>

<body>

<footer>
```

You can now replace the contents of your `docs/CODE_GUIDELINES.md` file with the text above to ensure all guidelines are seen in English. Let me know if there is anything else you need!

## 📝 基本原则

### 1. 代码风格
- 严格遵循 PEP 8 规范
- 使用 4 空格缩进
- 行长度限制在 79 字符以内
- 使用有意义的变量和函数名
- 类名使用 CapWords 命名法
- 函数和变量名使用小写字母加下划线

### 2. 文档规范
```python
def process_market_data(raw_data: pd.DataFrame, 
                       indicators: List[str]) -> pd.DataFrame:
    """处理市场数据并添加技术指标
    
    Args:
        raw_data (pd.DataFrame): 原始市场数据
        indicators (List[str]): 需要添加的技术指标列表
        
    Returns:
        pd.DataFrame: 处理后的数据框
        
    Raises:
        ValueError: 当输入数据格式不正确时
        
    Example:
        >>> df = process_market_data(data, ['RSI', 'MACD'])
    """
    pass
```

### 3. 类型注解
- 使用 Python 类型提示
- 复杂类型使用 typing 模块
- 返回类型明确标注

```python
from typing import Dict, List, Optional, Union

def analyze_trend(
    price_data: pd.DataFrame,
    timeframe: str,
    indicators: Optional[List[str]] = None
) -> Dict[str, Union[str, float]]:
    pass
```

## 🏗 项目结构

### 1. 目录组织
```
src/
├── collectors/
│   ├── __init__.py
│   ├── binance_collector.py
│   └── base_collector.py
├── processors/
│   ├── __init__.py
│   ├── feature_engineer.py
│   └── data_cleaner.py
├── analysis/
│   ├── __init__.py
│   ├── llm_analyzer.py
│   └── risk_manager.py
└── interface/
    ├── __init__.py
    ├── cli.py
    └── web_app.py
```

### 2. 模块职责
- collectors: 负责数据采集
- processors: 数据处理和特征工程
- analysis: 市场分析和风险管理
- interface: 用户界面实现

## 🔧 开发实践

### 1. 错误处理
```python
class DataCollectionError(Exception):
    """数据采集相关错误的基类"""
    pass

def fetch_market_data():
    try:
        response = api.get_klines()
    except RequestException as e:
        raise DataCollectionError(f"API请求失败: {str(e)}")
    except ValueError as e:
        raise DataCollectionError(f"数据格式错误: {str(e)}")
```

### 2. 日志记录
```python
import logging

logger = logging.getLogger(__name__)

def process_data():
    logger.info("开始处理数据")
    try:
        # 处理逻辑
        logger.debug("数据处理细节...")
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        raise
```

### 3. 测试规范
```python
import pytest

def test_feature_engineering():
    """测试特征工程模块"""
    # 准备测试数据
    test_data = prepare_test_data()
    
    # 执行测试
    result = process_features(test_data)
    
    # 验证结果
    assert 'RSI' in result.columns
    assert not result['MACD'].isnull().any()
```

## 🔒 安全规范

### 1. 配置管理
- 使用环境变量存储敏感信息
- 不在代码中硬编码密钥
- 使用配置文件管理非敏感设置

```python
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
```

### 2. 数据验证
```python
from pydantic import BaseModel, validator

class MarketData(BaseModel):
    symbol: str
    price: float
    volume: float
    
    @validator('price', 'volume')
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('必须为正数')
        return v
```

## 📊 性能优化

### 1. 数据处理
- 使用 vectorized 操作代替循环
- 适当使用多进程处理
- 实现数据缓存机制

```python
# 推荐
df['returns'] = df['close'].pct_change()

# 不推荐
returns = []
for i in range(1, len(df)):
    returns.append((df['close'][i] - df['close'][i-1]) / df['close'][i-1])
```

### 2. API 调用
- 实现请求限流
- 使用连接池
- 添加重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_data():
    pass
```

## 🔄 版本控制

### 1. Git 规范
- 使用功能分支开发
- 提交信息格式化
- 定期合并主分支

### 2. 提交信息模板
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- feat: New feature
- fix: Bug fix
- docs: Documentation updates
- style: Code style changes (formatting, missing semi-colons, etc.)
- refactor: Code refactoring without functional changes
- test: Adding or updating tests
- chore: Auxiliary tasks (build, tooling, etc.)

## 📝 代码审查清单

### 1. 功能性
- [ ] Check if the feature implementation is complete.
- [ ] Ensure proper handling of edge cases.
- [ ] Verify robust error handling.

### 2. 可维护性
- [ ] Code structure is clear and modular.
- [ ] Naming conventions are followed.
- [ ] Sufficient comments and documentation are provided.

### 3. 性能
- [ ] Evaluate algorithm complexity.
- [ ] Check resource usage and potential bottlenecks.
- [ ] Ensure proper use of concurrency (if applicable).

### 4. 测试
- [ ] Unit tests cover key components.
- [ ] Integration tests verify the complete workflow.
- [ ] Edge cases and boundary conditions are thoroughly tested.

# Project Process

## Overview
This document outlines the processes for setting up, developing, testing, reviewing, and deploying the project. It is intended to guide all team members and contributors.

## Environment Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/crypto-trading-analysis.git
   cd crypto-trading-analysis
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   - For production: 
     ```bash
     pip install .
     ```
   - For development:
     ```bash
     pip install ".[dev]"
     ```

## Development Process
- **Coding Standards**: Follow the guidelines outlined in `CODE_GUIDELINES.md`.
- **Branching Strategy**: 
  - Create a new branch for each new feature or bug fix.
  - Name your branch descriptively (e.g., `feature/llm-enhancements`).
- **Commit Often**: 
  - Commit small chunks of work with clear descriptive messages.
  - Ensure each commit compiles and passes tests.
  
## Testing
- Write tests for every new feature and bug fix.
- Run tests locally using:
  ```bash
  pytest
  ```
- Ensure test coverage remains high and document any areas that lack tests.

## Code Review and Merging
- Open a pull request (PR) for your changes.
- Request reviews from at least one other team member.
- Address all review comments before merging.
- Merge into the main branch only after successful reviews and passing tests.

## Deployment Process
- **Installation**: Use the `setup.py` configuration for installation.
- **Environment Variables**: Configure via the `.env` file (copy from `.env.example`).
- **Running the Application**: Launch using the CLI:
  ```bash
  crypto-analysis -s BTCUSDT -i 1h -l 7d
  ```
- **Monitoring**: Review log files (located in the `logs/` directory) for any errors or important messages.

## Maintenance and Updates
- Update the documentation, tests, and code as features evolve.
- Periodically review dependencies and code quality.
- Refactor and cleanup obsolete code on a regular basis.

## Communication and Documentation
- Use issue trackers for reporting bugs and suggesting enhancements.
- Document important decisions in project meeting notes.
- Maintain updated API documentation and user guides for the project.

## Continuous Integration & Deployment (CI/CD)
- Set up automated testing and linting on every commit.
- Use CI/CD pipelines to automatically deploy changes to staging environments.
- Ensure that any production deployment is preceded by successful build and test phases. 