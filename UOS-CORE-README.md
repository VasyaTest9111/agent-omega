# 🚀 UOS-Core: Universal Operating System Core

**Universal Operating System Core (UOS-Core)** — професійна, модульна система автоматизації на основі **Infrastructure as Code** принципів.

---

## 📋 Структура проекту

```
agent-omega/
├── initialize_project.py      # Ініціалізація конфігурації системи
├── task_orchestrator.py        # Оркестратор для управління завданнями
├── SYSTEM_CONFIG.py            # (Генерується) Конфігураційний файл
├── Makefile                    # Команди для розробки та розгортання
├── CI-PIPELINE.yml             # CI/CD конфігурація (потребує переміщення)
└── UOS-CORE-README.md          # Цей файл
```

---

## 🎯 Основні компоненти

### 1. **initialize_project.py** 🔧
Ініціалізує конфігураційний файл системи з відміткою часу та статусом.

**Особливості:**
- ✅ Автоматичне логування всіх операцій
- ✅ Обробка помилок (IOError, Exception)
- ✅ UTF-8 кодування файлів
- ✅ Безпечна робота з файловою системою

```bash
# Запуск
python initialize_project.py

# Результат
2026-07-19 10:30:45,123 - INFO - ✓ System configuration initialized: ./SYSTEM_CONFIG.py
```

---

### 2. **task_orchestrator.py** 🎭
Управляє виконанням завдань у системі автоматизації.

**Особливості:**
- ✅ Перевірка стану системи (ACTIVE)
- ✅ Логування виконання завдань з часовими мітками
- ✅ Отримання детальної системної інформації
- ✅ Обробка помилок на рівні завдань

```bash
# Запуск
python task_orchestrator.py

# Результат
✓ TaskOrchestrator initialized | System status: ACTIVE | Mode: AUTONOMOUS
✓ Executing task: 'data_validation' | Mode: AUTONOMOUS | ...
```

---

### 3. **Makefile** 📦
Зручні команди для управління системою.

**Доступні команди:**

| Команда | Опис |
|---------|------|
| `make help` | Показати довідку |
| `make init` | Ініціалізувати конфігурацію системи |
| `make run` | Запустити оркестратор (включає init) |
| `make lint` | Перевірити код (pylint, flake8) |
| `make test` | Запустити тести |
| `make clean` | Очистити згенеровані файли |

---

### 4. **CI/CD Pipeline** (CI-PIPELINE.yml) ⚙️
Автоматизована перевірка при кожному push.

**Включає:**
- 🔍 **Syntax Validation** — перевірка синтаксису Python
- 🔍 **Linting** — pylint, flake8, black, isort
- 🔐 **Security Checks** — bandit, safety
- 🧪 **Integration Tests** — запуск системи та перевірка роботи
- 📊 **Build Summary** — звіт про статус

---

## 🚀 Швидкий старт

### Крок 1️⃣: Перемістіть CI-PIPELINE.yml
```bash
mkdir -p .github/workflows
mv CI-PIPELINE.yml .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "chore: Move CI-PIPELINE to .github/workflows"
git push origin main
```

### Крок 2️⃣: Ініціалізація системи
```bash
make init
```

**Результат:**
```
🔧 Initializing UOS-Core system configuration...
2026-07-19 10:30:45,123 - INFO - ✓ System configuration initialized: ./SYSTEM_CONFIG.py
✓ Initialization completed
```

### Крок 3️⃣: Запуск оркестратора
```bash
make run
```

**Результат:**
```
🔧 Initializing UOS-Core system configuration...
✓ Initialization completed
🚀 Starting task orchestrator...
2026-07-19 10:30:46,456 - INFO - ✓ TaskOrchestrator initialized | System status: ACTIVE | Mode: AUTONOMOUS
2026-07-19 10:30:46,789 - INFO - System Information: {...}
✓ Executing task: 'data_validation' | Mode: AUTONOMOUS | Registry: CORE_INTEGRATION | ...
✓ Task 'data_validation': SUCCESS
✓ Task 'process_configuration': SUCCESS
✓ Task 'deploy_infrastructure': SUCCESS
✓ Orchestrator execution completed
```

### Крок 4️⃣: Перевірка коду
```bash
make lint
```

---

## 📊 Архітектура системи

```
┌─────────────────────────────────────────────────────────────┐
│                      UOS-Core System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │ initialize_project   │      │  task_orchestrator   │    │
│  │ .py                  │─────→│  .py                 │    │
│  └──────────────────────┘      └──────────────────────┘    │
│           │                              │                   │
│           ├─→ SYSTEM_CONFIG.py           │                  │
│           │   (Generated)                │                  │
│           │                              ▼                  │
│           │                    ┌──────────────────────┐    │
│           │                    │  SystemState         │    │
│           │                    │  • state: ACTIVE     │    │
│           │                    │  • mode: AUTONOMOUS  │    │
│           │                    │  • registry: CORE    │    │
│           │                    └──────────────────────┘    │
│           │                              │                   │
│           └──────────────────────────────┤                   │
│                                          ▼                   │
│                            ┌──────────────────────┐         │
│                            │  Task Executor       │         │
│                            │  • execute_task()    │         │
│                            │  • get_system_info() │         │
│                            └──────────────────────┘         │
│                                          │                   │
│                                          ▼                   │
│                            ┌──────────────────────┐         │
│                            │  Logging System      │         │
│                            │  • INFO / ERROR      │         │
│                            │  • Timestamps        │         │
│                            └──────────────────────┘         │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  CI/CD Pipeline (.github/workflows/ci.yml)                  │
│  ✓ Syntax ✓ Linting ✓ Security ✓ Integration Tests         │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Приклад: Користувацьке завдання

```python
from task_orchestrator import TaskOrchestrator

# Ініціалізувати оркестратор
orchestrator = TaskOrchestrator()

# Виконати завдання
success = orchestrator.execute_task("backup_database")

# Отримати інформацію про систему
info = orchestrator.get_system_info()
print(f"System Status: {info['status']}")
print(f"Mode: {info['operational_mode']}")
print(f"Registry: {info['registry']}")
```

---

## 🔐 Безпека

- ✅ **Syntax Validation** — перевірка коректності всіх Python файлів
- ✅ **Code Linting** — pylint, flake8 (якість та стандарти)
- ✅ **Formatting** — black, isort (єдиний стиль коду)
- ✅ **Security Checks** — bandit (вразливості), safety (залежності)
- ✅ **Logging Audit** — всі операції записуються з часовою міткою

---

## 📦 Залежності

**Мінімальні:**
```
Python 3.9+
```

**Опціональні (для розробки):**
```bash
pip install pylint flake8 black isort bandit safety pytest
```

---

## 🔄 Робочий цикл

```
┌──────────────┐
│ Code Changes │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Git Push        │
└──────┬───────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ CI Pipeline Triggered (.github/workflows)   │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Jobs:                                       │
│ • Syntax Validation ✓                       │
│ • Linting & Code Quality ✓                  │
│ • Security Checks ✓                         │
│ • Integration Tests ✓                       │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ Build Summary & Status                      │
│ ✅ All checks passed / ❌ Failures found    │
└──────────────────────────────────────────────┘
```

---

## 🧪 Тестування локально

```bash
# Перевірити синтаксис
python -m py_compile initialize_project.py
python -m py_compile task_orchestrator.py

# Запустити pylint
pylint initialize_project.py task_orchestrator.py

# Запустити flake8
flake8 initialize_project.py task_orchestrator.py

# Запустити bandit (безпека)
bandit initialize_project.py task_orchestrator.py
```

---

## 📖 Документація

### Логування
```python
import logging

logger = logging.getLogger(__name__)
logger.info("✓ Operation successful")
logger.error("✗ Operation failed")
logger.warning("⚠ Warning message")
```

### Формат логів
```
2026-07-19 10:30:45,123 - INFO - ✓ System configuration initialized
2026-07-19 10:30:46,456 - ERROR - ✗ Failed to initialize TaskOrchestrator
```

---

## 🤝 Контрибьютинг

Усі зміни автоматично перевіряються **CI/CD пайплайном**. Переконайтесь, що:

1. ✅ Код має коректний синтаксис
2. ✅ Лінтер не знаходить помилок
3. ✅ Тести проходять успішно
4. ✅ Нема вразливостей безпеки

---

## 📄 Ліцензія

MIT License

---

## 📞 Контакти

**UOS-Core** — професійна система автоматизації на основі Infrastructure as Code.

---

## 🏆 Статус проекту

| Компонент | Статус | Дата |
|-----------|--------|------|
| initialize_project.py | ✅ Готово | 2026-07-19 |
| task_orchestrator.py | ✅ Готово | 2026-07-19 |
| Makefile | ✅ Готово | 2026-07-19 |
| CI-PIPELINE.yml | ✅ Готово | 2026-07-19 |
| Документація | ✅ Готово | 2026-07-19 |

---

**Версія:** 1.0.0  
**Останнє оновлення:** 2026-07-19  
**Статус:** 🟢 Production Ready
